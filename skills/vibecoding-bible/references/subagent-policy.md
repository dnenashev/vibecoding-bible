# Политика сабагентов

## Содержание

1. Цель
2. Decision rule
3. Verdicts
4. Когда делегировать
5. Когда оставить локально
6. Context Capsule
7. SubagentTaskContract
8. Параллельная работа
9. Обязанности оркестратора
10. Failure modes
11. Self-check

## 1. Цель

Использовать сабагента как механизм сохранения контекста оркестратора, а не как ритуал декомпозиции.

Главный сценарий:

> Исходная сессия накопила важные решения и ограничения. Один bounded subtask требует длинного чтения/выполнения и, вероятно, нескольких compaction. Если оркестратор выполнит его сам, он рискует потерять исходный контекст. Сабагент получает минимальный task-local capsule, выполняет работу, а оркестратор сохраняет центральную модель и интегрирует результат.

Сабагент не является способом снять ответственность. Оркестратор отвечает за product intent, approvals, conflicts, integration и final evidence.

## 2. Decision rule

Делегировать, когда одновременно выполняется большинство условий:

```text
context_preservation_value
  + task_duration
  + task_locality
  + independent_verifiability
  > coordination_cost
  + integration_risk
  + context_transfer_risk
```

Особенно сильный сигнал: задача требует загрузить большой собственный corpus/logs/repository region, а оркестратору важно не вытеснить решения исходного диалога.

## 3. Verdicts

| Verdict | Meaning |
|---|---|
| `KEEP_LOCAL` | Выполнить оркестратором |
| `DELEGATE` | Передать один bounded autonomous subtask |
| `PARALLELIZE` | Передать несколько независимых subtasks с разными write scopes |
| `DECOMPOSE_FIRST` | Задача слишком широкая/связанная; сначала выделить contracts |
| `BLOCKED` | Нельзя безопасно продолжить без authority/input/external state |

До начала длинной реализации записать verdict и одну фразу причины.

## 4. Когда делегировать

- глубокий анализ большого, локализованного модуля;
- долгая test/build/debug loop с ясным success criterion;
- исследование независимой integration/API;
- создание bounded artifact по frozen input contract;
- миграция внутри чётко выделенного write scope;
- независимый forward-test/eval без утечки ожидаемого ответа;
- параллельные компоненты, которые не меняют общую schema/decision одновременно;
- задача, которая почти наверняка вызовет несколько context compactions у оркестратора.

## 5. Когда оставить локально

- задача короткая или требует непрерывного текущего reasoning;
- central architecture/product/security decision;
- scope ещё не определён;
- пользователь активно уточняет требования;
- subtask тесно переплетён с несколькими модулями и write scopes;
- результат нельзя независимо проверить;
- цена передачи контекста выше ожидаемой экономии;
- действие требует нового authority/approval;
- оркестратор всё равно должен перечитать весь corpus для интеграции.

Не делегировать только ради параллелизма. Не передавать сабагенту неразрешённую внешнюю мутацию.

## 6. Context Capsule

Перед делегированием сохранить компактный capsule исходной сессии:

```markdown
## Objective
Конкретный outcome исходной задачи.

## Frozen decisions
Уже принятые решения, которые нельзя пересматривать без escalation.

## Facts
Подтверждённые repository/user facts.

## Assumptions / unknowns
Что можно проверить; что запрещено выдавать за fact.

## Invariants / red lines
Что нельзя сломать или обходить.

## Current state
Commit/worktree/config/test status и релевантные refs.

## Integration contract
Какой output ожидает оркестратор и как он будет проверен.
```

Capsule не должен содержать весь чат. Передавать только task-local knowledge. Secrets не копировать; ссылаться на разрешённую configuration boundary.

## 7. SubagentTaskContract

Каждый делегированный task содержит:

```yaml
id: stable-task-id
objective: one observable outcome
allowed_scope:
  read: [exact paths/resources]
  write: [exact non-overlapping paths]
non_goals: []
frozen_decisions: []
invariants: []
facts: []
assumptions: []
unknowns: []
required_skill_or_docs: []
first_test_or_probe: command/procedure
acceptance_criteria: []
required_evidence: []
report_format:
  - outcome
  - files_changed
  - tests_run
  - evidence
  - assumptions_remaining
  - risks
  - recommended_next_action
escalate_when: []
```

Task должен быть bounded и завершаться проверяемым output. «Разберись со всем проектом» — не контракт.

## 8. Параллельная работа

`PARALLELIZE` разрешён, если:

- subtasks независимы;
- write scopes не пересекаются;
- shared schemas/frozen decisions уже определены;
- один integration owner;
- merge order и общие gates известны;
- agents не запускают конкурирующие migrations или destructive actions.

Если два агента должны менять один contract/schema, выбрать одного owner либо сначала создать frozen interface.

## 9. Обязанности оркестратора

До делегирования:

1. Сохранить Context Capsule.
2. Зафиксировать TaskContract и write scope.
3. Убедиться, что задача укладывается в authority пользователя.
4. Назвать required evidence и escalation conditions.

После делегирования:

1. Не принимать summary как proof — проверить diff/artifacts/tests.
2. Сверить output с frozen decisions и parent ProjectContract.
3. Разрешить conflicts и stale assumptions.
4. Запустить shared integration/release gates самостоятельно.
5. Обновить central decision/context record.
6. Сообщить пользователю итог, ограничения и следующий шаг.

Merge или сообщение «готово» не равны завершению.

## 10. Failure modes

| Failure | Guardrail |
|---|---|
| Сабагенту передан весь чат | Минимальный Context Capsule |
| Потерян product intent | Frozen decisions остаются у оркестратора |
| Два агента перезаписывают files | Non-overlapping write scopes |
| Агент сделал незапрошенный redesign | Explicit non-goals и allowed scope |
| Summary скрывает failing tests | Required raw evidence и orchestrator rerun |
| Long task всё равно разрастается | `DECOMPOSE_FIRST` и smaller contracts |
| Сабагент принял central decision | Escalate condition + orchestrator ownership |
| Parallel work создаёт schema conflicts | Freeze interface до parallelization |
| Test agent знает ожидаемый ответ | Forward-test с raw artifact и generic prompt |
| Делегирование дороже работы | `KEEP_LOCAL` по умолчанию для коротких tasks |

## 11. Self-check

1. Делегирование действительно сохраняет ценный session context?
2. Subtask bounded и автономен?
3. Output независимо проверяем?
4. Context Capsule минимален, но достаточен?
5. Frozen decisions и red lines явны?
6. Write scope точен и не пересекается?
7. Пользователь разрешил требуемые действия?
8. Оркестратор сохранил integration ownership?
9. Есть escalation conditions?
10. После возврата будут запущены shared gates?

