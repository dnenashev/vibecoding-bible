# Release receipt: vibecoding-bible v2.1.0

Judge verdict является advisory evidence и сам по себе не закрывает release gate.
Поле «reviewer confirmation» заполняет человек; агент его не подписывает.

## Identity

- skill VERSION: 2.1.0
- release commit / tag: коммит, помеченный `v2.1.0` (включает этот receipt) / `v2.1.0`
- дерево skill на момент прогона: `f7f9ca0` — идентично дереву skill в release commit
- corpus version (`tests/forward-cases.yaml`): 1, обновлён в `f7f9ca0` (32 кейса)
- runner (`tests/run_forward_cases.py`) commit: `ac4247e`
- validators commit: `scripts/validate_skill.py` — `f7f9ca0`; `validate_registry.py` — не изменялся, неприменим

## Прогон

- run id: `tests/receipts/2026-08-22T08-48-12`
- дата, окружение: 2026-08-22, darwin
- reviewer: PENDING — подтверждает владелец репозитория
- answer model / judge model: session default / session default (тот же класс модели)
- запущенные кейсы: positive 5 / negative 2 / boundary 1 из 32
- пропущенные кейсы и причина: 24 кейса не затронуты дельтой — изменения касаются
  `agent-harness.md`, `build.md`, `production.md`, `ai-systems.md`, `core-principles.md`,
  `vocabulary.md` и `SKILL.md`; отобраны четыре новых кейса и четыре соседних по этим же
  файлам для проверки на overfitting

## Результат

- judge advisory verdict: PASS (8 из 8)
- blocking cases: нет
- infrastructure errors: нет
- расхождения reviewer с judge: PENDING — reviewer ещё не разбирал прогон
- cross-case patterns:
  - оба сторожевых кейса отработали в нужную сторону: на обратимой правке risk `LOW`
    тяжёлый контур не развернулся, объяснение задним числом не принято как evidence;
  - соседние кейсы не деградировали: `existing_bug_dirty_worktree`,
    `zero_downtime_tenant_migration`, `use_existing_agent_execution_harness` и
    `negative_text_reformatting` сохранили прежнее поведение;
  - повторяющаяся слабость не в дельте, а в плотности изложения: judge дважды отметил
    перегруженность ответа при `strong` по существу

## Валидация

- `scripts/validate_skill.py`: PASS — 0 ошибок
- `validate_registry.py`: неприменимо
- установленная копия идентична релизному дереву: проверяется после публикации тега

## Verdict

- release_state: `CANDIDATE`
- обоснование: тег `v2.1.0` создан как immutable identity кандидата и как условие
  проверки установленных копий валидатором. Он не является ACCEPT: точный ACCEPT даёт
  человек после разбора прогона, и только он переводит состояние в `ACCEPTED`/`RELEASED`
- reviewer confirmation (имя, дата): PENDING

## Known non-blocking gaps

1. В кейсе `boundary_expectation_written_after_action` отвечающий агент сослался на
   `docs/EXPECTATION-GATE-2026-08-22.md:37` и на внутренний `case_id` корпуса, не прочитав
   источник. Поведение корректное, опора — непроверенная. Причина, вероятно, средовая:
   рабочим каталогом прогона был релизный worktree, где `docs/` виден агенту.
   Owner: следующий прогон запускать из disposable fixture, а не из дерева репозитория.
2. Сжатие канона (`testing-harness.md` разделы 7 и 9) не выполнено; бюджет объёма
   превышен на 4 строки. Условие снятия — накопленные receipts с полем `expectation`.
   Owner: см. `docs/EXPECTATION-GATE-2026-08-22.md`, раздел 5.
3. Полезность правил на реальной инженерной работе не измерена: forward-кейсы проверяют
   поведение агента на запросе, а не исход задачи.
