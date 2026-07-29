# Канон: production-ready вайбкодинг

## Содержание

1. Назначение
2. Lean AI
3. Oper8
4. Production-ready scope
5. Политика mocks
6. TDD
7. Tokenomics
8. shadcn
9. Evidence и operations
10. Исключения
11. Диагностическая матрица

## 1. Назначение

Этот канон определяет, как проектировать и реализовывать AI-продукты, функции и agent workflows. Его цель — не максимальная скорость генерации кода, а минимальный путь к принятому outcome с контролируемым риском, стоимостью и проверяемым поведением.

Порядок приоритетов:

1. Реальный outcome пользователя или бизнеса.
2. Безопасность и корректность принятого scope.
3. Проверяемость и управляемость системы.
4. Скорость и стоимость достижения outcome.
5. Удобство реализации.

## 2. Lean AI

### Главный тезис

Не автоматизировать waste. Сначала определить решение или outcome, которое должно измениться; затем убрать лишние шаги; только после этого добавлять AI.

Для каждого workflow зафиксировать:

- consumer;
- Core Job/current way и наблюдаемую потерю;
- expected outcome и downstream decision;
- primary metric и counter-metrics;
- гипотезу, почему AI улучшит outcome;
- минимальный набор AI decisions;
- стоимость одного принятого outcome.

### Инварианты Lean AI

- Value before AI.
- Один artifact имеет одну ясную ответственность.
- Observation, fact, inference, hypothesis и unknown различимы.
- Сначала standard stream, отдельно risky/exception stream.
- AI decision не равен внешнему action.
- Human correction не становится production truth автоматически.
- Eval score не подменяет business outcome.
- Fine-tuning не является обязательным default.
- Повторный ручной перенос и лишние model hops считаются waste.
- Scope уменьшается удалением функциональности, а не качества.

## 3. Oper8

Oper8 превращает AI-функцию в управляемую операционную систему.

### Шесть обязательных контрактов

1. `ContextPack` — versioned вход, provenance, freshness, разрешённые данные и missing facts.
2. `Rulebook` — deterministic rules, owners, effective dates, exceptions и change process.
3. `EvalSuite` — representative cases, primary/counter-metrics, red lines и expected evidence.
4. `AutonomyPolicy` — уровни самостоятельности, permissions, approvals, stop rules и maximum level.
5. `DecisionRecord` — выбранная альтернатива, alternatives considered, context/model/rules/tools versions, confidence и human intervention.
6. `OutcomeRecord` — фактический результат после observation window, source refs, attribution confidence и win/loss/inconclusive.

### Уровни автономности

- `A1` — AI только предлагает; человек принимает решение и действует.
- `A2` — AI готовит bounded artifact; человек проверяет/утверждает.
- `A3` — AI выполняет reversible low-risk action под policy и audit.
- `A4` — AI выполняет более широкие действия с canary/readback/rollback.
- `A5` — высокая автономность; допустима только после сильного production evidence и отдельного approval.

Autonomy определяется на уровне конкретного decision/action, а не «агента в целом». Повышать её только по evidence; red-line failure блокирует promotion и может требовать rollback.

### Memory и freshness

- Назвать владельца каждого memory store.
- Хранить provenance и captured/effective timestamps.
- Не смешивать working memory, durable facts, rules и outcomes.
- Upstream change создаёт новую версию и помечает dependents `stale`.
- Retrieval не делает информацию истинной; retrieved item проходит relevance/freshness/authorization checks.
- Не хранить скрытую chain-of-thought; хранить проверяемые decisions и evidence.

## 4. Production-ready scope

### Правило

По умолчанию строить production-ready product/function, а не throwaway MVP. Допустим маленький vertical slice, но внутри него обязательны:

- полный обязательный user journey;
- реальные data/integration boundaries;
- error/empty/loading/retry states;
- persistence и migrations;
- security и permissions;
- observability;
- deploy/readback/rollback;
- tests нужных уровней;
- documented limitations без ложных claims.

### Что можно отложить

- дополнительные сегменты и роли;
- второстепенные workflows;
- необязательные integrations;
- optimization после подтверждённого bottleneck;
- масштабирование, не требуемое утверждённой нагрузкой.

### Что нельзя называть MVP-исключением

- публичную утечку данных;
- эфемерное required state;
- отсутствие rollback для материальной мутации;
- fake integration;
- hardcoded success;
- отсутствие cost limits для paid AI;
- unit-only доказательство live path;
- обязательный путь, работающий только вручную вопреки заявлению.

## 5. Политика mocks

### Production-strict policy

Запрещены в production/runtime/integration/live evidence:

- mock/fake data, выдаваемые пользователю как реальные;
- hardcoded provider response или happy path;
- placeholder implementation обязательной функции;
- env/header/query branch, включающий QA behavior в production service;
- fallback credential или secret в коде;
- catch-all, превращающий failure в fabricated success;
- demo brands/payloads в accepted production artifact.

### Допустимые test doubles

Разрешены только когда одновременно выполнено:

1. Double находится в test-only composition root и отсутствует в production bundle.
2. Он заменяет внешнюю границу, а не tested domain logic.
3. Он нужен для deterministic unit/component/replay case.
4. Test явно маркирован как non-live evidence.
5. Обязательная integration отдельно проверяется sandbox/live evidence.

Нет ключа или provider access — это `blocked`, configuration error либо честный manual/deterministic fallback. Не повод мокать runtime.

## 6. TDD

### Цикл

1. Зафиксировать behavior и evidence level.
2. Написать минимальный поведенческий test.
3. Запустить и убедиться, что он падает по ожидаемой причине — Red.
4. Реализовать минимальный production path — Green.
5. Refactor без расширения контракта.
6. Запустить regression и более высокие evidence levels.
7. Связать найденный production defect с новым regression case.

### Запреты

- Не писать production code до подтверждённого Red для нового behavior.
- Не ослаблять assertion ради Green.
- Не менять expected output на фактический только потому, что test упал.
- Не принимать required skip/todo/warning как release success.
- Не делать production branch специально под fixture.
- Не считать snapshot/source-string test достаточным для behavior, требующего runtime/E2E.

## 7. Tokenomics

### Pre-call

Каждый runtime AI request должен иметь:

- exact model и versioned billing policy;
- input upper bound;
- max output tokens;
- worst-case cost;
- per-call, per-run, daily и monthly caps;
- atomic reservation до network fetch;
- attempt budget и общий deadline.

Если policy отсутствует, model mismatch или cap превышен — request блокируется до fetch.

### Post-call

Settlement сохраняет:

- provider-reported input/output/cached tokens;
- actual либо явно estimated/conservative cost;
- model/billing/policy attribution;
- success/failure/timeout status;
- workflow/run/request/attempt identifiers.

Неизвестная стоимость не равна нулю. Paid response без valid usage fail closed, кроме заранее описанного conservative accounting для provider surface без token usage.

### Optimization target

Оптимизировать:

```text
cost_per_accepted_outcome = total_workflow_cost / accepted_outcomes
```

Сокращать лишние context, retries и model hops, но не ценой correctness, evidence или downstream rework.

## 8. shadcn

Для web UI:

1. Обнаружить `components.json`.
2. Использовать доступный `shadcn` skill.
3. Получить actual project context через project package runner.
4. Проверить `base`, framework, RSC, Tailwind version, aliases, icon library и installed components.
5. Получить актуальную документацию затрагиваемых primitives.
6. Использовать existing components и built-in variants до custom markup/styles.
7. Добавить automated source/component/browser conformance.

Обязательные общие правила:

- semantic tokens вместо raw palette;
- `FieldGroup`/`Field` для forms;
- correct Base/Radix APIs;
- full component composition;
- Spinner/Skeleton/Empty/Alert/Separator вместо hand-built replacements;
- configured icon library и icon contract;
- штатные chat primitives для conversation UI;
- keyboard, focus, accessibility, responsive и console-warning evidence.

## 9. Evidence и operations

### Уровни evidence

1. `source_inspection` — наличие и структура кода.
2. `unit` — локальная логика.
3. `component` — component behavior на контролируемых границах.
4. `contract` — schema/interface compatibility.
5. `integration_sandbox` — реальная тестовая интеграция.
6. `e2e_live` — обязательный live-like путь.
7. `production_observation` — outcome, нагрузка и downstream effects.

Более слабый уровень не подменяет требуемый сильный.

### Observability minimum

Сохранять identifiers/versions, state transitions, model/tools, token usage/cost, attempts/deadline, approvals, mutations, readback, stale/rollback и pending outcome. Маскировать secrets/PII; не сохранять chain-of-thought.

### External mutations

Требовать:

- exact target и permission;
- idempotency key;
- bounded diff;
- approval по risk class;
- post-action readback;
- rollback/compensation;
- audit event и outcome window.

## 10. Исключения

Exception не отменяет red line. Допустимо только для некритического constraint и содержит:

- reason и exact scope;
- owner и approvedBy;
- effectiveFrom/expiresAt;
- risk и compensating control;
- machine check и regression test;
- closure criterion.

Постоянное, бесхозное или недокументированное exception запрещено.

## 11. Диагностическая матрица

| Симптом | Сначала проверить | Не делать первым |
|---|---|---|
| Агент пишет много, результата нет | outcome, step count, context waste | добавлять ещё prompt-инструкции |
| Агент ломает соседний код | scope, write permissions, tests, ownership | просить «быть осторожнее» |
| После compaction теряются решения | ContextPack, decision log, делегирование bounded task | бесконечно расширять system prompt |
| AI output нестабилен | schema, evidence, eval cases, deterministic boundaries | увеличивать retries без cap |
| Unit tests зелёные, prod ломается | evidence gap, real integration, E2E/live path | добавлять ещё mocks |
| Стоимость растёт | calls/outcome, context, retries, model routing | оптимизировать цену одного prompt изолированно |
| UI выглядит несистемно | actual shadcn context и conformance | писать новый component с нуля |
| Agent workflow нельзя отладить | DecisionRecord, versions, events, readback | логировать chain-of-thought |
| Agent orchestration собирается вручную | нужен ли framework; для TypeScript сначала оценить Mastra | добавлять framework без use-case и contract |
| «MVP» накопил долги | production-ready slice boundary | переписывать всё без contract |
