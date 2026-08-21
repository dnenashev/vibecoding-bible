# Архитектура программного продукта

## Содержание

1. Назначение
2. Выбрать режим и тип продукта
3. Зафиксировать reality snapshot
4. Выбрать стек
5. Выбрать форму системы
6. Провести границы и ownership
7. Спроектировать domain и data
8. Зафиксировать API и integration contracts
9. Определить state, concurrency и caching
10. Спланировать migrations и compatibility
11. Задать non-functional requirements и failure modes
12. Учесть особенности платформы
13. Зафиксировать решение в ADR
14. Избегать антипаттернов
15. Короткий Architecture Brief
16. Self-check

## 1. Назначение

Использовать этот модуль на фазе `DESIGN`, когда нужно спроектировать новый продукт, функцию, integration или существенное изменение существующей системы.

Цель архитектуры — не нарисовать больше компонентов, а сделать critical path понятным, изменяемым и проверяемым. Выбирать самое простое устройство, которое выполняет утверждённые требования и выдерживает известные риски.

Сначала проектировать обычное программное обеспечение. Добавлять AI, agents, queues, caches, microservices и другие специальные механизмы только при подтверждённой потребности.

Результат модуля:

- ясные границы системы;
- владельцы данных и решений;
- проверяемые contracts;
- явные failure modes;
- минимальный набор architecture decisions для начала `BUILD`.

## 2. Выбрать режим и тип продукта

Сначала выбрать delivery mode и risk:

| Delivery mode | Архитектурный результат |
|---|---|
| `EXPLORE` | Один обратимый spike, временные границы и критерий `discard / continue / promote` |
| `BUILD` | Production-ready vertical slice и достаточные решения для его эксплуатации |

| Risk | Что добавляет к архитектуре |
|---|---|
| `LOW` | Ничего сверх базовых границ |
| `STANDARD` | Обычные ownership, failure modes и recovery |
| `CRITICAL` | Усиленные isolation, recovery, audit и approval boundaries |

Не проектировать весь будущий продукт, если текущая задача требует один slice. Не выпускать `EXPLORE`-решение в production без нового design review.

Определить основной тип продукта:

- web application;
- backend service или API;
- mobile или desktop application;
- CLI, script или automation;
- browser/IDE extension;
- data pipeline или scheduled job;
- library/SDK;
- embedded/edge component;
- AI workflow или agent system;
- сочетание нескольких типов.

Тип задаёт вопросы, а не готовый стек. Например, CLI требует продуманного exit status и non-interactive mode; mobile — offline state и upgrade path; API — versioning и client compatibility.

## 3. Зафиксировать reality snapshot

До target architecture описать текущее состояние по фактам:

1. Найти entrypoints, packages, runtime и deployment units.
2. Найти действующие schemas, migrations, APIs и внешние integrations.
3. Определить, где хранится authoritative state.
4. Проверить реальные версии runtime и dependencies.
5. Найти существующие project instructions и architecture decisions.
6. Отделить source evidence от README, планов и предположений.
7. Зафиксировать dirty worktree и незавершённые migrations.

Использовать компактную запись:

```text
Fact: подтверждено кодом, config, schema или runtime.
Assumption: рабочая гипотеза, которую нужно проверить.
Unknown: неизвестное, способное изменить решение.
Constraint: условие, которое нельзя нарушить.
```

Если самый опасный `unknown` делает архитектуру недоказуемой, провести короткий spike до фиксации решения.

## 4. Выбрать стек

Сначала использовать существующий поддерживаемый стек, если он закрывает critical path. Цена второго языка, framework или datastore включает deployment, observability, security updates, hiring и migration, а не только скорость первого прототипа.

Оценивать кандидаты по конкретным критериям:

- совместимость с текущим runtime и командой;
- соответствие critical path;
- зрелость нужных capabilities;
- эксплуатационная простота;
- testability и local development;
- portability и exit cost;
- performance в ожидаемом профиле нагрузки;
- security и update policy;
- стоимость инфраструктуры и поддержки.

Проводить spike только для спорной capability. Не строить параллельно два продукта ради выбора framework.

Technology default считать условным:

- использовать его, если он соответствует текущему stack и требованиям;
- заменить обоснованной альтернативой, если critical path этого требует;
- проверить актуальную официальную документацию и exact installed version;
- записать причину выбора, если она влияет на долгосрочную стоимость.

## 5. Выбрать форму системы

Для нового продукта начинать с одного deployable unit или modular monolith, если нет доказанной причины разделять runtime.

Разделять на services, только когда существует хотя бы одна материальная граница:

- независимое масштабирование по другому профилю нагрузки;
- отдельная security или compliance boundary;
- независимый lifecycle и ownership команды;
- разные availability/recovery требования;
- технологическое ограничение, не решаемое внутри одного runtime;
- isolation тяжёлой или ненадёжной workload.

Не использовать microservices для визуального выражения модулей. Модульность сначала обеспечить contracts и dependency direction внутри одного deployable unit.

Для каждого runtime component определить:

- одну ответственность;
- входы и выходы;
- owner;
- state ownership;
- failure behavior;
- deploy/rollback unit.

## 6. Провести границы и ownership

Проводить границы по бизнес-возможностям и change patterns, а не по техническим существительным `controllers/services/utils`.

Для каждой границы указать:

- какие решения она принимает;
- какими данными владеет;
- какие инварианты защищает;
- какие contracts публикует;
- от каких компонентов зависит;
- что запрещено обходить напрямую.

Соблюдать однонаправленные зависимости. Domain layer не должен знать детали UI, provider SDK или storage driver. Интеграционные детали закрывать adapters там, где это действительно облегчает tests, migration или замену provider.

Не создавать abstraction «на будущее». Создавать её при наличии двух реализаций, нестабильной внешней границы или важной test seam.

## 7. Спроектировать domain и data

Начинать с сущностей, состояний и инвариантов, а не с таблиц или экранов.

Определить:

- ключевые entities и stable identifiers;
- допустимые state transitions;
- обязательные и nullable поля;
- uniqueness и referential constraints;
- tenant/owner boundary;
- source of truth для каждого факта;
- provenance, timestamps и versioning;
- retention, deletion и export expectations;
- derived data и способ пересчёта.

Использовать database constraints для инвариантов, которые база способна гарантировать. Не полагаться только на prompt, UI validation или один code path.

Не дублировать authoritative state без synchronization contract. Cache, search index, analytics warehouse и AI memory считать производными stores, если явно не решено иначе.

Для AI-generated data хранить достаточно provenance: model/config/rule versions, source references, creation time и validation status. Не смешивать гипотезу модели с подтверждённым domain fact.

## 8. Зафиксировать API и integration contracts

Для каждой boundary зафиксировать минимальный contract:

- protocol и endpoint/event/tool name;
- authenticated caller и permissions;
- input/output schema;
- validation и error model;
- timeout и cancellation;
- retry semantics;
- idempotency для mutation;
- pagination, ordering и rate limits;
- versioning и compatibility policy;
- observability identifiers.

Для внешней integration дополнительно определить:

- sandbox/live environments;
- credential owner и secret reference;
- provider limits и outage behavior;
- readback после consequential mutation;
- fallback: `block`, `manual` или `deterministic`;
- reconciliation и rollback/compensation.

Не возвращать fabricated success при недоступности provider. Не считать HTTP `200` доказательством бизнес-эффекта без нужного readback.

## 9. Определить state, concurrency и caching

Для mutable operation ответить:

1. Кто может менять state?
2. Что произойдёт при двух одновременных запросах?
3. Где проходит transaction boundary?
4. Как обнаружить duplicate, stale write и partial failure?
5. Как безопасно повторить operation после timeout?

Выбирать optimistic locking, uniqueness constraint, transaction, queue или serialization по реальному конфликту. Не добавлять distributed lock без доказанной необходимости.

Cache добавлять только после определения:

- измеримого bottleneck;
- cache key и tenant boundary;
- TTL/freshness requirement;
- invalidation owner;
- поведение при miss и stale value;
- способ отключить cache при incident.

Кеширование не должно менять correctness незаметно.

## 10. Спланировать migrations и compatibility

Каждое изменение persisted schema или public contract планировать как переход между двумя состояниями.

Определить:

- backward/forward compatibility window;
- порядок deploy и migration;
- expand/migrate/contract для breaking schema change;
- backfill и его rate/resource limits;
- checkpoint/resume и idempotency;
- validation/readback после migration;
- rollback или roll-forward strategy;
- момент удаления старого path.

Не совмещать необратимую migration и зависимый code release без безопасного порядка. Не считать backup rollback, пока восстановление не проверено.

Versioned consumer contract сохранять до подтверждения, что все consumers перешли. Для offline clients учитывать старые app versions.

## 11. Задать non-functional requirements и failure modes

Задавать NFR числом или наблюдаемым условием только там, где оно влияет на решение:

- expected load и growth envelope;
- latency/throughput;
- availability и degradation;
- recovery time и recovery point;
- data volume и retention;
- cost ceiling;
- accessibility/platform compatibility;
- operational ownership.

Не изобретать SLA без product need и measurement path.

Для critical path пройти короткий failure review:

| Failure | Что определить |
|---|---|
| Dependency timeout | deadline, retry, fallback |
| Partial mutation | transaction, outbox или compensation |
| Duplicate request | idempotency и deduplication |
| Process restart | persisted state и resume |
| Stale client/state | version check и conflict response |
| Invalid data | validation, quarantine и repair |
| Load spike | backpressure, limits и degradation |
| Bad release | readback, feature flag и rollback |

Глубокие security, quality и operations protocols применять в соответствующих фазах; здесь определить лишь границы и требования, влияющие на architecture.

## 12. Учесть особенности платформы

### Web application

Определить server/client boundary, rendering strategy, session/auth flow, accessibility и browser support. Не добавлять client state manager, если URL, server state и local component state достаточны.

### Backend/API

Определить contract/versioning, authz, rate limits, background work, idempotency и operational endpoints. Не выполнять долгую работу внутри request без deadline и recovery model.

### Mobile/desktop

Определить offline behavior, sync/conflicts, secure local storage, update compatibility, deep links и platform permissions. Учитывать, что старые clients нельзя обновить мгновенно.

### CLI/automation

Определить stdin/stdout/stderr, exit codes, non-interactive mode, dry-run, idempotency и config precedence. Не печатать secrets и не зависеть от UI prompt в automation path.

### Data pipeline

Определить source watermark, schema drift, replay, deduplication, late data, data quality и lineage. Каждый batch/run должен быть идентифицируем и безопасно повторяем.

### Library/SDK

Определить public API, semantic versioning, supported runtimes, error model и migration notes. Не экспортировать internal framework types без необходимости.

### AI workflow

Отделить deterministic orchestration от probabilistic decisions. Agent framework, memory, evals и tokenomics проектировать через специализированные references, не переносить их автоматически на обычный код.

## 13. Зафиксировать решение в ADR

Создавать ADR для решения, которое:

- трудно и дорого отменить;
- меняет system boundary или source of truth;
- добавляет runtime, datastore или внешний provider;
- влияет на security, compatibility или operations;
- имеет реальные альтернативы и trade-offs.

Использовать короткий формат:

```markdown
# ADR: <решение>
Status: proposed | accepted | superseded
Context: какие факты и ограничения требуют решения
Decision: что выбираем и для какого scope
Alternatives: какие реалистичные варианты отклонены и почему
Consequences: что упрощается, что усложняется
Validation: какой test/spike/runtime evidence подтвердит решение
Rollback/exit: как отменить или заменить решение
```

Не создавать ADR для очевидной локальной детали. При изменении frozen decision создавать новый ADR и помечать старый superseded.

## 14. Избегать антипаттернов

- Начинать с target diagram без reality snapshot.
- Выбирать стек по популярности или личному вкусу.
- Добавлять microservices, queues, cache или agents без конкретной причины.
- Прятать business invariants в UI, prompts или cron scripts.
- Делить систему на слои без ownership и contracts.
- Иметь несколько sources of truth без reconciliation.
- Использовать shared database как скрытый API между независимыми services.
- Проектировать только happy path.
- Обещать exactly-once delivery вместо доказуемого exactly-once business effect.
- Создавать универсальные abstractions до появления реальных вариантов.
- Игнорировать migration и старые clients.
- Выдавать provider/framework capability за проверенный project property.

## 15. Короткий Architecture Brief

```markdown
## Architecture Brief
Delivery mode: EXPLORE | BUILD
Risk: LOW | STANDARD | CRITICAL
Product type:
Outcome / critical path:

### Reality
Facts:
Constraints:
Highest-risk unknown:

### Decision
Deployable units:
Module boundaries and owners:
Authoritative data stores:
Public/integration contracts:
State and concurrency model:
Migration/compatibility path:

### Quality attributes
Required NFR:
Top failure modes and controls:

### Validation
Spike or contract test:
Required ADRs:
Rollback/exit path:
```

Заполнять только применимые поля. Для маленького delta достаточно нескольких строк.

## 16. Self-check

1. Архитектура начинается с outcome и actual state?
2. Delivery mode и risk выбраны отдельно и соответствуют работе?
3. Conventional solution рассмотрено до специальных frameworks?
4. Stack выбран по critical path и operations, а не по вкусу?
5. Deployable units минимальны?
6. Boundaries имеют ownership, contracts и dependency direction?
7. Для каждого факта определён source of truth?
8. State transitions, concurrency и partial failures определены?
9. Integrations имеют timeout, idempotency и fallback semantics?
10. Migration сохраняет нужную compatibility?
11. NFR измеримы и действительно влияют на design?
12. Platform-specific behavior учтено?
13. Дорогие решения зафиксированы в коротких ADR?
14. Есть проверяемый validation step и exit path?
