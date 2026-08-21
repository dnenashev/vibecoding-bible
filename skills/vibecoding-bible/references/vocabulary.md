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

## Delivery mode

`EXPLORE | BUILD`

- `EXPLORE` — обратимый эксперимент без production claim;
- `BUILD` — default: маленький production-ready slice.

Режим `BUILD` и фаза `BUILD` — разные вещи с совпадающим именем. Фаза отвечает на вопрос
«где мы», delivery mode — «что мы выпускаем».

## Risk

`LOW | STANDARD | CRITICAL`

- `LOW` — обратимое изменение с малым blast radius и без чувствительных данных;
- `STANDARD` — default для реального продукта;
- `CRITICAL` — payments, PII, regulated data, high autonomy, необратимое действие или
  большой blast radius.

Delivery mode и risk независимы. Допустимы все четыре сочетания, включая
`EXPLORE + CRITICAL` — исследование на чувствительных данных.

До версии 2.0.0 существовал один enum `EXPLORE | BUILD | CRITICAL`. Соответствие при
переносе старых артефактов: `EXPLORE` → `EXPLORE + LOW` (или `+ CRITICAL`, если данные
чувствительные), `BUILD` → `BUILD + STANDARD`, `CRITICAL` → `BUILD + CRITICAL`.

## Глубина контракта

`lite | standard | full | critical`

- `lite` — bounded change при risk `LOW`;
- `standard` — новый product, feature или integration, заметное изменение behavior;
- `full` — новая система, migration или широкий cross-cutting change;
- `critical` — любой scope при risk `CRITICAL`, с усиленными threat, evidence,
  approval и recovery полями.

Глубина выводится из risk и размера scope: `LOW` → `lite`, `STANDARD` → `standard` или
`full`, `CRITICAL` → `critical`. Явный override допускается с указанием причины.

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

## Delivery lane и человеческие подтверждения

Дорожки доставки исправления, определения — в [`bug-repair.md`](bug-repair.md):

- `READY_FOR_BATCH` — проверенный fix ждёт ближайший release batch; default для несрочного;
- urgent hotfix — отдельная дорожка для срочного исправления с тем же exact-candidate контуром.

Человеческие подтверждения различаются по силе и не заменяют друг друга:

- `PREVIEW PASS` — пользователь подтвердил конкретный сценарий на preview-сборке;
- `QA PASS` — пройдена QA на immutable candidate;
- `ACCEPT` — точное разрешение на релиз, привязанное к identity кандидата.

`PREVIEW PASS` никогда не становится `ACCEPT` автоматически.

## Уровни evidence

`source | static | unit | component | contract | integration | e2e | live_observation`

Порядок — от слабого к сильному. Слабый уровень не заменяет требуемый сильный.
Полная таблица «что доказывает / что не доказывает» — в
[`project-contract.md`](project-contract.md), раздел «Evidence levels».

## Verdict проверки и решения человека на checkpoint

Результат проверки (TestingHarness, EvalSuite, Registry run):

`PASS | FAIL | INSUFFICIENT_EVIDENCE`

`INSUFFICIENT_EVIDENCE` — отдельное значение, а не разновидность `PASS`. Недоступное
trusted evidence даёт его или `BLOCKED`, но никогда `PASS`.

Решение человека на checkpoint:

`APPROVE | REJECT | CHANGE_CRITERION | ESCALATE`

- `APPROVE` — качество и evidence устраивают, checkpoint замораживается;
- `REJECT` — результат не соответствует ожиданию; обязателен reason;
- `CHANGE_CRITERION` — критерий был неполон или ошибочен; правится критерий, а не результат;
- `ESCALATE` — нужно продуктовое, risk или permission решение.

Определения и порядок применения — в [`testing-harness.md`](testing-harness.md).

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
