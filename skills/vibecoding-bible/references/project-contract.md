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

## 2. Режим, риск и глубина контракта

Сначала выбрать delivery mode и risk — это независимые оси. Затем вывести глубину контракта.

### Mode `EXPLORE`

Для reversible spike без production claim. Использовать короткий experiment contract:

- unknown/hypothesis;
- time/cost box;
- test fixture и safety boundary;
- success/failure signal;
- `discard | continue | promote` decision.

Exploration artifact нельзя подключать к production path без нового `BUILD` contract.

### Mode `BUILD`

Default для реального продукта или функции. Выбрать глубину по risk и размеру scope:

- `lite` — bounded change при risk `LOW`;
- `standard` — новый product/feature/integration или заметное изменение behavior при risk `STANDARD`;
- `full` — новая система, migration или широкий cross-cutting change.

### Risk `CRITICAL`

Для payments, PII, regulated data, high autonomy, irreversible mutation или большого blast radius. Использовать `critical` contract с усиленными threat/evidence/approval/recovery полями — независимо от того, `EXPLORE` это или `BUILD`. Для `EXPLORE + CRITICAL` контракт остаётся коротким, но обязан содержать изоляцию, запрет production-записи и правило удаления данных.

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

### Agent Execution Harness

Для длительной, возобновляемой или consequential работы над coding-agent:

- `existing | build | manual_fallback` decision и rationale;
- WorkflowDefinition/StageContract versions;
- session/revision/subject identity и host/project bindings;
- HostAdapter/ProjectAdapter capabilities и least privilege;
- evidence/approval trust boundaries;
- budgets, stale/rebind/recovery/replay policy;
- conformance/fault qualification.

### Delivery harness

- `KEEP_LOCAL | DELEGATE | PARALLELIZE | DECOMPOSE_FIRST`;
- context-preservation reason;
- task/write scopes;
- integration owner;
- delivery lane: `READY_FOR_BATCH | URGENT_HOTFIX`, release trigger и maximum wait;
- release intent manifest, accepted handoffs/capabilities и composition owner;
- provenance, capability evidence и QA coverage policy;
- immutable candidate, QA и exact ACCEPT policy для bug release;
- shared gates.

### Risk CRITICAL additions

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

Эта таблица описывает `implementation_verdict`. Release ведётся отдельным словарём
`release_state`: `PENDING | CANDIDATE | ACCEPTED | RELEASED | BLOCKED`. До появления
evidence кандидата release_state равен `PENDING`. Канонические определения обоих
словарей — в [`vocabulary.md`](vocabulary.md); здесь их не переопределять.

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
2. Freeze release intent и классифицировать каждый handoff как `INTEGRATED | DEFERRED | SUPERSEDED | MISSING`.
3. Блокировать `MISSING`; проверить provenance и behavioral capability exact candidate.
4. Для batch freeze manifests и пересчитать aggregate impact финального cumulative candidate.
5. Построить QA coverage matrix из acceptance criteria release intent.
6. Проверить required commands, applicable Registry entries и evidence levels.
7. Проверить security/data/operational impact по risk mode.
8. Проверить migrations/integrations/deploy/readback/rollback.
9. Проверить unresolved failures, skip/todo и constraints.
10. Выдать `release_state` и, если он не `RELEASED`, назвать blocker или недостающее evidence.

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
14. Выбранный Agent Execution Harness хранит state только в chat, позволяет self-approval или не имеет stale/rebind policy.

### Release

15. Required build/test/lint/type/security/accessibility/performance check падает либо required test skipped/todo.
16. Применимый active blocking Registry entry не выбран, failed, skipped или не имеет fresh evidence.
17. Mandatory integration не прошла required sandbox/live evidence.
18. External mutation не имеет idempotency/readback/rollback/compensation.
19. Authentication/authorization/tenant isolation не доказаны для affected path.
20. Migration/backup/recovery не проверены на требуемом уровне.
21. AI EvalSuite blocking slice не прошёл либо judge не откалиброван.
22. TestingHarness опирается на self-attestation, unexecuted replay или unresolved evidence.
23. Autonomy превышает утверждённый уровень.
24. Token/cost caps или usage accounting отсутствуют для paid AI path.
25. Production readiness основана только на source/unit/mock/offline result.
26. Deploy/readback/rollback не воспроизводимы.
27. Critical/high issue или expired constraint остаётся открытым.
28. Release decision выдан за реальный OutcomeRecord до observation window.
29. Принятый handoff отсутствует в cumulative candidate и не имеет explicit defer/supersede decision.
30. Candidate provenance или behavioral capability coverage не доказаны для release intent.
31. QA coverage выбрана произвольно и не покрывает user-visible acceptance criteria batch.

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
Release intent/composition/QA coverage:
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
Release intent/composition receipt/QA coverage:

## Production
Security/privacy/data:
Performance/reliability/observability:
CI-CD/deploy/readback/rollback/recovery:

## AI / TestingHarness
AI policy/evals/tokenomics:
TestCase/checkpoints/replay:
Agent Execution Harness/workflow/adapters/state:

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
13. Delivery lane, batch trigger и urgent hotfix criteria определены по применимости?
14. Release intent reconciled с provenance, capability evidence и QA coverage?
15. Agent Execution Harness применён только по необходимости и остаётся portable?
16. Пользователю понятен один следующий action?
