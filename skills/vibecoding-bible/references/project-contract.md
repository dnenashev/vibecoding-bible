# VibecodingProjectContract

## Содержание

1. Назначение
2. Режим и глубина контракта
3. Как заполнять
4. Обязательное ядро
5. Расширения standard и critical
6. Implementation и release gates
7. Red lines
8. Evidence levels
9. Templates
10. Self-check

## 1. Назначение

`VibecodingProjectContract` связывает намерение пользователя, изменения в системе и доказательство результата. Он нужен не для отчётности, а чтобы до кода ответить:

1. Какой outcome должен измениться?
2. Что входит и не входит в текущий slice?
3. Что нельзя сломать?
4. Как доказать результат и безопасно откатиться?

Контракт содержит два независимых verdict:

- `implementation gate` — можно ли начинать изменение;
- `release gate` — доказано ли, что exact candidate готов к выбранной среде.

Ожидаемый failing Red совместим с implementation readiness, но блокирует release, пока не станет Green.

## 2. Режим и глубина контракта

Сначала выбрать operating mode.

### `EXPLORE`

Для reversible spike без production claim. Использовать короткий experiment contract:

- unknown/hypothesis;
- time/cost box;
- test fixture и safety boundary;
- success/failure signal;
- `discard | continue | promote` decision.

Exploration artifact нельзя подключать к production path без нового `BUILD` contract.

### `BUILD`

Default для реального продукта или функции. Выбрать глубину:

- `lite` — bounded low-risk change в существующей системе;
- `standard` — новый product/feature/integration или заметное изменение behavior;
- `full` — новая система, migration или широкий cross-cutting change.

### `CRITICAL`

Для payments, PII, regulated data, high autonomy, irreversible mutation или большого blast radius. Использовать `critical` contract с усиленными threat/evidence/approval/recovery полями.

### Когда контракт не нужен

- чистое объяснение;
- read-only diagnosis;
- mechanical refactor без behavior/interface/risk change;
- documentation-only change без runtime impact;
- тривиальная правка, полностью покрытая действующими gates.

Если маленькая задача затрагивает integration, schema, permission, user-visible behavior или release — использовать минимум `lite` delta.

## 3. Как заполнять

1. Извлечь данные из сообщения, repository и runtime; не выдавать пользователю пустую форму.
2. Разделить существенные claims на `fact`, `assumption`, `unknown`, `not_applicable`.
3. Поставить первым unknown, способный обрушить outcome.
4. Указать parent contract/version для delta.
5. Заполнить только применимые расширения.
6. Для `not_applicable` дать короткую причину.
7. Выдать verdict, allowed scope и один next action.

Не считать README, старый report или proposed architecture текущим evidence без проверки actual source/config.

## 4. Обязательное ядро

Применять к `lite`, `standard`, `full` и `critical`.

### Identity

- id/version/mode/depth/parent/status;
- target type/name;
- owner;
- exact code/config baseline;
- created/frozen timestamps.

### Outcome

- consumer;
- problem/current way;
- expected observable outcome;
- primary success signal;
- counter-signal, который не должен ухудшиться.

Artifact вроде «создать экран» или «написать AI-текст» не является достаточным outcome без user/downstream effect.

### Scope

- included behavior;
- excluded/non-goals;
- affected user journey;
- invariants;
- compatibility constraints;
- exact write/blast-radius boundary.

### Reality

- facts + source evidence;
- assumptions + validation;
- unknowns + owner/next probe;
- dirty worktree/current failures;
- relevant versions/dependencies.

### Change

- current → target behavior;
- affected components/interfaces/data;
- first Red;
- Regression Registry path/version и applicable entry IDs;
- minimal implementation slice;
- required commands/procedures.

### Safety and acceptance

- permissions/secrets/privacy impact;
- failure and rollback/compensation;
- acceptance criteria + required evidence level;
- implementation verdict;
- release status/verdict.

## 5. Расширения standard и critical

Заполнять по применимости, а не механически.

### Product and experience

- target user/segment;
- journey and requirements;
- content/interaction states;
- accessibility/platform constraints;
- analytics/feedback signal.

### Architecture and data

- system boundaries и ownership;
- stack decision и rationale;
- domain/data model;
- API/integration contracts;
- migration/backfill/compatibility;
- concurrency/cache/state policy;
- relevant ADRs.

### Production

- environments/config/secrets;
- authentication/authorization/tenancy;
- threat model/privacy/retention;
- performance/capacity/reliability;
- observability/SLO;
- CI/CD/feature flag/canary;
- deploy/readback/rollback;
- backup/recovery/incident owner.

### AI systems

- зачем AI и где deterministic code лучше;
- model/provider/version и fallback;
- ContextPack/Rulebook/AutonomyPolicy;
- prompt/structured output/tool contracts;
- memory/RAG provenance/freshness;
- framework decision: `none`, `Mastra` или justified alternative;
- token/cost reservation, settlement и caps;
- DecisionRecord/OutcomeRecord;
- EvalSuite reference для consequential probabilistic behavior.

### TestingHarness

Для первого/изменённого сложного workflow:

- subject/TestCase versions;
- input/terminal outcome/quality criteria;
- critical checkpoints и human calibration;
- trusted evidence sources;
- role separation;
- failure classification;
- bounded BugSpec/repair budgets;
- replay scope, affected downstream path и правила переиспользования trusted upstream evidence;
- qualification/promotion policy.

### Delivery harness

- `KEEP_LOCAL | DELEGATE | PARALLELIZE | DECOMPOSE_FIRST`;
- context-preservation reason;
- task/write scopes;
- integration owner;
- immutable candidate, QA и exact ACCEPT policy для bug release;
- shared gates.

### CRITICAL additions

- abuse/misuse cases;
- data classification and legal/compliance owner;
- explicit actor/capability matrix;
- independent approval requirements;
- sandbox/canary/blast-radius limits;
- failure injection and recovery evidence;
- incident/kill-switch path;
- stronger live evidence and observation window.

## 6. Implementation и release gates

### Verdicts

| Verdict | Meaning |
|---|---|
| `READY` | Весь stated scope разрешён |
| `READY_WITH_CONSTRAINTS` | Разрешён только exact safe scope с owner, expiry и control |
| `BLOCKED` | Нельзя начинать или выпускать затронутый scope |

До реализации release status всегда `PENDING`.

### Implementation algorithm

1. Выбрать mode/depth.
2. Проверить mandatory core и применимые red lines.
3. Проверить feasibility mandatory integrations.
4. Зафиксировать first Red и evidence plan.
5. Проверить permissions, blast radius и rollback.
6. Выдать `BLOCKED`, если применима red line.
7. Иначе `READY_WITH_CONSTRAINTS` или `READY`.
8. Freeze version до production code.

### Release algorithm

1. Привязать evidence к exact candidate/config/environment.
2. Проверить required commands, applicable Registry entries и evidence levels.
3. Проверить security/data/operational impact по risk mode.
4. Проверить migrations/integrations/deploy/readback/rollback.
5. Проверить unresolved failures, skip/todo и constraints.
6. Выдать отдельный release verdict.

Constraint обязан содержать exact scope, owner, expiry, compensating control, validation и closure criterion. Иначе это blocker.

## 7. Red lines

Любая применимая непрошедшая red line даёт `BLOCKED` соответствующего gate.

### Оба gate

1. Не определены consumer/outcome или safe scope.
2. Production path содержит mock/fake/hardcoded success/placeholder core behavior.
3. Secret/PII уходит в code, log или неразрешённый provider.
4. Critical unknown выдан за fact.
5. Требуются не предоставленные authority/credentials/external writes.
6. `EXPLORE` artifact пытаются выпустить без BUILD promotion.

### Implementation

7. Не определены boundaries, invariants или first Red.
8. Не доказана принципиальная доступность mandatory integration.
9. Security/permissions/data/rollback impact не оценён по риску.
10. New schema/API не имеет migration/compatibility plan.
11. Consequential AI behavior не имеет model/context/tool/budget/fallback/eval policy.
12. Первый сложный workflow не имеет TestCase/checkpoint/replay plan.
13. Не определены write scope и delivery owner.

### Release

14. Required build/test/lint/type/security/accessibility/performance check падает либо required test skipped/todo.
15. Применимый active blocking Registry entry не выбран, failed, skipped или не имеет fresh evidence.
16. Mandatory integration не прошла required sandbox/live evidence.
17. External mutation не имеет idempotency/readback/rollback/compensation.
18. Authentication/authorization/tenant isolation не доказаны для affected path.
19. Migration/backup/recovery не проверены на требуемом уровне.
20. AI EvalSuite blocking slice не прошёл либо judge не откалиброван.
21. TestingHarness опирается на self-attestation, unexecuted replay или unresolved evidence.
22. Autonomy превышает утверждённый уровень.
23. Token/cost caps или usage accounting отсутствуют для paid AI path.
24. Production readiness основана только на source/unit/mock/offline result.
25. Deploy/readback/rollback не воспроизводимы.
26. Critical/high issue или expired constraint остаётся открытым.
27. Release decision выдан за реальный OutcomeRecord до observation window.

## 8. Evidence levels

| Level | Доказывает | Не доказывает |
|---|---|---|
| `source` | code/config/artifact presence | runtime behavior |
| `static` | types/lint/schema/static policy | execution path |
| `unit` | isolated logic | integration/user journey |
| `component` | bounded component behavior | full system |
| `contract` | interface compatibility | provider availability |
| `integration` | реальные boundaries в test environment | end-to-end outcome |
| `e2e` | полный representative path | долгосрочную reliability |
| `live_observation` | production behavior/outcome | causality без review |

Каждый blocking criterion указывает required level и exact command/procedure.

## 9. Templates

### Lite delta

```markdown
# Contract: <change> v<version>
Mode/depth: BUILD/lite
Parent/baseline:

Outcome:
Included / excluded:
Invariants:
Facts / assumptions / critical unknown:
Current → target behavior:
First Red:
Regression Registry / selected IDs:
Required evidence:
Permissions / rollback:
Implementation verdict:
Release status/verdict:
```

### Standard/full/critical

```markdown
# Project Contract: <name> v<version>
Mode/depth/status/parent:
Owners/baseline:

## Outcome and scope
Consumer/problem/current way/outcome:
Primary/counter-signals:
Included/excluded/journey/invariants:

## Reality
Facts + evidence:
Assumptions + validation:
Unknowns + owner/probe:

## Design
Requirements/experience:
Architecture/data/APIs/integrations:
Failure/migration/compatibility:

## Build and verify
Change slices/write scopes:
First Red/test strategy/evidence:
Regression Registry path/version/selected IDs:
Delivery harness:

## Production
Security/privacy/data:
Performance/reliability/observability:
CI-CD/deploy/readback/rollback/recovery:

## AI / TestingHarness
AI policy/evals/tokenomics:
TestCase/checkpoints/replay:

## Gates
Implementation verdict:
Release status/verdict:
Constraints/red lines:
```

## 10. Self-check

1. Mode/depth соответствует риску?
2. Контракт помогает принять решение, а не добавляет форму?
3. Outcome наблюдаем и связан с consumer?
4. Scope мал, но полон внутри границы?
5. Facts/assumptions/unknowns разделены?
6. First Red и required evidence названы?
7. Architecture/data/API changes совместимы?
8. Security/production поля заполнены только по применимости, но red lines не пропущены?
9. AI/eval/harness добавлены только когда нужны?
10. EXPLORE не выдан за production?
11. Implementation и release verdicts разделены?
12. Regression Registry применён без запуска лишних tests?
13. Пользователю понятен один следующий action?
