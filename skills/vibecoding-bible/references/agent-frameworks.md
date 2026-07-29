# Agent frameworks: правило выбора

## Содержание

1. Канонический verdict
2. Нужен ли framework
3. Почему Mastra — рекомендуемый default
4. Матрица альтернатив
5. Архитектурные правила
6. Протокол внедрения Mastra
7. Поля ProjectContract
8. Антипаттерны
9. Актуальность документации
10. Self-check

## 1. Канонический verdict

Если продукту нужен application-level runtime для AI agents, workflows, memory, tools и multi-agent orchestration, для TypeScript/Node.js первой оценивать **Mastra**.

Это:

- рекомендуемый default, а не обязательная зависимость;
- стартовая гипотеза, а не замена architecture decision;
- способ не собирать общий runtime вручную, а не разрешение делегировать framework бизнес-инварианты и governance.

Выбор должен быть записан как `none`, `Mastra` или именованная альтернатива с evidence-based rationale. Язык проекта, существующий stack, durability, deployment и операционные требования сильнее личного предпочтения.

Не считать выбор одним взаимоисключающим названием. Durable process engine, AI runtime и application/domain layer могут быть разными слоями — например, Temporal для долгоживущего business process и Mastra для agents, tools и AI observability.

## 2. Нужен ли framework

### Выбирать `none`

Не добавлять agent framework, если одновременно верно следующее:

- есть один-два bounded model calls;
- flow детерминирован обычным application code;
- не нужны persistent memory, checkpoint/resume или long-running execution;
- нет multi-agent coordination и динамического tool loop;
- provider SDK, typed schemas и существующая observability закрывают production path.

В этом случае framework увеличит dependency surface и cognitive load без достаточной ценности.

### Оценивать agent framework

Framework оправдан, если применимы несколько условий:

- agent выбирает tools или следующий шаг динамически;
- workflow многошаговый, ветвящийся, долгий либо должен suspend/resume;
- нужны durable state, memory и recovery после process failure;
- участвуют несколько специализированных agents;
- нужен human-in-the-loop;
- требуются единые tracing, evals, model routing и operational controls;
- одинаковые orchestration primitives используются в нескольких product flows.

### Decision tree

```text
Только bounded AI calls?
  ├─ да → provider SDK + typed application code
  └─ нет → процесс длится часы/дни, ждёт signals или обязан переживать сбои?
           ├─ да → сначала оценить durable process engine; затем AI runtime
           └─ нет → нужен integrated agent runtime?
                    ├─ TypeScript/Node → сначала оценить Mastra
                    ├─ Python → сравнить Agno, CrewAI и LangGraph
                    └─ graph/checkpoint semantics доминируют → оценить LangGraph
```

## 3. Почему Mastra — рекомендуемый default

Mastra объединяет в одном TypeScript-oriented framework основные primitives, которые обычно приходится интегрировать отдельно:

- agents для open-ended решений и tool use;
- typed tools и MCP integration;
- explicit workflows для последовательностей, ветвлений и параллельных шагов;
- suspend/resume и persisted workflow state;
- memory и storage;
- multi-agent composition;
- evals, tracing/observability и локальный Studio;
- model-provider abstraction.

Это делает Mastra сильным baseline для новых TypeScript AI-приложений и сервисов. Но наличие primitive в framework ещё не доказывает его production readiness в конкретном проекте.

Mastra не снимает ответственность за:

- authentication, authorization и tenant isolation;
- data classification, retention и privacy;
- бизнес-инварианты и idempotency внешних мутаций;
- token/cost reservation, settlement и caps;
- ContextPack, Rulebook, EvalSuite и AutonomyPolicy;
- deployment, SLO, incident response, readback и rollback;
- regression, integration и live evidence.

## 4. Матрица альтернатив

| Кандидат | Когда предпочесть | Главный trade-off |
|---|---|---|
| **Mastra** | TypeScript/Node; нужен единый stack agents + workflows + memory/storage + tools + observability | Более крупная abstraction surface, чем у provider SDK; exact API зависит от установленной версии |
| **LangGraph** | Нужны явный state graph, checkpoints, interrupts, replay/time travel, сложные циклы и полный контроль над orchestration | Больше graph/state-machine проектирования и integration work |
| **Agno** | Python; нужен интегрированный runtime для agents, teams, workflows, memory, knowledge и tools | Python-first ecosystem и собственные abstractions/runtime |
| **CrewAI** | Python; domain удобно выражается ролями, crews/tasks и event-driven flows | Role-based модель может маскировать workflow invariants, если использовать crew там, где нужен deterministic flow |
| **OpenAI Agents SDK** | Нужен лёгкий provider-centric SDK: tools, handoffs/agents-as-tools, sessions, guardrails и tracing без большого framework | Не считать автоматической заменой полноценного durable workflow engine и независимого governance layer |
| **Temporal + AI runtime** | Business process длится долго, ждёт внешних signals, содержит материальные side effects и должен восстанавливаться после инфраструктурных сбоев | Temporal — process engine, не agent framework; добавляет отдельную operational surface и требует deterministic workflow/activity boundary |
| **Без framework** | Небольшой детерминированный AI path без durable orchestration | Общие primitives придётся добавить позже, если сложность действительно появится |

Не выбирать по числу логотипов или feature checklist. Проверить конкретный critical path на версии, которую реально будет использовать проект.

## 5. Архитектурные правила

### Workflow и agent — разные инструменты

- **Workflow** использовать для известной последовательности, branching rules, retries, approvals, compensation и business invariants.
- **Agent** использовать для open-ended выбора, где допустимое пространство действий ограничено tools, policy и evals.
- Не превращать детерминированный шаг в agent только ради «агентности».
- Не прятать обязательный порядок операций в prompt.

### Multi-agent не является default

Начинать с одного agent. Добавлять specialist agent, только если есть измеримая причина:

- разные tools/permissions или security domains;
- независимые context packs;
- параллелизуемые bounded задачи;
- отдельные evals и ownership;
- один agent стабильно превышает context/quality/cost limits.

Каждый handoff определяет owner результата, передаваемый контекст, output schema, budget, deadline, stop condition и failure behavior.

### Memory — не база истины

Разделять:

- run/working state;
- conversation history;
- durable user/entity facts;
- domain knowledge;
- rules/policies;
- decision и outcome records.

Для каждого store определить owner, tenant boundary, provenance, timestamps, freshness, retention, deletion, authorization и stale propagation. Retrieval проходит relevance, freshness и permission checks.

### Tools — permission boundary

Каждый tool имеет typed input/output, least privilege, timeout, bounded retries и audit event. Мутирующий tool дополнительно требует idempotency key, risk-based approval, post-action readback и rollback/compensation.

### Durability и failure semantics

Для production workflow явно проверить:

- что и когда checkpoint'ится;
- переживает ли run process restart;
- как обеспечены idempotency и exactly-once business effect;
- как работают retry, deadline, cancellation и concurrency;
- как resume связывается с той же versioned policy/context;
- что происходит при частичном успехе;
- как оператор видит, повторяет и откатывает run.

Если native workflow runtime не доказывает требуемую crash recovery, event history, timers/signals, versioning или многодневное исполнение, не имитировать эти гарантии дополнительными prompts и retries. Оценить отдельный durable engine. В такой композиции engine владеет порядком, ожиданием, retry/timeout и business state; LLM, Mastra agents и внешние tools выполняются как activities/steps за детерминированной границей.

На момент обновления этого канона Mastra имеет официальную Temporal integration, но `@mastra/temporal` помечена experimental. Проверять статус и exact API по установленной версии; для critical path требовать recovery spike и не связывать архитектуру с experimental adapter без явного constraint и rollback path.

## 6. Протокол внедрения Mastra

1. Зафиксировать use-case и доказать, что `none` недостаточно.
2. Проверить runtime/language/deployment compatibility.
3. Проверить exact installed Mastra version и читать её embedded docs/types; при отсутствии установки — текущую официальную документацию.
4. Разложить процесс: deterministic steps → workflow; open-ended decisions → agents; side effects → typed tools.
5. Выбрать production storage. Не хранить required state только в памяти процесса или `/tmp`.
6. Спроектировать memory ownership, freshness, tenant isolation и retention.
7. Добавить suspend/resume и human checkpoint там, где этого требует AutonomyPolicy.
8. Встроить token reservation/settlement, per-run budgets, max attempts и deadline.
9. Связать traces с workflow/run/step, model, tool, context/rule versions и cost. Не логировать secrets, PII или chain-of-thought.
10. Начать с Red tests: workflow transitions, tool contracts, failure/retry, resume, permissions и budget enforcement.
11. Подтвердить real storage/integration и live-like critical path; unit tests не заменяют это evidence.
12. Зафиксировать deploy, readback, rollback и framework upgrade policy.

При работе с Mastra использовать доступный `mastra` skill для version-aware реализации. Не писать API по памяти.

## 7. Поля ProjectContract

В `AI governance` заполнить:

- `frameworkDecision`: `none | Mastra | <alternative>`;
- `rationale`: почему выбор лучше для exact critical path;
- `orchestrationLayers`: кто владеет domain process, durability и AI execution;
- `runtimeAndVersion`;
- `deploymentModel`;
- `workflowVsAgentBoundary`;
- `storageAndDurability`;
- `memoryOwnershipAndFreshness`;
- `multiAgentTopology` либо `not_applicable`;
- `toolPermissionsAndMutationControls`;
- `humanCheckpoints`;
- `observabilityAndEvals`;
- `tokenBudgetEnforcement`;
- `upgradeAndRollbackPolicy`.

Если выбор сделан до prototype/benchmark, пометить его как assumption и назвать validation case. Для consequential architecture решения допустим короткий spike, но не fake production path.

## 8. Антипаттерны

- Добавлять Mastra «потому что это AI-проект».
- Писать собственный orchestration framework до проверки готового решения.
- Давать agent доступ к БД/API в обход typed tools и permissions.
- Использовать multi-agent как замену decomposition или ясным contracts.
- Считать conversation history долговременной памятью.
- Хранить rules и durable facts внутри prompt без versioning/provenance.
- Прятать retries/loops в agent reasoning без общего attempt budget.
- Считать framework tracing достаточной product observability.
- Предполагать, что memory, storage или resume production-ready без реального restart/recovery test.
- Замыкать domain logic на framework types без adapter boundary, если это затрудняет tests или migration.

## 9. Актуальность документации

Agent frameworks меняются быстро. Перед архитектурным или API-решением проверить официальные docs и установленную версию.

Primary sources:

- [Mastra documentation](https://mastra.ai/docs)
- [Mastra multi-agent workflow](https://mastra.ai/en/examples/agents/multi-agent-workflow)
- [Mastra Temporal integration](https://mastra.ai/blog/introducing-temporal-workflows)
- [Temporal workflows and replay](https://docs.temporal.io/workflows)
- [LangGraph persistence](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [LangGraph memory](https://docs.langchain.com/oss/javascript/langgraph/add-memory)
- [CrewAI documentation](https://docs.crewai.com/index)
- [Agno agents](https://docs.agno.com/agents/overview)
- [Agno teams](https://docs.agno.com/teams/overview)
- [OpenAI Agents SDK orchestration](https://openai.github.io/openai-agents-js/guides/multi-agent/)
- [OpenAI Agents SDK guardrails](https://openai.github.io/openai-agents-js/guides/guardrails/)

Не фиксировать в архитектуре непроверенный claim вида «framework умеет всё из коробки». Фиксировать exact capability, configuration, storage/provider и evidence, который это подтверждает.

## 10. Self-check

1. Доказано ли, что framework нужен?
2. Для TypeScript/Node Mastra оценена первой или причина исключения названа?
3. Проверено ли, нужен один framework или отдельные process engine и AI runtime?
4. Альтернатива выбрана по critical path, а не по популярности?
5. Deterministic workflow отделён от open-ended agent decisions?
6. Multi-agent добавлен по измеримой причине?
7. Memory ownership, freshness, retention и tenant isolation определены?
8. Tool permissions и external mutation controls заданы?
9. Durability, restart, retry, resume и partial failure проверяемы?
10. Tokenomics, evals и observability входят в project harness?
11. Есть adapter/upgrade/rollback strategy и evidence на exact version?
