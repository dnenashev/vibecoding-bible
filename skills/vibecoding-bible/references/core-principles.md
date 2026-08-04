# Канон: простое production-ready вайбкодинг-проектирование

## Содержание

1. Назначение
2. Приоритеты
3. Простота и scope
4. Truth и evidence
5. Изменения и TDD
6. Реальные boundaries
7. Human и AI autonomy
8. Production minimum
9. Исключения
10. Диагностическая матрица

## 1. Назначение

Канон применяется к любому цифровому продукту, создаваемому с помощью AI: conventional software и AI systems. Цель — минимальный путь к принятому outcome без скрытого долга, fabricated evidence и неконтролируемого риска.

AI помогает проектировать и реализовывать. Он не отменяет product reasoning, инженерные границы, permissions и проверку фактического результата.

## 2. Приоритеты

При конфликте выбирать в таком порядке:

1. Реальный outcome пользователя.
2. Безопасность и корректность выбранного scope.
3. Простота понимания, изменения и эксплуатации.
4. Проверяемость и обратимость.
5. Скорость и стоимость достижения результата.
6. Удобство конкретной технологии/framework.

Не автоматизировать waste. Сначала понять решение или действие, которое должно измениться; затем убрать лишние шаги; только после этого добавлять software/AI.

## 3. Простота и scope

### Принцип

Выбирать самую простую архитектуру, которая честно выдерживает requirements и risk. Не выбирать самый короткий код ценой потери данных, безопасности или поддержки.

### Режимы

- `EXPLORE` — reversible experiment без production claim;
- `BUILD` — default: маленький production-ready vertical slice;
- `CRITICAL` — усиленный контур для high-impact риска.

Scope уменьшать удалением функциональности, а не качества внутри принятой границы.

### Production-ready slice

Минимум по применимости:

- законченный user journey;
- реальные data/integration boundaries;
- loading/empty/error/retry/cancel states;
- persistence/migration/compatibility;
- permissions и privacy;
- tests нужного уровня;
- observability;
- deploy/readback/rollback;
- explicit limitations.

### Не усложнять заранее

Не добавлять без доказанной необходимости:

- microservices;
- multi-agent topology;
- event bus;
- distributed cache;
- custom framework;
- premature abstraction;
- новый database/provider;
- generalized plugin system.

## 4. Truth и evidence

Различать:

- `fact` — подтверждён source/runtime evidence;
- `assumption` — рабочая гипотеза с validation;
- `unknown` — неизвестное с owner/next probe;
- `not_applicable` — неприменимо с причиной.

Иерархия evidence:

```text
source/static → unit → component/contract → integration → E2E → live observation
```

Более слабый уровень не заменяет требуемый сильный. README, self-report агента, screenshot или `passed: true` без resolvable evidence не доказывают production behavior.

Не сохранять hidden chain-of-thought. Сохранять observable inputs, decisions, versions, actions, evidence и outcomes.

## 5. Изменения и TDD

Каждое изменение behavior выполнять так:

1. Зафиксировать current и expected behavior.
2. Ограничить write scope и invariants.
3. Создать минимальный failing behavioral test — Red.
4. Убедиться, что он падает по ожидаемой причине.
5. Реализовать минимальный Green.
6. Refactor только внутри согласованного scope.
7. Запустить regressions и required higher-level evidence.
8. Синхронизировать docs/decisions.

Запрещено:

- писать feature code до проверяемого behavior contract;
- ослаблять assertion ради Green;
- менять expected output на фактический только из-за fail;
- оставлять required skip/todo;
- делать branch под конкретный fixture;
- превращать соседний redesign в «небольшой fix».

## 6. Реальные boundaries

### Mocks

Mock/fake/stub разрешён только в test-only composition root и не считается live evidence. Production path не содержит hardcoded success, placeholder core behavior или fabricated provider result.

Нет credential/provider access — это `BLOCKED`, configuration error либо explicit manual/deterministic fallback.

### Integrations

Для каждой mandatory integration определить:

- exact provider/environment/version;
- typed contract;
- auth/permission boundary;
- timeout/retry/rate limit;
- failure/fallback behavior;
- sandbox/live verification.

### Data

Назвать owner и source of truth. Определить schema/version, provenance, privacy, retention, migration, backup/recovery и stale propagation по риску.

### External mutations

Требовать exact target, least privilege, idempotency, bounded diff, risk-based approval, post-action readback, rollback/compensation и audit event.

## 7. Human и AI autonomy

Deterministic order, invariants и side-effect control реализовывать кодом/workflow. AI использовать для open-ended decisions, где допустимые действия ограничены policy, tools и evidence.

Autonomy задавать на уровне конкретного decision/action:

- proposal;
- bounded artifact;
- reversible action;
- broader action with canary/readback/rollback;
- high autonomy только после production evidence и approval.

Human correction не становится truth автоматически. Проверить её против правил и outcome. AI/judge/repairer не подтверждает собственный consequential pass.

Для AI systems применять versioned context/rules/models/tools, fallback, token/cost budgets и EvalSuite. Для первого сложного workflow — calibration-first TestingHarness.

## 8. Production minimum

По риску определить:

- authentication/authorization/tenancy;
- secrets/privacy/data handling;
- performance/capacity/reliability;
- logs/metrics/traces и SLO;
- environments/config/CI-CD;
- migration/deploy/readback/rollback;
- backup/recovery/incident owner;
- analytics/feedback/outcome window.

Не объявлять production-ready по одному локальному happy path. Не требовать enterprise controls для reversible EXPLORE spike.

## 9. Исключения

Exception не отменяет red line. Допустимое исключение содержит:

- exact scope и reason;
- owner/approvedBy;
- risk и compensating control;
- expiry;
- validation и closure criterion.

Постоянное, бесхозное или недокументированное исключение запрещено.

## 10. Диагностическая матрица

| Симптом | Сначала проверить | Не делать первым |
|---|---|---|
| Непонятно, что строить | user/problem/current way/outcome | выбирать framework |
| Scope разрастается | mode, slice, non-goals, critical unknown | добавлять ещё backlog |
| Агент ломает соседний код | write scope, tests, ownership, dirty state | просить «быть осторожнее» |
| После compaction теряются решения | project context, decision log, bounded delegation | расширять prompt бесконечно |
| Баг чинится случайными patches | reproduction, hypothesis, localization, first Red | переписывать модуль целиком |
| Unit зелёный, prod ломается | evidence gap, integration/E2E/live path | добавлять mocks |
| AI output нестабилен | context/rules/schema/evals/fallback | бесконечные retries |
| UI неудобен | journey, IA, states, accessibility, user validation | косметический polish |
| Стоимость растёт | calls/outcome, context, retries, architecture waste | менять модель без baseline |
| Release страшно делать | migrations, flags, canary, readback, rollback | ручной deploy без evidence |
| Процесс слишком тяжёл | risk mode и применимость artifacts | удалять safety red lines |
