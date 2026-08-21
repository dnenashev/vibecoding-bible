# Release receipt: vibecoding-bible v<version>

Заполняется человеком перед публикацией. Связывает версию skill, версию корпуса,
runner и фактический результат прогона. Judge verdict является advisory evidence
и сам по себе не закрывает release gate.

## Identity

- skill VERSION:
- release commit / tag:
- corpus version (`tests/forward-cases.yaml`):
- runner (`tests/run_forward_cases.py`) commit:
- validator (`scripts/validate_skill.py`) commit:

## Прогон

- run id (каталог в `tests/receipts/`):
- дата, окружение, reviewer:
- answer model / judge model:
- запущенные кейсы: positive __ / negative __ / boundary __ из __
- пропущенные кейсы и причина:

## Результат

- judge advisory verdict: PASS | BLOCKED
- blocking cases:
- infrastructure errors:
- расхождения, где reviewer не согласен с judge (обязательны к описанию):
- cross-case patterns:

## Валидация

- `scripts/validate_skill.py`: PASS | FAIL
- `scripts/validate_registry.py` (если применимо): PASS | FAIL
- установленная копия идентична релизному дереву: да | нет

## Verdict

- release_state: PENDING | CANDIDATE | ACCEPTED | RELEASED | BLOCKED
- reviewer confirmation (имя, дата):
- known non-blocking gaps с owner и сроком:
