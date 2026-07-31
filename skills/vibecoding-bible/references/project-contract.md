# VibecodingProjectContract

## Содержание

1. Назначение
2. Full и delta
3. Заполнение
4. Структура
5. Gates
6. Red lines
7. Evidence levels
8. Human-readable template
9. Self-check

## 1. Назначение

`VibecodingProjectContract` — обязательный preflight и acceptance contract для нового проекта, крупной функции, AI workflow, интеграции, migration, security/permissions/autonomy change или production release.

Он отвечает на четыре вопроса:

1. Какой реальный outcome должен измениться?
2. Какой минимальный scope будет полностью production-ready?
3. Какие архитектура, harness и guardrails сделают результат управляемым?
4. Каким evidence будет доказано решение задачи?

Контракт содержит два независимых gate:

- `implementation gate` — безопасно ли начинать код;
- `release gate` — доказано ли после реализации, что scope production-ready.

Ожидаемый Red test совместим с implementation readiness, но тот же fail блокирует release.

## 2. Full и delta

### `full`

Использовать для:

- нового product/service;
- нового AI/agent workflow;
- крупной user-facing feature;
- обязательной внешней integration;
- architecture/data migration;
- security, permission или autonomy change;
- функции с payment, PII, external mutation или большим blast radius;
- первого production launch.

### `delta`

Использовать для ограниченной задачи внутри существующего frozen contract. Указать parent version и только изменяемые блоки. Delta не может скрыть затронутую red line.

### Контракт не нужен

- чистое объяснение;
- read-only диагностика;
- documentation-only change без runtime impact;
- mechanical refactor без изменения behavior/interface/risk;
- тривиальный fix, полностью покрытый действующими acceptance gates.

Если «маленькая» задача затрагивает новую integration, migration, permission или behavior, повысить её до delta.

## 3. Заполнение

1. Извлечь цель, scope и constraints из сообщения и repository.
2. Провести read-only inspection текущего source/config/tests.
3. Разделить каждое существенное утверждение на `fact`, `assumption`, `unknown`, `not_applicable`.
4. Не считать старые docs/reports текущим evidence без проверки source/commit.
5. Поставить первым unknown, способный заблокировать весь проект.
6. Задать максимум один blocking question за раз.
7. Для `not_applicable` указать причину.
8. Выдать gate verdict, allowed scope и один следующий action.

Не заставлять пользователя заполнять анкету, если данные можно извлечь самостоятельно.

## 4. Структура

### Identity

- id/version/kind/parent/status;
- target type/name;
- project, quality и incident owners;
- created/frozen timestamps.

### Value

- consumer;
- current waste/problem;
- expected outcome;
- downstream decision/behavior;
- success criteria;
- primary metric;
- counter-metrics.

Artifact («создать экран/файл/AI-текст») не является достаточным outcome.

### Scope

- один production-ready vertical slice;
- included/excluded/non-goals;
- user journeys;
- invariants;
- assumptions и compatibility constraints.

### Architecture

- current/target state;
- system boundaries и components;
- interfaces и data ownership;
- state transitions;
- failure modes;
- migration/backfill;
- blast radius.

### Integrations

Для каждой зависимости:

- purpose/provider/environment;
- required for core path;
- credential reference;
- verification state;
- timeout/retry;
- idempotency/readback;
- fallback: `block`, `manual` или `deterministic`.

### Production

- environments/config/secrets;
- authentication/authorization/privacy;
- logs/metrics/traces и SLO;
- deploy/readback/rollback;
- incident owner и blast radius.

### AI governance

- value/model policies;
- framework decision: `none`, `Mastra` или обоснованная альтернатива;
- orchestration layers: application workflow, durable process engine и AI runtime;
- runtime/version, deployment model и production storage;
- critical decisions и autonomy levels;
- ContextPack/Rulebook/EvalSuite/AutonomyPolicy;
- EvalSuite owner/status/version/provenance, floor/ceiling, slices, per-slice thresholds, ambiguity/fallback, judge calibration, exact run config и OutcomeRecord link;
- DecisionRecord/OutcomeRecord;
- memory/freshness/stale;
- workflow durability, retries, suspend/resume и human checkpoints;
- tool schemas, permissions и mutation controls;
- manual/deterministic fallback.

### Testing harness

- применимость: workflow, multi-agent system, agent role, skill либо `not_applicable` с rationale;
- `TestSubjectManifest` и совместно утверждённый TestCase: input, acceptable terminal outcome, quality criteria и forbidden outcomes;
- minimal critical checkpoints, quality rubrics, evidence sources и human calibration policy;
- `CheckpointReview` protocol: `APPROVE`, `REJECT`, `CHANGE_CRITERION`, `ESCALATE`;
- actual subject/TestCase/config/model/tool versions/hashes;
- authenticated Designer/Runner/Recorder/Collector/Evaluator/Investigator/Repairer/Verifier/Approver;
- trusted evidence collectors и resolvable receipt formats;
- append-only journal, trace completeness и drift policy;
- atomic idempotency/outbox protocol для run changes и external mutations;
- classification: workflow/test-case/judge/data/environment/harness defect или ambiguous product decision;
- bounded autonomous repair: approved BugSpec, Red→Green proof, attempts/deadline/token/cost budgets и stop rules;
- targeted, clean-checkpoint и full-clean replay procedures, isolated namespace и side-effect policy;
- regression promotion и progressive autonomy по checkpoint/risk slice;
- acceptance/promotion/rollback policy;
- harness qualification: seeded defects, trace loss, spoofing и false-green checks.

### Delivery harness

- `KEEP_LOCAL`, `DELEGATE`, `PARALLELIZE` или `DECOMPOSE_FIRST`;
- reason;
- subagent task refs;
- non-overlapping write scopes;
- integration owner;
- context-preservation plan.

### Quality

- first Red test;
- acceptance criteria и evidence levels;
- required commands;
- regressions, security, performance и accessibility;
- zero required skip/todo;
- mock policy reference.
- TestingHarness reference и required qualification/evidence status для consequential composite behavior.

### UI

- `shadcn` либо justified `not_applicable`;
- components.json и actual CLI context;
- required primitives/docs;
- source/component/browser conformance;
- approved exceptions.

### Economics

- AI applicability;
- policy/rates/caps;
- worst-case reservation;
- usage settlement;
- cost per accepted outcome target.

### Governance

- facts/assumptions/unknowns;
- red-line checks;
- time-bounded constraints;
- implementation/release reports.

## 5. Gates

### Verdicts

| Verdict | Meaning |
|---|---|
| `READY` | Весь зафиксированный scope разрешён для соответствующего gate |
| `READY_WITH_CONSTRAINTS` | Разрешён только exact safe scope с owner, expiry и compensating controls |
| `BLOCKED` | Нельзя начинать/выпускать затронутый scope |

До реализации release имеет `evaluationStatus: pending`, а не положительный verdict.

### Lifecycle

```text
draft
  → blocked → новая draft version
  → ready/ready_with_constraints → frozen
  → stale при upstream change
  → superseded новой version
```

Frozen contract не редактировать молча. Создать новую version и пометить downstream plans/tests/artifacts stale.

### Implementation algorithm

1. Выбрать full/delta.
2. Извлечь facts/assumptions/unknowns.
3. Проверить общие и implementation red lines.
4. При failure → `BLOCKED`.
5. Проверить vertical slice и acceptance evidence plan.
6. Некритический ограниченный unknown требует owner/expiry/control → `READY_WITH_CONSTRAINTS`.
7. Без blockers/constraints → `READY`.
8. Freeze contract и подтвердить Red до production code.

### Release algorithm

1. Собрать evidence на exact commit/config.
2. Проверить общие и release red lines.
3. При failure → `BLOCKED`.
4. Проверить production path, integrations, security, cost, deploy/readback/rollback.
5. Безопасно ограниченный release → `READY_WITH_CONSTRAINTS`.
6. Весь scope доказан → `READY`.

Каждый constraint содержит exact statement, allowed scope, owner, expiry, compensating control, validation и closure criterion. Иначе это blocker.

## 6. Red lines

Любая применимая непрошедшая red line даёт `BLOCKED` соответствующего gate.

### Оба gate

1. Не определены consumer или измеримый outcome.
2. Production path содержит mock/stub/fake/hardcoded success/test-only branch.
3. Secrets хранятся в code/log или уходят неразрешённому provider.
4. Критическая assumption/unknown выдана за fact.
5. Работа требует не предоставленных пользователем полномочий.

### Implementation

6. Не определены vertical slice, boundaries или invariants.
7. Не доказана принципиальная доступность mandatory integration.
8. Не определены first Red и acceptance criteria.
9. Не определены security, permissions, observability и rollback для scope.
10. Runtime AI не имеет model/context/rule/eval/autonomy/token budget policy.
11. Consequential AI behavior не имеет EvalSuite owner, version, provenance, slices, acceptance/fallback policy или reproducible run plan.
12. Web UI не имеет actual shadcn context/conformance plan.
13. Не выбраны delivery strategy и write scopes.
14. Consequential workflow, multi-agent system, agent role или skill не имеет совместно утверждённого TestCase с input/outcome/quality criteria, critical checkpoints, human calibration, failure classification, bounded repair и full-clean replay strategy.

### Release

15. Mandatory integration не прошла required sandbox/live evidence.
16. Required test/build/lint/security/conformance содержит fail/skip/todo/warning по принятой policy.
17. External mutation не имеет idempotency/readback/rollback.
18. AI calls не имеют работающего token/cost accounting и enforcement.
19. AI decision не связан с actual context/rules/model/tool versions.
20. Required EvalSuite не прошёл blocking per-slice thresholds на exact model/context/rules/tools/judge versions либо judge не откалиброван по принятой risk policy.
21. Required TestingHarness acceptance основан на caller/subject self-attestation, spoofable identity, unresolved evidence refs, неисполненном replay или только targeted replay; failure был исправлен без classification либо сам harness не прошёл qualification.
22. Autonomy превышает доказанный и утверждённый уровень.
23. Web UI не прошло required shadcn/browser conformance.
24. Production readiness основана только на source/unit/mock/replay/offline score.
25. Deploy/readback/rollback не воспроизводимы.
26. Release decision выдан за реальный OutcomeRecord до observation window либо idempotency допускает duplicate/orphan consequential mutation после crash.

## 7. Evidence levels

| Level | Доказывает | Не доказывает |
|---|---|---|
| `source_inspection` | structure/config/code presence | runtime behavior |
| `unit` | isolated logic | integration/user journey |
| `component` | component on controlled boundaries | full production flow |
| `contract` | schema/interface compatibility | real provider availability |
| `integration_sandbox` | real test environment connection | production outcome |
| `e2e_live` | full live-like mandatory path | long-term business outcome |
| `production_observation` | real outcome/load/downstream effects | causality without attribution review |

Каждый acceptance criterion указывает required level, procedure/command и blocking flag.

## 8. Human-readable template

```markdown
# Project Contract: <name> v<version>

## Implementation gate
READY | READY_WITH_CONSTRAINTS | BLOCKED
Reason / allowed scope / next action:

## Release gate
PENDING | READY | READY_WITH_CONSTRAINTS | BLOCKED
Reason / evidence / next action:

## Value
Consumer:
Current waste:
Expected outcome:
Primary metric:
Counter-metrics:

## Scope
Production-ready vertical slice:
Included:
Excluded / non-goals:
Invariants:

## Facts / assumptions / unknowns
Facts + evidence:
Assumptions + validation:
Unknowns + owner/date:

## Architecture and integrations
Boundaries/components/data/state:
Real integrations/fallbacks:
Failure modes/migration:

## Production
Security/permissions/secrets/privacy:
Observability/SLO:
Deploy/readback/rollback/blast radius:

## AI and tokenomics
Framework/runtime decision and rationale:
Orchestration layers and ownership:
Model/context/rules/evals/autonomy:
EvalSuite lifecycle/status/version/owner/provenance:
Floor/ceiling/slices/thresholds/ambiguity/fallback:
Judge calibration/run config/regression/OutcomeRecord link:
Memory/storage/durability/tool permissions:
Budgets/reservation/settlement:
Fallback:

## Delivery harness
KEEP_LOCAL | DELEGATE | PARALLELIZE | DECOMPOSE_FIRST
Task contracts/write scopes/integration owner:

## Testing harness
Subject type/id/version/hash and actual contract ref:
TestCase input/terminal outcome/quality criteria/forbidden outcomes:
Critical checkpoints/rubrics/evidence/human calibration:
CheckpointReview protocol:
Authenticated roles and separation of duties:
Trusted collectors/evidence receipts/journal:
Failure classification:
Bounded BugSpec → Red/Green → targeted replay:
Clean checkpoint/full clean replay:
Regression promotion/progressive autonomy:
Acceptance/promotion/rollback policy:
Harness qualification/seeded faults/known gaps:

## TDD and evidence
First Red:
Acceptance criteria:
Release commands:

## UI
Actual shadcn context/docs/conformance/exceptions:

## Red-line report
Passed:
Blocked:
Constraints:
```

## 9. Self-check

1. Outcome, а не artifact?
2. Один маленький, но полный production slice?
3. Facts/assumptions/unknowns различимы?
4. Самый опасный unknown первый?
5. Integrations реальные?
6. Mock/replay не выдан за live?
7. First Red и evidence levels названы?
8. Security/observability/deploy/rollback определены?
9. Потребность в agent framework и выбор Mastra/альтернативы обоснованы?
10. AI governance и token budgets есть?
11. EvalSuite имеет owner/version/provenance/slices/thresholds/calibration/fallback и online outcome link?
12. Consequential workflow/agent/role/skill имеет совместно утверждённый TestCase, critical checkpoints, CheckpointReview, classification и bounded autonomous repair?
13. Actual hashes/roles/receipts закреплены, а full clean replay и harness qualification выполнены?
14. Actual shadcn context получен?
15. Delivery strategy рациональна?
16. Implementation readiness не выдана за release?
17. Constraint не скрывает red-line failure?
18. Следующий шаг конкретен и проверяем?
