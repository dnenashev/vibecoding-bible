# Практический workflow реализации

## 1. Назначение

Использовать этот модуль на фазе `BUILD` для нового проекта, feature, bug fix, integration, migration или refactor с изменением поведения.

Цель — выполнить минимальное production-ready изменение и оставить репозиторий в понятном, проверяемом состоянии. Не измерять прогресс количеством созданных файлов или написанного кода.

Работать коротким циклом:

```text
reality → contract → Red → minimal Green → refactor → evidence → next slice
```

Глубокие правила тестирования, AI governance, security и release применять через соответствующие references. Здесь определить повседневный способ изменения кода.

## 2. Выбрать режим и границу изменения

Выбрать delivery mode и risk отдельно:

- mode `EXPLORE` — time-boxed spike, изолированный от production path;
- mode `BUILD` — production-ready slice по умолчанию;
- risk `LOW | STANDARD | CRITICAL` — определяет силу approvals, evidence и изоляции.

До изменения сформулировать:

- observable outcome;
- included scope;
- excluded scope;
- invariants;
- первый Red;
- требуемый evidence level;
- rollback или безопасный exit.

Использовать `VibecodingProjectContract` full/delta по риску. Для локального изменения достаточно короткого delta; не заполнять большой документ ради ритуала.

Если граница задачи не помещается в одно проверяемое утверждение, разделить её до начала кода.

## 3. Ориентироваться в репозитории

Сначала получить карту, затем читать детали.

1. Найти project instructions: `AGENTS.md`, `CONTRIBUTING`, package-level rules.
2. Посмотреть `git status` и текущую branch/commit.
3. Найти entrypoints, manifests, workspaces и build/test commands.
4. Найти код, tests, schemas и config, связанные с requested behavior.
5. Проследить один реальный call/data path от входа до результата.
6. Найти существующий похожий pattern до создания нового abstraction.
7. Проверить runtime и installed dependency versions.

Использовать `rg --files` и `rg` для поиска. Не читать весь репозиторий последовательно.

Составить короткую карту:

```text
Entry → validation → domain decision → state/integration → output
Tests → какой уровень и какой behavior доказывают
Config → где задаётся runtime behavior
```

README считать подсказкой, а не доказательством actual behavior.

### Незнакомый и legacy код

Большая часть работы идёт в чужом существующем коде. Здесь порядок другой: сначала
зафиксировать фактическое поведение, потом менять.

1. Найти способ запустить систему и увидеть её поведение своими глазами; без этого любая
   гипотеза о причине остаётся предположением.
2. Характеризовать текущее поведение тестом до изменения. Characterization test фиксирует
   то, что система делает сейчас, включая странности. Он не утверждает, что это правильно.
3. Отделить намеренное поведение от случайного, спросив пользователя, а не решая за него:
   на legacy-коде «баг» и «контракт, на который кто-то опирается» выглядят одинаково.
4. Сузить границу изменения до того места, где поведение можно проверить. Не переписывать
   модуль ради удобства чтения.
5. Для замены большого куска использовать strangler-подход: новая реализация рядом,
   переключение по одному пути, старый код удаляется после подтверждения.

Если тестов нет вообще, первым Red становится characterization test на затронутый путь.
Не начинать с добавления общей test suite ко всему проекту: это отдельная работа с
отдельным решением.

Отсутствие понимания всей системы не является блокером. Блокером является отсутствие
проверяемой границы: непонятно, что сломается, и нет способа это увидеть. В этом случае
сначала строить наблюдаемость, а не патч.

Не приписывать legacy-решениям глупость. Считать, что у странного кода была причина,
и искать её в истории, тестах и данных до того, как удалять.

## 4. Прочитать project instructions

Применять инструкции по области действия:

1. Найти root instructions.
2. Найти вложенные instructions для изменяемого пути.
3. Разрешить конфликт в пользу более специфичного файла, если higher-level rule не говорит иначе.
4. Зафиксировать команды, formatting, test и architecture constraints.
5. Не переносить правила одного package на весь monorepo автоматически.

Если инструкция требует недоступный tool или противоречит пользовательской цели, остановиться и сообщить точный conflict. Не обходить правило молча.

Не менять project instructions как способ упростить текущую реализацию без отдельного обоснования.

## 5. Сформировать Context Capsule

Перед длинной работой сохранить только решения, которые нельзя потерять:

```markdown
## Objective
Какой observable outcome получить.

## Frozen decisions
Что уже утверждено и не пересматривается молча.

## Facts
Что подтверждено repository/runtime evidence.

## Assumptions / unknowns
Что требует проверки.

## Scope / invariants
Что менять и что не ломать.

## Current state
Commit, dirty files, commands и blockers.

## Evidence
Какие проверки должны пройти.
```

Не копировать весь чат или большие source fragments. Обновлять capsule только при изменении решения или факта.

Для небольшого change хранить capsule в рабочем reasoning, а не создавать файл. Создавать artifact, если работа длинная, передаётся между agents или должна пережить сессию.

## 6. Разбить задачу на slices

Каждый slice должен:

- менять одно наблюдаемое поведение;
- иметь один основной owner и небольшой write scope;
- начинаться с проверяемого Red;
- завершаться Green и relevant regression;
- оставлять систему runnable;
- не зависеть от fabricated data или незавершённого production branch.

Предпочитать vertical slice:

```text
input → domain behavior → real boundary → observable output
```

Не разбивать работу только по слоям `сначала все types → потом все services → потом UI`, если ни один промежуточный этап нельзя проверить как behavior.

Сначала выполнять slice с максимальным uncertainty/risk, если его можно проверить дёшево. Не начинать с косметики, когда неизвестна доступность обязательной integration.

## 7. Выполнить implementation loop

Для каждого slice:

1. Подтвердить expected behavior и первый Red.
2. Запустить test/probe и проверить правильную причину failure.
3. Изменить минимальный production path.
4. Запустить узкий test до Green.
5. Упростить naming, boundaries и duplication без расширения behavior.
6. Запустить соседние regressions.
7. Проверить integration/build/type/lint только на применимом уровне.
8. Просмотреть diff на scope creep, secrets, placeholders и debug output.
9. Обновить contract/decision/docs при изменении интерфейса или решения.
10. Зафиксировать evidence и перейти к следующему slice.

Не накапливать много неподтверждённых изменений перед первым запуском. Короткая feedback loop важнее красивого большого patch.

Не исправлять unrelated defects без включения в scope. Зафиксировать их отдельно, если они не блокируют текущую задачу.

## 8. Применить TDD без ритуала

Следовать Red → Green → Refactor из `core-principles.md`.

Выбирать test на ближайшей границе, способной доказать поведение:

- pure domain behavior — unit;
- component interaction — component;
- boundary/schema — contract;
- database/provider — integration;
- user critical path — E2E.

Не заменять behavior test проверкой source string или snapshot, если пользовательский результат требует runtime. Не писать unit test на framework internals.

Для bug fix сначала воспроизвести дефект. Red должен падать до исправления по причине дефекта и проходить после него.

Если bug требуется довести через isolated repair, integration, human QA или controlled release, полностью прочитать [`bug-repair.md`](bug-repair.md). Не считать QA раннего Dev-preview доказательством exact release candidate.

Test double разрешать только на внешней границе в test-only composition. Не использовать double как доказательство обязательной live integration.

Если deterministic automated test технически невозможен, зафиксировать повторяемый probe и требуемый более сильный evidence; не объявлять TDD выполненным формально.

## 9. Диагностировать системно

Не начинать со случайного patch. Использовать цикл:

```text
symptom → minimal reproduction → facts → boundary localization
→ falsifiable hypothesis → one probe → root cause → regression Red → fix
```

### Сначала воспроизвести

- зафиксировать exact input, environment, version и observed output;
- уменьшить сценарий без удаления причины;
- определить expected behavior и источник expectation;
- проверить, воспроизводится ли проблема стабильно.

### Затем локализовать

- найти последний корректный state и первый некорректный;
- проверить boundary inputs/outputs;
- сравнить failing и passing case;
- проверить recent diff, config и dependency changes;
- изменить одну переменную за probe.

### После этого исправить

- исправлять root cause, а не скрывать symptom;
- добавлять regression test до production fix;
- не расширять exception handling до catch-all;
- не превращать failure в пустой или fabricated success;
- проверять соседние paths и failure behavior.

Если гипотеза опровергнута, обновить facts и выбрать следующую. Не накапливать несколько speculative fixes одновременно.

## 10. Управлять dependencies и generated code

Добавлять dependency, только если она:

- решает конкретную задачу лучше небольшого local code;
- совместима с runtime/license/security constraints;
- поддерживается и имеет приемлемый upgrade path;
- не дублирует уже установленную capability;
- оправдывает bundle/runtime/operational cost.

Проверять exact installed version и официальную документацию. Не писать API по памяти для быстро меняющегося package.

Не обновлять unrelated dependencies вместе с feature. Lockfile change должен соответствовать manifest change и быть просмотрен.

Generated code:

- изменять через canonical generator, если project так устроен;
- изменять source schema/template, а не generated output вручную;
- запускать generator детерминированно;
- проверять diff и committed artifact policy;
- не скрывать ручной patch в generated file.

Если generator недоступен, считать это blocker или явно ограниченным constraint, а не переписывать большой output вручную.

## 11. Сохранить dirty worktree

Считать существующие изменения пользовательскими, пока не доказано обратное.

Перед patch:

1. Посмотреть status и diff только для затрагиваемых файлов.
2. Определить, пересекается ли requested change с текущими edits.
3. Не форматировать и не переписывать unrelated regions.
4. Не использовать destructive reset/checkout.
5. При неизбежном конфликте остановиться и запросить решение.

После patch проверить, какие строки принадлежат текущей задаче. Не включать чужие изменения в commit без явного scope.

Не запускать bulk formatter на всём repository, если задача меняет несколько файлов и project не требует этого.

## 12. Соблюдать change и git hygiene

Поддерживать change понятным:

- один commit — одна связная причина изменения;
- сообщение commit объясняет intent, а не перечисляет файлы;
- diff не содержит secrets, local config, temporary logs и debug flags;
- rename отделён от behavior change, если иначе review становится непрозрачным;
- public interface, migration и consumer changes синхронизированы;
- required tests не отключены и assertions не ослаблены.

Перед commit просмотреть `git diff --check`, targeted diff и status. Запустить project-required checks.

Не делать commit, push, PR или release, если пользователь запросил только анализ. При запросе реализации commit/push выполнять только в пределах предоставленной authority и установленного workflow.

Не переписывать опубликованную историю без явного запроса.

### Granularity изменения и PR

Изменение готовят так, чтобы его мог проверить человек. Один PR — одно решение и его
следствия. Не смешивать поведенческое изменение с массовым переименованием,
переформатированием или обновлением зависимостей: смешанный diff нельзя отревьюить,
его можно только принять на веру.

Если работа не помещается в проверяемый объём, разделить на последовательность, где
каждый шаг самостоятельно корректен и обратим. Описание изменения должно называть
причину и границу, а не пересказывать diff.

## 13. Решить, нужен ли сабагент

По умолчанию оставить задачу локально, если она короткая и требует непрерывного reasoning.

Делегировать bounded subtask, если он:

- загрузит большой отдельный corpus;
- вероятно вызовет несколько compaction;
- имеет независимый write scope;
- проверяется отдельным artifact/test;
- позволяет оркестратору сохранить product intent и decisions.

Перед делегированием создать короткий `SubagentTaskContract`: exact objective, allowed read/write scope, frozen decisions, required evidence и escalation conditions.

Не делегировать центральное architecture/product/security решение. Не использовать несколько agents для одного shared file без frozen interface и одного integration owner.

После возврата проверять diff и evidence самостоятельно. Summary агента не является proof.

## 14. Синхронизировать документацию

Обновлять документацию, когда изменение затрагивает:

- public interface или user behavior;
- setup, configuration или commands;
- schema/migration/compatibility;
- architecture decision;
- operational procedure;
- known limitation или fallback.

Не добавлять documentation-only claim, который не подтверждён source/runtime. Удалять устаревшее утверждение или явно помечать future plan.

Сохранять один source of truth. README должен вести к contract/schema/runbook, а не дублировать их полностью.

Не создавать новый документ, если короткое изменение существующего канонического места решает задачу.

## 15. Остановиться при правильном условии

Остановиться и запросить решение, если:

- требуется новое полномочие, credential или external write;
- project instructions конфликтуют с задачей;
- mandatory integration недоступна;
- dirty worktree пересекается и безопасное объединение неочевидно;
- expected behavior неоднозначно и варианты меняют product outcome;
- обнаружена security/privacy red line;
- migration необратима без утверждённого recovery path;
- bounded task превратился в architecture redesign;
- повторяются одинаковые failures без новой проверяемой гипотезы.

Не останавливаться только потому, что работа сложна. Сузить reproduction, проверить следующий факт или выделить blocker.

Slice завершён, когда:

- observable behavior реализован;
- required checks проходят на exact code/config;
- нет required skip/todo или placeholder path;
- diff соответствует scope;
- docs/contracts синхронизированы;
- ограничения и непроверенные уровни evidence названы честно.

Green unit test не равен release readiness. Перед `SHIP` выполнить отдельный release gate.

## 16. Короткий Build Brief

```markdown
## Build Brief
Delivery mode: EXPLORE | BUILD
Risk: LOW | STANDARD | CRITICAL
Outcome:
Included / excluded:
Invariants:

### Reality
Relevant path:
Existing pattern:
Dirty worktree:
Highest-risk unknown:

### Slice
First Red:
Minimal production change:
Required evidence:
Rollback/exit:

### Execution
Project commands:
Dependency/generated-code impact:
Delivery: KEEP_LOCAL | DELEGATE | PARALLELIZE | DECOMPOSE_FIRST
Docs/contracts to update:
```

Заполнять только поля, влияющие на действие или evidence.

## 17. Self-check

Общий self-check — в [`../SKILL.md`](../SKILL.md). Здесь только то, что проверяется именно этим файлом.

1. Dirty user changes сохранены?
2. Прослежен реальный behavior/data path?
3. Slice мал, вертикален и проверяем?
4. Debugging шёл от reproduction и hypothesis, а не случайных patches?
5. Diff свободен от scope creep, secrets, placeholders и debug output?

