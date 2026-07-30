# TestingHarness: доказательное тестирование AI-систем

## Содержание

1. Назначение и граница с EvalSuite
2. Объекты тестирования
3. Непереговорная модель доверия
4. Роли и separation of duties
5. Версионируемые артефакты
6. Жизненный цикл прогона
7. Режимы исполнения
8. Универсальная матрица сценариев
9. Специализация по объекту тестирования
10. Evidence, checkpoints и semantic verdicts
11. Issue, repair и TDD
12. Clean replay и внешние мутации
13. Acceptance, promotion и rollback
14. Проверка самого harness
15. Observability и tokenomics
16. Mastra и другие реализации
17. Минимальный production-ready slice
18. Red lines
19. Шаблон TestingHarnessContract
20. Self-check

## 1. Назначение и граница с EvalSuite

`TestingHarness` — отдельный служебный контур, который исполняет сценарии, собирает доказательства, останавливает прогон при отклонении, воспроизводит исправление и выдаёт проверяемый acceptance verdict.

Он отвечает на вопрос:

> Можно ли доверять этому прогону, его доказательствам и решению о выпуске?

`EvalSuite` отвечает на другой вопрос:

> Насколько хорошо вероятностный AI-компонент ведёт себя на выбранном наборе случаев?

Эти контуры дополняют друг друга, но не взаимозаменяемы:

- EvalSuite содержит cases, slices, labels, judges, metrics и thresholds;
- TestingHarness управляет execution, identities, trace, checkpoints, repair, replay и acceptance;
- высокий offline eval score не доказывает реальную интеграцию, side effects или recovery;
- зелёный deterministic test не доказывает качество открытого AI-решения;
- release consequential AI behavior обычно требует обоих контуров.

## 2. Объекты тестирования

Один универсальный протокол применяется к четырём основным типам `TestSubject`:

1. `workflow` — последовательность deterministic и AI-шагов, state transitions, approvals и side effects;
2. `multi_agent_system` — topology, роли, handoffs, shared memory, coordination и partial failures;
3. `agent_role` — контракт одной роли: входы, решения, инструменты, permissions, abstention и handoff;
4. `skill` — trigger/routing, инструкции, lazy references, task outcome, permissions и fresh-agent поведение.

При необходимости тип расширяется до `single_agent`, `tool` или `memory_pipeline`, но не ценой потери конкретных инвариантов.

Harness тестирует наблюдаемое поведение и system boundaries, а не скрытую chain-of-thought. Рассуждение агента не является доказательством корректного результата.

## 3. Непереговорная модель доверия

Главное правило:

> Test subject, test actor или semantic supervisor не могут доказать hard fact собственным утверждением.

Недостаточные доказательства:

- boolean `passed: true` от вызывающего клиента;
- текст «проверено» без resolvable evidence reference;
- screenshot без identity, timestamp, target и связанного state receipt;
- supervisor confidence или explanation без наблюдаемого trace;
- hardcoded copy контракта, выданная за hash реального source;
- два approval с разными строками actor, если identity не аутентифицирована;
- replay, который создал запись `queued`, но не исполнил действия;
- отсутствие ошибки, выданное за доказательство outcome.

Hard evidence создаёт `TrustedEvidenceCollector`, находящийся вне control plane субъекта тестирования. Collector проверяет источник и сохраняет immutable или tamper-evident receipt.

Подходящие источники:

- ответ реальной state query с server-side identity и version;
- database/event-store receipt с correlation ID;
- результат test runner на exact commit/config;
- tool receipt с target, arguments hash, result hash и timestamp;
- artifact hash и независимый parser/validator;
- browser/network trace, связанный с run и authenticated session;
- readback внешней системы после mutation.

Если collector недоступен, состояние называется `BLOCKED: evidence collector unavailable`, а не `pending success` и не `passed with confidence`.

## 4. Роли и separation of duties

Минимальная ролевая модель:

- `contract_owner` определяет expected behavior, invariants и risk policy;
- `test_actor` выполняет пользовательские действия: человек, persona agent или deterministic runner;
- `recorder` пишет append-only journal наблюдаемых действий и событий;
- `evidence_collector` независимо подтверждает hard facts;
- `semantic_supervisor` сравнивает наблюдения с контрактом и классифицирует неоднозначности;
- `repairer` реализует approved BugSpec;
- `verifier` повторяет тесты и clean replay;
- `release_approver` принимает promotion/rollback decision.

В маленькой команде один человек может выполнять несколько ролей, но для consequential decision обязательны логическое разделение и durable audit. Запрещено:

- subject-under-test подтверждает собственный pass;
- repairer единолично принимает собственный fix;
- semantic supervisor превращает interpretation в hard evidence;
- caller выбирает произвольную identity через недоверенный header;
- одна identity выдаёт два независимых approval под разными labels;
- ожидаемый ответ скрыто передаётся persona agent.

Identity должна приходить из server-authenticated session/service principal. Проверять нужно capability и роль, а не только строковое имя.

## 5. Версионируемые артефакты

### `TestSubjectManifest`

- `subjectId`, `subjectType`, owner;
- code/skill/workflow/model version и content hash;
- entrypoint и environment;
- topology, roles, tools и permissions;
- ContextPack/Rulebook/EvalSuite/AutonomyPolicy refs;
- state stores и external side effects;
- source refs, вычисленные из фактических файлов/artifacts;
- known limitations и required evidence level.

### `ScenarioContract`

- user/persona goal;
- preconditions и fixture provenance;
- action semantics, но не скрытые UI selectors как единственный контракт;
- expected checkpoints и allowed branches;
- hard invariants и semantic criteria;
- forbidden actions;
- stop conditions, time/token/cost budget;
- required evidence и acceptance policy.

### `RunSnapshot`

- run/attempt IDs и parent lineage;
- exact subject, scenario, environment и dependency versions;
- authenticated actor/role assignments;
- code dirty state и diff hash;
- model/provider/tool/judge versions;
- seed, clock, locale и relevant feature flags;
- started/ended timestamps и terminal status.

### Runtime artifacts

- `JournalEvent` — append-only action/runtime event;
- `EvidenceReceipt` — independently verified fact: content hash, collector/source, authenticated producer, environment/mode, timestamp, correlation, verifier, immutable payload ref и limitations;
- `CheckpointProof` — contract clause + receipts + verdict;
- `Observation` — замеченное отклонение или ambiguity;
- `IssueRecord` — classification, severity, reproduction и evidence bundle;
- `BugSpec` — минимальный approved change contract;
- `RepairRecord` — exact diff/commit, changed-files ledger, scope check, rollback recipe и Red→Green evidence;
- `ReplayRecord` — source/target lineage и action outcomes;
- `AcceptanceReport` — evidence matrix, limits и unresolved areas;
- `PromotionRecord` — decision, approvers, autonomy effect и rollback trigger.

Frozen artifact не редактировать. Создавать новую version и помечать downstream run/replay/report `stale`.

`DecisionRecord` и `OutcomeRecord` не объединять. Release/promotion decision фиксирует ожидание и observation window; реальный outcome создаётся позже из downstream evidence. Нельзя в момент acceptance записать его же status как «наблюдаемый бизнес-результат» с высокой attribution confidence.

## 6. Жизненный цикл прогона

```text
actual contract snapshot
  → preflight
  → clean isolated run
  → append-only journal
  → trusted evidence receipts
  → checkpoint proof
  → deviation? pause and reproduce
  → approved BugSpec
  → Red → Green → Refactor
  → clean replay in a new run
  → independent verification
  → acceptance / limited acceptance / rejection
  → production observation and promotion / rollback
```

### Preflight

До запуска проверить:

1. hashes и versions реального subject/contract;
2. environment, fixtures и data provenance;
3. authenticated identities и permissions;
4. recorder/collector availability и trace completeness probe;
5. side-effect policy, idempotency и rollback capability;
6. budgets, stop conditions и emergency stop;
7. отсутствие скрытого доступа actor к expected answer;
8. пригодность harness к выбранному evidence level.

Manual check может быть явно approved человеком, но не должен автоматически становиться machine-verified fact.

### Во время прогона

- каждое действие получает monotonically increasing sequence и correlation IDs;
- critical event немедленно переводит run в `paused_at_issue`;
- sequence gap, contract drift или потеря collector блокируют продолжение;
- supervisor review привязан к persisted event IDs;
- unknown остаётся unknown; нельзя достраивать trace догадкой;
- retries bounded и различимы с новыми attempts.

Append-only должен обеспечиваться storage policy/constraint, а не только соглашением API. Idempotency receipt сохранять атомарно с mutation или через durable transactional/outbox protocol: сбой между side effect и записью ответа не должен создавать duplicate run, orphan replay или повторную внешнюю mutation.

## 7. Режимы исполнения

1. `deterministic_runner` — machine-executable tests для правил, schemas, state transitions и invariants;
2. `human_supervised` — реальный пользователь действует, supervisor наблюдает каждый checkpoint;
3. `persona_supervised` — изолированный agent-user следует versioned persona contract только через разрешённый интерфейс;
4. `clean_replay` — новый run повторяет action semantics до defect/final checkpoint;
5. `shadow_or_dual_run` — candidate сравнивается с baseline без production authority;
6. `fault_injection` — seeded defects проверяют сам harness и false-green resistance;
7. `production_observation` — ограниченный canary с readback, counter-metrics и rollback trigger.

Mode является свойством evidence. `mock`, `recorded_replay`, `sandbox_live`, `shadow`, `canary` и `production_observation` нельзя повышать простым переименованием записи; новая evidence level требует нового исполнения в соответствующей среде.

Persona agent не получает code, database, internal APIs, supervisor notes или expected answer, если этого не имеет моделируемая роль. Любой такой доступ фиксируется как contamination.

## 8. Универсальная матрица сценариев

Для каждого subject выбирать релевантные slices, а не механически запускать всё:

- happy path и alternate valid branch;
- boundary/empty/unknown/ambiguous input;
- invalid input и forbidden action;
- stale context, stale memory или incompatible version;
- tool/provider timeout, malformed response и partial outage;
- retry exhaustion, token/cost/deadline exhaustion;
- interruption, resume и duplicate delivery;
- concurrency, ordering race и conflicting updates;
- permission escalation и cross-tenant access;
- prompt injection/data exfiltration attempt;
- partial side effect, readback failure и compensation;
- semantic ambiguity, abstention и human handoff;
- regression на ранее найденный production failure.

Sample size, repetitions и thresholds выводить из severity, baseline, variance и допустимой false-pass probability. Не переносить числа из одного проекта как универсальный стандарт.

## 9. Специализация по объекту тестирования

### Workflow

Проверять state machine, обязательный порядок, allowed branches, resume, duplicate events, approvals, artifact lineage, side effects и terminal outcome. Replay повторяет действия, а не копирует конечное состояние.

### Multi-agent system

Проверять:

- topology и разрешённые communication edges;
- role identity и запрет подмены роли;
- handoff payload schema, provenance и acknowledgement;
- ownership shared memory, freshness и conflict resolution;
- attribution decisions/actions конкретному агенту и version;
- bounded loops, deadlock/livelock и duplicate work;
- partial agent/tool failure, restart и recovery;
- separation planner/executor/verifier;
- aggregate token/cost/deadline budget;
- отсутствие privilege amplification через delegation.

### Agent role

Проверять входной контракт, domain boundaries, known/unknown, tool allowlist, permission denials, abstention, escalation, handoff completeness, forbidden mutations, model/context versions и response schema. Роль должна корректно отказать там, где outcome недоказуем или полномочий недостаточно.

### Skill

Проверять на fresh agents без скрытого контекста:

- true-positive trigger и естественные переформулировки;
- true-negative routing, когда skill не нужен;
- полный task outcome, а не упоминание инструкций;
- lazy loading только требуемых references;
- соблюдение read/write/approval boundaries;
- отсутствие fabricated repository/runtime claims;
- обработку missing file/tool/credential;
- instruction conflicts и prompt injection;
- forward-test после каждого существенного изменения;
- regression cases из реальных сбоев.

Skill нельзя валидировать только чтением `SKILL.md` тем же агентом, который его редактировал. Нужен fresh-agent behavior.

## 10. Evidence, checkpoints и semantic verdicts

`CheckpointProof` считается valid только если:

1. ссылается на clause pinned `ScenarioContract`;
2. все hard invariants имеют independently resolvable receipts;
3. receipts принадлежат этому run/attempt и exact subject version;
4. semantic criterion имеет calibrated supervisor/judge либо explicit human review;
5. waiver содержит owner, rationale, expiry и compensating control;
6. known evidence gaps видимы в report.

Evidence делить минимум на:

- `hard_verified` — collector подтвердил observable fact;
- `semantic_reviewed` — meaning оценён calibrated judge/supervisor;
- `human_attested` — человек подтвердил manual observation;
- `offline_simulated` — test double/replay/fixture;
- `live_verified` — реальная integration или live-like path;
- `unverified` — claim ещё не подтверждён.

Semantic supervisor может сказать `pass`, `pause` или `insufficient_evidence`. Его explanation остаётся interpretation, пока hard facts не подтверждены collector.

## 11. Issue, repair и TDD

При отклонении:

1. остановить run на безопасной границе;
2. сохранить evidence bundle и минимальное reproduction;
3. классифицировать: product defect, contract defect, test defect, environment defect, data defect, flaky/unknown;
4. проверить, воспроизводится ли проблема без подсказки ожидаемого ответа;
5. создать bounded `BugSpec` с included/excluded scope, invariants и first Red;
6. получить approval на repair, если write/blast radius этого требует;
7. repairer выполняет Red → Green → Refactor;
8. независимый verifier запускает targeted regression и clean replay;
9. ambiguous contract не «чинить» автоматически — вернуть contract owner.

Нельзя расширять repair до соседнего refactor без нового delta-contract. Passing test, созданный после fix и никогда не видевший Red, не считается достаточным regression evidence.

## 12. Clean replay и внешние мутации

Replay всегда создаёт новый target run с pinned lineage. Он повторяет user-visible action semantics через тот же разрешённый interface.

Правила replay:

- deterministic-first: точное действие либо явный stop;
- запрещены closest-match selector, silent action substitution и пропуск шага;
- фиксированные provider outputs допустимы для path replay, но маркируются offline;
- отдельно выполняется live revalidation probabilistic/provider behavior;
- replay проходит все checkpoints до defect point и затем обязательный downstream path;
- drift source/contract/environment блокирует сравнение либо создаёт новую baseline;
- target run не наследует pass flags и receipts source run.
- target run заново проходит preflight против фактической post-fix build/config и не наследует старый preflight как доказательство;

Для внешней mutation требуются idempotency key, exact target, pre-state, execution receipt, post-action readback и rollback/compensation. Replay не имеет production mutation authority по умолчанию.

## 13. Acceptance, promotion и rollback

Acceptance report отдельно показывает hard, semantic, human, offline, live и unverified evidence. Допустимые terminal verdicts:

- `accepted` — все blocking criteria доказаны на требуемом уровне;
- `accepted_with_limits` — только non-critical limitation с owner/expiry/control;
- `rejected` — defect, red line или недостаточное evidence;
- `blocked` — prerequisite или trusted collector недоступен;
- `invalidated` — contamination, drift или corruption лишили прогон доказательной силы.

Обязательные release условия:

- exact subject/contract/config versions;
- trace completeness и no unresolved sequence gaps;
- no unresolved critical/high issue;
- blocking checkpoints имеют trusted receipts;
- required EvalSuite slices прошли calibrated gates;
- required clean replay/live path выполнены;
- approvals принадлежат authenticated distinct identities;
- production observation, counter-metrics и rollback trigger определены.

Acceptance фиксирует release decision, а не симулирует будущий outcome. `OutcomeRecord` появляется после заявленного observation window и ссылается на независимый source of truth; attribution остаётся `unknown/low`, если причинность не доказана.

Promotion autonomy выполняется на уровне конкретного decision/action. Один успешный run не повышает весь агент или систему автоматически.

## 14. Проверка самого harness

Harness нельзя считать trusted только потому, что он запустился. До использования как release gate провести `HarnessQualification`:

1. внедрить versioned seeded defects, неизвестные supervisor/test actor;
2. проверить detection rate по risk slices;
3. измерить false green, false red и inconclusive;
4. проверить trace completeness и deliberate event loss;
5. подменить/оборвать evidence reference и ожидать fail-closed;
6. попытаться spoof identity и выдать два approval;
7. изменить source после snapshot и ожидать contract drift;
8. повторить side effect и ожидать idempotent result;
9. проверить clean replay на UI/route drift;
10. откалибровать semantic judge на expert-labeled disagreements.

Seeded defects не должны становиться частью production path. Их manifest, owner и cleanup proof сохраняются отдельно.

Пока qualification не пройден, результаты harness называются `diagnostic evidence`, но не единственным release gate. Численные release thresholds определяются risk policy и данными qualification, а не придумываются заранее.

## 15. Observability и tokenomics

Сохранять:

- run/attempt/subject/scenario/actor IDs;
- versions/hashes/context/rules/models/tools/judges;
- state transitions, retries, deadlines и stop reason;
- evidence receipt provenance и verification result;
- agent handoffs, memory reads/writes и stale decisions;
- token reservation, actual usage, cost и latency по role/step;
- human intervention, repair, approval и rollback;
- outcome/counter-metrics после observation window.

Не сохранять secrets, лишние PII и chain-of-thought.

Оптимизировать не число тестовых model calls изолированно, а `cost_per_detected_material_defect` и `cost_per_trusted_accepted_outcome`. Сначала deterministic assertions, затем semantic judge только для действительно неоднозначных критериев. Не экономить токены ценой потери blocking evidence.

## 16. Mastra и другие реализации

Для TypeScript/Node.js Mastra — рекомендуемый первый кандидат, если harness требует durable workflows, agents, tools, memory, suspend/resume и observability. Но framework не является trust boundary сам по себе.

Возможная декомпозиция:

- deterministic workflow/state machine управляет lifecycle и gates;
- Mastra agent выполняет persona или semantic supervisor role;
- durable storage хранит journal, receipts и artifacts;
- отдельный collector адаптер читает реальные systems of record;
- test runner выполняет deterministic assertions;
- browser runner исполняет user-visible path;
- approval service проверяет authenticated capabilities.

Для простого skill или agent role может хватить test runner + fresh-agent invocations + append-only artifacts. Для долгоживущего процесса с сильными recovery guarantees оценивать Temporal или другой durable engine отдельно от AI runtime.

## 17. Минимальный production-ready slice

Первый полный slice harness включает:

1. один versioned subject manifest;
2. один high-value scenario и один negative/failure scenario;
3. реальный contract snapshot и drift detection;
4. authenticated actor и append-only journal;
5. минимум один trusted evidence collector;
6. hard checkpoint и semantic criterion, если он действительно нужен;
7. issue pause и BugSpec;
8. first Red, Green и targeted regression;
9. новый clean replay;
10. acceptance report с explicit unverified areas;
11. fault-injection check самого harness;
12. rollback/cleanup proof.

Уменьшать scope можно количеством subjects/scenarios, но не самодекларацией evidence или удалением trust boundaries.

## 18. Red lines

Implementation gate блокирован, если:

- consequential subject не имеет manifest, invariants и required evidence plan;
- hard facts планируется принимать от subject/caller без collector;
- identity/permissions/separation of duties не определены;
- contract snapshot не связан с actual source/version;
- external mutation не имеет idempotency/readback/rollback;
- repair/replay могут молча изменить contract или production state;
- harness планируется как release gate без qualification strategy.

Release gate блокирован, если:

- acceptance основан на caller-supplied booleans или unresolved refs;
- actor identity spoofable либо approvals не независимы;
- exact versions, lineage или trace неполны;
- append-only/idempotency держатся только на API convention и допускают duplicate/orphan state после crash;
- required clean replay только queued/declared, но не executed;
- required live evidence заменено mock/offline replay;
- semantic self-verdict выдан за hard evidence;
- unresolved critical/high issue или required evidence gap скрыт limitation;
- harness провалил seeded fault, trace-loss или identity-spoof test;
- repairer единолично подтвердил и выпустил собственный fix.

## 19. Шаблон TestingHarnessContract

```markdown
# TestingHarnessContract: <name> v<version>

Subject type/id/version/hash:
Contract source/version/hash:
Owner and risk class:

Outcome and blocking invariants:
Scenarios/slices:
Required evidence levels:

Actor/recorder/collector/supervisor/repairer/verifier/approver:
Authentication and capabilities:
Forbidden role combinations:

Environment/fixtures/provenance:
Journal and evidence stores:
Collector adapters and trust boundaries:
Model/context/rules/tools/judge versions:

Modes and budgets:
Checkpoints and receipts:
Semantic criteria/calibration:
Stop conditions:

Issue classification:
BugSpec approval:
First Red:
Clean replay procedure:

External mutations/idempotency/readback/rollback:
Acceptance and promotion policy:
Production observation/counter-metrics/rollback trigger:

Harness qualification/seeded faults:
Known evidence gaps:
Implementation verdict:
Release verdict:
```

## 20. Self-check

1. EvalSuite и TestingHarness не перепутаны?
2. Subject и actual contract version/hash закреплены?
3. Actor не знает скрытый expected answer?
4. Hard facts создаёт независимый collector, а не caller boolean?
5. Identities аутентифицированы, capabilities проверены?
6. Semantic supervisor не выдан за oracle?
7. Journal append-only, sequence gaps и drift fail-closed?
8. Modes и target-specific probes выбраны по риску?
9. Issue отделяет product, contract, test, environment и data defects?
10. Repair имеет approved BugSpec и доказанный Red→Green?
11. Replay создаёт новый run и действительно исполняет actions?
12. Offline, live, human и unverified evidence разделены?
13. External mutations имеют idempotency/readback/rollback?
14. Release approvals независимы от repair и subject?
15. Harness прошёл seeded faults, trace loss и identity spoofing?
16. Thresholds обоснованы risk/baseline/variance, а не скопированы?
17. Token/cost измеряется на trusted accepted outcome?
18. Следующий шаг — маленький полный slice, а не декоративная панель?
