# Словарь: канонические значения

Единственный источник истины для публичных enum Библии. Любой другой файл skill
ссылается на этот словарь и не переопределяет значения. Расхождение между словарём
и reference считать дефектом skill, а не поводом для локальной трактовки.

Валидатор `scripts/validate_skill.py` проверяет, что значения ниже употребляются
согласованно во всех файлах.

## Фаза lifecycle

`UNDERSTAND | DESIGN | BUILD | VERIFY | SHIP | LEARN`

Фаза описывает, где находится работа. Она не является уровнем строгости и не
определяет глубину контракта сама по себе.

## Режим строгости

`EXPLORE | BUILD | CRITICAL`

- `EXPLORE` — обратимый эксперимент без production claim;
- `BUILD` — default: маленький production-ready slice;
- `CRITICAL` — усиленный контур для payments, PII, regulated data, high autonomy,
  необратимых действий и большого blast radius.

Режим `BUILD` и фаза `BUILD` — разные вещи с совпадающим именем. Различать по контексту:
фаза отвечает на вопрос «где мы», режим — «насколько строго».

## Глубина контракта

`lite | standard | full | critical`

- `lite` — bounded low-risk change в существующей системе;
- `standard` — новый product, feature или integration, заметное изменение behavior;
- `full` — новая система, migration или широкий cross-cutting change;
- `critical` — любой scope в режиме `CRITICAL`, с усиленными threat, evidence,
  approval и recovery полями.

Глубина выводится из режима и размера scope; явный override допускается с указанием причины.

## Вердикты

Два gate имеют разные словари. Не переносить значение одного в другой.

```
implementation_verdict: READY | READY_WITH_CONSTRAINTS | BLOCKED
release_state:          PENDING | CANDIDATE | ACCEPTED | RELEASED | BLOCKED
```

- `READY` — весь заявленный scope разрешён;
- `READY_WITH_CONSTRAINTS` — разрешён только точный безопасный scope; constraint обязан
  содержать scope, owner, expiry, compensating control, validation и closure criterion;
- `BLOCKED` — нельзя начинать затронутый scope.

Состояния релиза:

- `PENDING` — release ещё не оценивался; состояние по умолчанию до появления evidence;
- `CANDIDATE` — собран immutable candidate, evidence привязан к нему, ожидается QA/ACCEPT;
- `ACCEPTED` — получен точный ACCEPT, связанный с identity кандидата;
- `RELEASED` — выполнены deploy, readback и подтверждение целевой среды;
- `BLOCKED` — применима release red line.

Формулировка «release verdict» в прозе означает решение по `release_state`, а не отдельный
словарь. Соответствие потоку bug repair: собран immutable candidate — `CANDIDATE`; получен
точный ACCEPT — `ACCEPTED`; выполнены deploy и readback — `RELEASED`.

Implementation readiness не является release readiness. Зелёный кандидат не доказывает,
что в него вошли все принятые handoffs.

## Классификация handoff в release intent

`INTEGRATED | DEFERRED | SUPERSEDED | MISSING`

`MISSING` блокирует релиз.

## Уровни evidence

`source | static | unit | component | contract | integration | e2e | live_observation`

Порядок — от слабого к сильному. Слабый уровень не заменяет требуемый сильный.
Полная таблица «что доказывает / что не доказывает» — в
[`project-contract.md`](project-contract.md), раздел «Evidence levels».

## Статусы записи Regression Registry

`draft | active | quarantined | superseded | deprecated`

Определения и правила перехода — в [`regression-registry.md`](regression-registry.md).

## Метки истинности

`fact | assumption | unknown | not_applicable`

## Delivery verdict

`KEEP_LOCAL | DELEGATE | PARALLELIZE | DECOMPOSE_FIRST`

Выбирается до начала работы, описывает распределение исполнения, а не уровень риска.

## Виды forward-кейсов

`positive | negative | boundary`

Используются корпусом `tests/forward-cases.yaml`. Лишнее срабатывание Библии на
`negative` — такой же blocking failure, как пропуск свойства на `positive`.
