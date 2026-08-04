# AI systems: models, context, tools и agents

## Содержание

1. Когда использовать AI
2. AI decision boundary
3. Model и provider policy
4. Prompt и structured output
5. ContextPack и Rulebook
6. Retrieval и memory
7. Tools и permissions
8. Workflow, agent и multi-agent
9. Framework decision
10. Durability и state
11. Evals и TestingHarness
12. Tokenomics
13. Observability и records
14. Fallback и failure semantics
15. ProjectContract fields
16. Антипаттерны
17. Self-check

## 1. Когда использовать AI

Сначала проверить, даёт ли AI измеримую пользу. Не использовать model call для поведения, которое проще, дешевле и надёжнее выразить deterministic code, query, rules или обычным UI.

AI уместен, когда задача содержит open-ended interpretation, generation, ranking, extraction или выбор, а acceptable behavior можно ограничить contract/evals/fallback.

Зафиксировать:

- consumer и downstream decision;
- current way/waste;
- expected improvement;
- AI-specific risk;
- deterministic alternative;
- cost per accepted outcome.

## 2. AI decision boundary

Разложить product path:

```text
deterministic input validation
  → bounded AI decision
  → deterministic output validation
  → policy/approval
  → optional external action
  → readback/outcome
```

Не позволять prompt владеть business invariants, permissions, billing, retries или irreversible side effects.

Для каждого AI decision определить:

- exact input/output schema;
- allowed alternatives;
- required facts и missing-data behavior;
- ambiguity/abstention/fallback;
- autonomy level;
- downstream action и blast radius;
- EvalSuite owner.

## 3. Model и provider policy

Выбирать модель по capability, latency, privacy, reliability и total workflow cost, а не по привычке.

Сохранять:

- provider/model/version or snapshot;
- parameters и structured-output mode;
- data residency/privacy constraints;
- retry/fallback routing;
- rate/concurrency limits;
- billing policy;
- evaluation baseline.

Не угадывать model IDs и API. Проверять installed SDK/types/embedded docs, затем актуальную официальную документацию.

Model fallback не должен молча менять quality, data policy или tool permissions. Он получает собственные eval evidence и versioned route policy.

## 4. Prompt и structured output

Prompt является versioned executable policy, но не единственным control layer.

Хороший prompt определяет:

- одну ясную роль/capability;
- allowed context и source priorities;
- observable output contract;
- unknown/ambiguity behavior;
- tool-use boundaries;
- forbidden claims/actions;
- concise examples только там, где они различают поведение.

Предпочитать typed structured output для machine-consumed decisions. Валидировать schema и business invariants после model response.

Не хранить secrets, rapidly changing rules или весь knowledge base внутри prompt. Не просить модель «быть осторожной» вместо permission boundary.

## 5. ContextPack и Rulebook

### ContextPack

Versioned вход для конкретного decision:

- source/provenance;
- captured/effective timestamps;
- authorization/data class;
- relevance/freshness;
- missing/contradictory facts;
- size/token budget;
- dependent artifact versions.

### Rulebook

Deterministic policy:

- rule IDs и owners;
- effective dates/version;
- priority/conflict resolution;
- exceptions;
- change process;
- machine-checkable invariants.

Retrieval не делает информацию истинной. Каждый item проходит permission, relevance, freshness и provenance checks.

## 6. Retrieval и memory

Разделять:

- current run/working state;
- conversation history;
- durable user/entity facts;
- domain knowledge/index;
- rules/policies;
- decisions;
- observed outcomes.

Для каждого store определить owner, source of truth, tenant boundary, write authority, freshness, retention, deletion и stale propagation.

Не сохранять chain-of-thought. Сохранять user-provided facts, verified observations, decisions/actions и evidence.

RAG/retrieval проверять отдельно по:

- indexing coverage;
- retrieval relevance/recall;
- source attribution;
- stale/duplicate/conflicting content;
- access control;
- answer grounding и abstention.

## 7. Tools и permissions

Каждый tool имеет:

- одну responsibility;
- typed input/output;
- least-privilege credential/capability;
- server-side authorization;
- timeout/cancellation;
- bounded retries;
- audit receipt;
- explicit error semantics.

Mutating tool дополнительно требует exact target, idempotency, approval по risk class, pre/post state, readback и rollback/compensation.

Tool output считается untrusted input до validation. Не позволять retrieved content или prompt injection повышать permissions.

## 8. Workflow, agent и multi-agent

### Workflow

Использовать для известного порядка, branching rules, retries, approvals, compensation и state invariants.

### Agent

Использовать для bounded open-ended выбора. Ограничить tools, attempts, deadline, tokens/cost и stop conditions.

### Multi-agent

Не использовать по умолчанию. Добавлять specialist role, если доказана хотя бы одна причина:

- разные permissions/security domains;
- независимые context packs;
- параллельные bounded tasks;
- разные eval ownership;
- single-agent context/quality/cost ceiling.

Каждый handoff содержит owner, schema, context refs, provenance, budget, deadline, acknowledgement и failure behavior. Delegation не повышает privileges.

## 9. Framework decision

### `none`

Предпочитать provider SDK + typed application code для одного-двух bounded calls без durable workflow, memory и dynamic tool loop.

### Mastra

Для TypeScript/Node.js первой оценивать Mastra, если нужны agents, explicit workflows, tools, memory/storage, suspend/resume, multi-agent composition и observability. Это preferred default, не обязательная зависимость.

При реализации Mastra:

1. Проверить installed `@mastra/*` packages.
2. Читать embedded docs/types exact version.
3. При отсутствии packages использовать актуальные official docs.
4. Применить доступный `mastra` skill.
5. Не писать API/model IDs по памяти.

### Alternatives

Оценивать по exact critical path:

- explicit graph/checkpoint semantics;
- Python ecosystem;
- lightweight provider-centric agents;
- long-running durable business process;
- existing team/runtime constraints.

Durable process engine и AI runtime могут быть разными слоями. Framework primitive не доказывает production recovery, auth, privacy или governance.

## 10. Durability и state

Для long-running AI process определить:

- state owner и persistence;
- checkpoint/resume semantics;
- restart recovery;
- event/version history;
- retry/deadline/cancellation;
- concurrency и duplicate delivery;
- exactly-once business effect через idempotency;
- policy/context compatibility on resume;
- partial success и compensation.

Если AI framework не доказывает required durability, использовать отдельный process engine либо application state machine. Не имитировать recovery дополнительными prompts.

## 11. Evals и TestingHarness

Для consequential probabilistic behavior создать versioned EvalSuite с cases, slices, provenance, calibrated judge, risk-based gates и fallback. Не использовать LLM judge для deterministic assertions.

Для первого нового/изменённого workflow использовать TestingHarness, когда нужно совместно откалибровать checkpoints, автономно классифицировать/исправлять defects и выполнить trusted replay.

Offline eval/replay не доказывает production outcome. Связать accepted decisions с OutcomeRecord после observation window.

## 12. Tokenomics

### До call

- input upper bound;
- max output;
- worst-case cost;
- per-call/run/user/day/month caps по применимости;
- atomic reservation;
- attempt budget/deadline.

Если cap/policy неизвестен или превышен, блокировать paid fetch либо использовать заранее утверждённый fallback.

### После call

- provider-reported input/output/cached tokens;
- actual или conservative estimated cost;
- provider/model/policy attribution;
- workflow/run/step/attempt IDs;
- success/failure/timeout;
- accepted/rejected outcome.

Неизвестная стоимость не равна нулю. Оптимизировать total `cost_per_accepted_outcome`, включая retries, judge calls, human work и downstream rework.

## 13. Observability и records

Сохранять:

- model/context/rule/tool/prompt versions;
- request/run/decision IDs;
- state transitions и tool receipts;
- latency/retries/token/cost;
- fallback/abstention/human intervention;
- mutation/readback/rollback;
- EvalSuite/TestCase refs;
- pending OutcomeRecord window.

`DecisionRecord` хранит выбранную альтернативу, inputs/versions, evidence, confidence, autonomy и actor. `OutcomeRecord` позже хранит фактический downstream result и attribution limits.

## 14. Fallback и failure semantics

Выбирать явное действие:

- deterministic fallback;
- clarify;
- abstain;
- human review;
- retry within budget;
- queue/resume;
- block.

Не превращать timeout, malformed output, missing source или provider outage в fabricated success. Не делать бесконечный agent loop.

## 15. ProjectContract fields

Зафиксировать по применимости:

- AI necessity and deterministic alternative;
- decision boundaries/autonomy;
- model/provider/version/fallback;
- ContextPack/Rulebook;
- prompt/output schemas;
- retrieval/memory ownership;
- tool permissions/mutations;
- workflow/agent/multi-agent topology;
- framework/durability decision;
- EvalSuite/TestingHarness refs;
- token/cost policy;
- observability/DecisionRecord/OutcomeRecord;
- upgrade/rollback policy.

## 16. Антипаттерны

- Добавлять AI/framework потому, что проект «AI-first».
- Прятать business process в prompt.
- Давать agent прямой unrestricted доступ к database/API.
- Считать conversation history durable memory.
- Использовать multi-agent вместо ясной decomposition.
- Увеличивать retries вместо исправления context/schema/tool.
- Считать framework tracing достаточной product observability.
- Выбирать model по benchmark без representative EvalSuite.
- Экономить tokens ценой missing evidence или повторной работы.
- Считать AI self-verdict acceptance evidence.

## 17. Self-check

1. AI действительно нужен?
2. Decision boundary мала и наблюдаема?
3. Deterministic rules/validation находятся вне prompt?
4. Model/provider/version/fallback проверены?
5. Context/rules/retrieval имеют provenance/freshness/permissions?
6. Memory stores разделены по responsibility?
7. Tools typed и least privilege?
8. Workflow/agent/multi-agent выбран по необходимости?
9. Framework decision и durability доказуемы?
10. EvalSuite/TestingHarness применены по типу риска?
11. Token/cost reservation и settlement работают?
12. Failures ведут к explicit fallback, а не fabricated success?
13. Decision и Outcome разделены?
14. Upgrade/rollback path существует?
