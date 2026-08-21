# Agent Execution Harness: переносимый control plane над AI-агентами

## 1. Назначение и граница

`Agent Execution Harness` — внешний deterministic control plane над проприетарным или открытым AI-агентом. Он хранит процесс, состояние, evidence и human decisions вне conversation context, поэтому работа переживает compaction, restart и смену host-agent.

Harness не заменяет интеллект агента. Он ограничивает, **что агент может делать сейчас**, какое доказательство нужно для перехода и кто вправе принять consequential решение.

Разделять:

- `Agent Execution Harness` управляет исполнением работы агентом;
- [`testing-harness.md`](testing-harness.md) калибрует и проверяет качество конкретного workflow, роли, skill или multi-agent subject;
- `EvalSuite` измеряет вероятностное AI-поведение.

TestingHarness может быть одним `WorkflowPack`, исполняемым через Agent Execution Harness. Эти понятия не взаимозаменяемы.

## 2. Когда harness оправдан

Использовать внешний harness, если работа имеет хотя бы один material признак:

- длится дольше одной надёжной agent session;
- требует pause/resume, retries или recovery;
- содержит несколько владельцев, handoffs или human checkpoints;
- изменяет repository, deployment, данные или внешнюю систему;
- требует независимого evidence и audit trail;
- имеет денежный, security, privacy или большой blast-radius риск;
- повторяется как устойчивый engineering process.

Не строить harness для короткой обратимой задачи, которую надёжно закрывает один agent run и обычные tests. Процесс должен экономить ожидаемую повторную работу, а не создавать церемонию.

## 3. Непереговорные принципы

1. Authoritative state находится вне prompt и conversation history.
2. Deterministic core владеет стадиями, transitions, budgets и permissions.
3. Агент является worker: его report — claim, а не receipt или approval.
4. Human decision поступает через отдельный authenticated channel.
5. Evidence связывается с exact subject, workflow/stage version и session revision.
6. Mutation разрешена только текущим StageContract и risk policy.
7. Новый workflow добавляется definition/pack, а не новой веткой в core engine.
8. Новый AI-host подключается adapter, не изменением process semantics.
9. Stale evidence и approval не переносятся между несовместимыми subjects/revisions.
10. Failure, timeout или missing evidence не превращаются в success.

## 4. Переносимая архитектура

```text
Workflow Packs ──→ Deterministic Harness Core ←── Session/Event Store
                         │          │
                    Evidence    Approval Channel
                         │          │
                    ProjectAdapter  │
                         │          │
                     HostAdapter ───┘
                         │
               proprietary/open AI agent
```

### Harness Core

Проверяет schemas, current stage/revision, allowed action, transition, evidence policy, budgets, approvals, idempotency и terminal state. Core не знает названий конкретных процессов или vendor API.

### Workflow Packs

Versioned definitions и связанные templates/policies. Bug repair, feature delivery, release, incident recovery или новый пользовательский процесс являются packs, а не hardcoded режимами движка.

### Stores и channels

- `Session/Event Store` — authoritative state и append-only transitions;
- `Evidence Store` — typed receipts или content-addressed refs без raw secrets;
- `Approval Channel` — authenticated human decision;
- UI/dashboard — опциональное представление, не source of truth.

## 5. WorkflowDefinition и WorkflowPack

Минимальная definition:

```yaml
id: portable-workflow
version: 1.0.0
input_schema_ref: schemas/input.json
required_capabilities: []
initial_stage: understand
stages:
  - id: understand
    contract_ref: stages/understand.yaml
  - id: implement
    contract_ref: stages/implement.yaml
terminal_states: [complete, blocked, cancelled]
```

`WorkflowDefinition` содержит только stable process semantics: stages, legal transitions, required capabilities и terminal states.

`WorkflowPack` может дополнительно содержать StageContracts, artifact templates, policy overlays, conformance cases и migration rules между versions.

Правила:

- definition version immutable после использования;
- session pinned к exact workflow version;
- изменение semantics создаёт новую version;
- произвольное число workflows не меняет core;
- data/config не исполняется как доверенный код без validation/signing policy;
- dynamic third-party plugins не нужны до доказанной необходимости.

## 6. StageContract

Каждая stage обязана явно определить:

- objective и observable outcome;
- preconditions;
- allowed read/write/actions;
- forbidden mutations;
- required evidence types и minimum trust;
- `expectation_policy`: `none | per_consequential_action | per_action`;
- legal outcomes/transitions;
- human approval policy;
- attempts, deadline, token/cost budgets;
- stop/escalation conditions;
- stale triggers и recovery/compensation boundary.

Пример:

```yaml
id: verify_candidate
objective: Prove the exact candidate satisfies accepted behavior
allowed_actions: [read_source, run_selected_tests, record_evidence]
required_evidence:
  - type: test
    minimum_trust: independent
expectation_policy: per_consequential_action
transitions:
  pass: accept_candidate
  fail: repair
  insufficient_evidence: blocked
approval: none
budget:
  attempts: 2
stop_conditions: [subject_drift, permission_gap, budget_exhausted]
```

`expectation_policy` выводится из risk: `LOW` → `none`, `STANDARD` →
`per_consequential_action`, `CRITICAL` → `per_action`. Действие, требующее ожидания, не
отправляется без него; отказ бесплатен и не расходует attempt budget.

Stage completion — atomic compare-and-set по expected revision. Late или duplicate transition не должен менять state повторно.

## 7. SessionState и subject identity

Минимальный state:

- session ID, workflow ID/version и status;
- current stage и monotonic revision;
- exact subject fingerprint/version/config/environment;
- host binding и project binding;
- evidence refs и pending decision;
- attempts/deadlines/token/cost usage;
- event sequence и terminal outcome.

`Subject fingerprint` связывает repository/worktree, candidate/config либо другой управляемый объект. Если subject изменился, harness повышает subject version, инвалидирует зависимое evidence и требует fresh receipts.

Не хранить authority в caller-supplied labels. Не считать conversation ID identity пользователя.

## 8. Evidence и approvals

### EvidenceReceipt

Receipt содержит:

- stable ID и type;
- producer/principal и trust class;
- workflow/session/stage/revision;
- subject/config fingerprints;
- environment и observed timestamp;
- payload hash или resolvable artifact reference;
- короткий observable summary;
- `expectation`, когда stage требует его политикой.

Ожидание фиксируется **до** действия: наблюдаемое утверждение, его `committed_hash`,
`verdict` (`HELD` | `MISSED`) и точка расхождения. Хеш отличает ожидание от объяснения
задним числом; без него запись является self-report, а не evidence. Схема —
[`evidence-receipt.schema.json`](../assets/schemas/evidence-receipt.schema.json).

`MISSED` не блокирует стадию, а датирует расхождение модели с реальностью и служит входом
для классификации по [`testing-harness.md`](testing-harness.md), раздел 7.

Agent self-report хранить как `reported`, а не trusted proof. Command/test/artifact/readback evidence получать через независимый runner, hook, system of record или content-addressed resolver.

Не сохранять raw transcript, secrets, лишние PII или chain-of-thought. Raw logs остаются во внешнем разрешённом store; Harness хранит безопасную ссылку/hash.

### HumanDecision

Decision связывать с authenticated principal, exact session/stage/revision/subject, allowed action, timestamp и optional feedback. Агент не записывает решение от имени пользователя и не переносит approval на новый subject.

UI-кнопка является transport. Authoritative decision сначала сохраняет Harness; сообщение в agent host лишь инициирует продолжение.

## 9. HostAdapter и ProjectAdapter

### HostAdapter

Изолирует API конкретного AI-host:

- объявляет capabilities и ограничения;
- bind/rebind host session;
- dispatch stage-scoped instruction;
- получает observable events/result;
- cancel/interrupt;
- подтверждает delivery без объявления task success.

Core использует generic `host_session_ref`, а не Codex-, Claude- или vendor-specific ID/API. Adapter не меняет permissions и transition policy.

### ProjectAdapter

Изолирует subject-specific операции:

- snapshot/fingerprint repository или другого target;
- создание safe workspace;
- разрешённые commands/tools;
- artifact build и provenance;
- deploy/readback/rollback;
- cleanup/reconciliation.

HostAdapter отвечает за связь с агентом. ProjectAdapter — за реальную рабочую среду. Их не объединять в unrestricted tool bridge.

## 10. Runtime loop

```text
discover/select WorkflowDefinition
  → validate input/capabilities
  → create or bind SessionState
  → return exact current StageContract
  → host-agent performs only allowed work
  → collect typed evidence
  → validate transition at expected revision
  → human checkpoint when required
  → resume next stage | block | recover | terminal state
```

На каждом шаге Harness возвращает один current stage. Agent не выбирает удобную следующую стадию и не выполняет downstream mutation заранее.

## 11. Rebind, recovery и replay

При новой conversation/agent session:

1. прочитать authoritative state по exact harness session;
2. убедиться, что прежний active host не будет украден другим active run;
3. rebind к trusted current host reference с expected revision и stable event ID;
4. перечитать current stage;
5. продолжить только совместимую работу.

Context summary не является state transfer.

При crash или uncertain mutation:

- inspect/readback provider, workspace и system of record;
- reconcile terminal state до retry;
- повторять только idempotent action либо выполнять compensation;
- использовать targeted replay от последнего compatible checkpoint;
- block при subject drift, ambiguous effect или missing evidence.

## 12. Использование существующего harness

Если среда уже предоставляет подходящий harness:

1. обнаружить доступные workflow definitions/capabilities;
2. выбрать существующий pack или честно назвать gap;
3. start/bind session к exact project/subject **до mutation**;
4. читать authoritative stage/revision;
5. выполнять только allowed work и записывать typed receipts;
6. завершать stage через Harness;
7. при human checkpoint показать понятное решение и остановиться;
8. после follow-up перечитать state, а не доверять тексту сообщения.

Vibecoding Bible остаётся policy layer: outcome, risk mode, TDD, Regression Registry, security, tokenomics, release composition и production guardrails. Harness остаётся process-state owner. Не вести параллельную state machine в чате.

Если Harness недоступен:

- для короткого low-risk scope использовать явный bounded manual fallback;
- для consequential/resumable scope остановить mutation, сохранить contract/evidence и восстановить Harness;
- если Harness ещё не существует, помочь построить minimal slice из следующего раздела;
- не выдавать чат, checklist или agent memory за durable control plane.

Эту двухветочную границу явно сообщать пользователю в практическом ответе, даже когда внешний Harness в текущем сценарии доступен: она определяет безопасное поведение при outage, unsupported contract или transport failure.

## 13. Минимальная собственная реализация

Начать с одного real workflow и одного HostAdapter:

1. versioned WorkflowDefinition + schema validation;
2. durable SessionState с optimistic revision;
3. StageContract enforcement;
4. append-only event journal и idempotent event IDs;
5. typed EvidenceReceipt resolver;
6. отдельный authenticated approval path;
7. subject fingerprint/drift invalidation;
8. bind/rebind, pause/cancel и crash reconciliation;
9. один ProjectAdapter с least privilege;
10. conformance tests и безопасный runbook.

CLI/API/UI выбирать по реальным host constraints. Не начинать с visual workflow editor, microservices, event bus, dynamic marketplace, multi-agent topology или universal memory.

Следующий workflow должен добавляться definition/pack без изменения core. Второй HostAdapter является сильным portability proof, но не нужен до работающего первого slice.

## 14. Conformance и fault tests

До production trust проверить:

- invalid или unsupported WorkflowDefinition;
- action/transition не из current stage;
- stale expected revision и duplicate event ID;
- subject/config drift после receipt или approval;
- missing, forged или self-attested trusted receipt;
- agent пытается подтвердить собственный consequential result;
- spoofed/duplicate human decision;
- crash до и после external mutation;
- retry вызывает duplicate side effect;
- host session сменился без safe rebind;
- replay queued, skipped или использует incompatible checkpoint;
- budget/deadline/permission exhausted;
- новый WorkflowPack запускается без core-code change;
- unsupported host capability ведёт к block/fallback, а не emulation.

TestingHarness/fault injection проверяет сам harness как subject: seeded false green, trace loss, identity spoofing, stale evidence, duplicate mutation и recovery.

## 15. Red lines

Блокировать соответствующий gate, если:

- authoritative state живёт только в prompt/chat;
- core hardcodes vendor API или фиксированный список workflows;
- agent выбирает stage, повышает privileges или принимает собственный результат;
- mutation выполнена вне allowed StageContract;
- ожидание записано после действия или его `committed_hash` отсутствует;
- transition не защищён revision/idempotency;
- evidence/approval не связано с exact subject;
- host switch переносит старую authority без rebind;
- timeout/transport failure превращён в workflow approval;
- raw secrets/PII/transcript/chain-of-thought сохраняются в Harness;
- manual fallback скрыт или выдан за durable execution;
- конкретная реализация объявлена обязательной частью универсального канона.

## 16. Self-check

Общий self-check — в [`../SKILL.md`](../SKILL.md). Здесь только то, что проверяется именно этим файлом.

1. Core не зависит от vendor и названий workflow?
2. StageContract ограничивает actions/evidence/transitions/budgets?
3. HostAdapter и ProjectAdapter имеют разные responsibilities?
4. Rebind/recovery/replay fail closed?
5. Conformance ловит stale state, self-approval и duplicate mutation?
6. `expectation_policy` соответствует risk, а ожидания зафиксированы до действий?

Использовать шаблон [`agent-harness-contract.md`](../assets/templates/agent-harness-contract.md) только когда harness действительно нужен.
