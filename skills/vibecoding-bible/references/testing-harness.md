# TestingHarness v2: Interactive Calibration + Autonomous Repair

## Содержание

1. Назначение
2. Главный принцип
3. Граница с EvalSuite
4. Объекты тестирования
5. Роли
6. TestCase
7. Проектирование checkpoints
8. Критерии качества
9. Жизненный цикл первого прогона
10. CheckpointReview
11. Классификация расхождений
12. Автономный repair loop
13. Replay protocol
14. Progressive autonomy
15. Evidence и trust boundaries
16. Ограничители автономности
17. Специализация по объектам
18. Scenario matrix
19. Проверка самого harness
20. Observability и tokenomics
21. Реализация и Mastra
22. Минимальный production-ready slice
23. Red lines
24. Шаблон TestingHarnessContract
25. Self-check

## 1. Назначение

`TestingHarness` нужен прежде всего для первого контролируемого испытания нового или существенно изменённого workflow, когда команда ещё не знает:

- работает ли workflow от входа до конечного результата;
- соответствует ли промежуточное поведение реальному намерению пользователя;
- правильно ли выбраны архитектура и границы;
- где возникают потери контекста, качества или state;
- можно ли позже безопасно повысить автономность тестирования.

Harness не должен превращать пользователя в ручного debugger. Пользователь совместно с агентом определяет, что считать хорошим результатом, и принимает смысловые checkpoints. Технический цикл исполнения, диагностики, исправления и перепроверки выполняет harness.

## 2. Главный принцип

> Сначала человек и агент калибруют качество на одном наблюдаемом прогоне. Затем подтверждённые критерии превращаются в regression cases, а harness постепенно становится автономным.

Архитектура называется `Interactive Calibration + Autonomous Repair`:

```text
analyze subject
  → co-design TestCase
  → propose critical checkpoints
  → agree quality rubrics
  → freeze TestCase
  → execute to checkpoint
  → independent agent evaluation
  → user calibration/approval
  → autonomous diagnosis and repair when needed
  → clean replay
  → final acceptance
  → promote approved checkpoints into regressions
```

Ручное изучение логов и пошаговый технический debugging — fallback, а не основной user journey.

## 3. Граница с EvalSuite

`EvalSuite` и `TestingHarness` решают разные задачи.

`EvalSuite` отвечает:

> Насколько хорошо вероятностный AI-компонент ведёт себя на наборе cases и risk slices?

Он содержит:

- cases и label provenance;
- acceptable outcomes;
- deterministic graders и semantic judges;
- slices, metrics и thresholds;
- judge calibration;
- regression history.

`TestingHarness` отвечает:

> Можно ли доверять конкретному исполнению workflow, промежуточному state, исправлению и итоговому acceptance?

Он управляет:

- согласованием TestCase;
- запуском subject;
- checkpoints и human calibration;
- evidence collection;
- diagnosis, BugSpec и repair;
- targeted и clean replay;
- release decision и последующим OutcomeRecord.

EvalSuite может использоваться внутри checkpoint evaluator. Но высокий eval score не доказывает handoff, persistence, external mutation, recovery или полный user journey.

## 4. Объекты тестирования

Базовый протокол применим к:

1. `workflow` — state transitions, AI decisions, approvals, artifacts и side effects;
2. `multi_agent_system` — topology, roles, handoffs, shared memory и coordination;
3. `agent_role` — входы, decisions, tools, permissions, abstention и escalation;
4. `skill` — trigger/routing, instructions, references, permissions и task outcome.

При необходимости разрешены `single_agent`, `tool` и `memory_pipeline`. Специализация не должна устранять общий calibration/repair/replay protocol.

## 5. Роли

Harness разделяет логические роли, даже если несколько ролей используют один model family:

- `HarnessDesigner` анализирует subject и проектирует TestCase вместе с пользователем;
- `Runner` запускает workflow и действует через разрешённый interface;
- `Recorder` автоматически пишет append-only execution journal;
- `EvidenceCollector` подтверждает hard facts из systems of record;
- `CheckpointEvaluator` оценивает результат по frozen rubric;
- `Investigator` классифицирует расхождение и локализует причину;
- `Repairer` исправляет только approved `workflow_defect` в bounded scope;
- `Verifier` независимо запускает tests и replay;
- `HumanApprover` калибрует смысловое качество на первом прогоне;
- `ReleaseApprover` принимает final promotion/rollback decision.

Обязательная независимость:

- Runner не подтверждает собственный hard pass;
- Repairer не верифицирует и не выпускает свой fix;
- CheckpointEvaluator не редактирует subject;
- semantic verdict не заменяет hard evidence;
- один caller не изображает несколько approvers произвольными labels.

Независимость может обеспечиваться отдельными агентными сессиями с минимальным контекстом, а не обязательно разными моделями.

## 6. TestCase

Первый этап всегда диалоговый. Агент изучает реальный subject, затем вместе с пользователем формирует `TestCase`.

### Обязательные поля

- `testCaseId`, version, owner и risk class;
- `TestSubjectManifest` с actual source/build/model/tool hashes;
- цель пользователя и ожидаемый terminal outcome;
- входные данные с provenance и privacy class;
- preconditions, environment и fixtures;
- допустимые варианты выходного результата;
- критерии качества результата;
- недопустимые результаты и forbidden actions;
- критические инварианты;
- checkpoints и их rubrics;
- required hard/semantic/human/live evidence;
- budgets: attempts, deadline, tokens и cost;
- external mutation policy;
- final acceptance и rollback policy.

### Входные данные

Использовать реальные или синтетически созданные test fixtures только внутри test environment. Fixture должен быть versioned и маркирован как test data. Он не выдаётся за live evidence и не попадает в production path.

Если workflow зависит от реальной integration, заранее определить sandbox/live-like boundary. Недоступность обязательной integration означает `BLOCKED`, manual verification или честное ограничение, но не mock success.

### Ожидаемый результат

Для deterministic output можно задать точное expected value/schema/state.

Для вероятностного output задавать:

- acceptable outcome set;
- quality dimensions;
- minimum blocking criteria;
- examples только как anchors, а не единственный допустимый текст;
- counter-examples и forbidden claims;
- ambiguity/fallback policy.

Нельзя превращать один эталонный output в требование дословного совпадения, если задача допускает несколько качественных решений.

## 7. Проектирование checkpoints

После первичного анализа workflow агент предлагает минимальный набор критических checkpoints. Пользователь утверждает или меняет их до запуска.

Checkpoint нужен, когда происходит хотя бы одно:

- существенное преобразование или потеря контекста;
- критическое AI-решение;
- handoff между workflows, roles или agents;
- запись durable state;
- freeze/versioning важного artifact;
- внешний side effect;
- human approval;
- переход, после которого исправление становится дорогим;
- security/permission boundary;
- irreversible или high-blast-radius action.

Checkpoint не нужен после каждого технического шага. Избыточные остановки повышают стоимость, создают approval fatigue и мешают увидеть целостный workflow.

Каждый checkpoint содержит:

- `checkpointId` и contract clause;
- expected observable state;
- blocking hard invariants;
- semantic quality rubric;
- evidence sources;
- allowed branches;
- resume compatibility rule;
- user review requirement;
- rollback/compensation boundary;
- downstream dependents.

## 8. Критерии качества

Критерий должен быть проверяемым и помогать принять решение. Формулировка «результат хороший» недостаточна.

Для каждого критерия указать:

- quality dimension;
- observable condition;
- blocking или advisory;
- evaluator: deterministic, semantic judge или human;
- evidence source;
- acceptable alternatives;
- failure severity;
- ambiguity handling;
- owner изменений критерия.

Пример:

```yaml
criterion: facts_have_provenance
dimension: trustworthiness
blocking: true
condition: every factual claim has a resolvable source reference
evaluator: deterministic_validator
evidence: artifact_claim_ledger
on_failure: pause_and_classify
```

Численные thresholds, repetitions и sample size нельзя изобретать. Они выводятся из risk tolerance, baseline, variance и цены false pass/false fail.

## 9. Жизненный цикл первого прогона

### Phase A — Design

1. Изучить actual workflow/source/config.
2. Зафиксировать facts, assumptions и unknowns.
3. Сформировать draft TestCase.
4. Предложить critical checkpoints.
5. Совместно определить quality rubrics.
6. Утвердить mutation, privacy и budget policies.
7. Freeze `TestCase v1` и hashes subject/config.

### Phase B — Guided execution

1. Runner запускает workflow с утверждённым input.
2. Recorder и Collector автоматически собирают trace/evidence.
3. На checkpoint выполнение останавливается.
4. CheckpointEvaluator применяет frozen rubric.
5. При agent `PASS` пользователь получает компактный `CheckpointReview`.
6. При user `APPROVE` checkpoint замораживается и workflow продолжается.
7. При agent `FAIL` либо user `REJECT` запускается classification.
8. Confirmed workflow defect уходит в autonomous repair loop.
9. После repair и replay checkpoint снова проходит agent evaluation и user review.
10. Цикл повторяется до terminal outcome.

### Phase C — Final verification

1. Выполнить полный clean replay от первоначального input.
2. Проверить все frozen checkpoints без наследования старых pass flags.
3. Собрать final output quality review.
4. Получить final human acceptance.
5. Превратить approved checkpoints и defects в regression cases.

## 10. CheckpointReview

Пользователь не должен разбирать raw logs. Harness формирует компактный review packet:

```text
Checkpoint: research_ready
Verdict: PASS | FAIL | INSUFFICIENT_EVIDENCE

Criteria:
✓ Coverage соответствует rubric
✓ Все факты имеют источники
✱ Один источник недоступен; limitation видима

Evidence:
- artifact hash
- state receipt
- validator output
- relevant trace refs

Uncertainties:
- что не удалось доказать

Recommendation:
APPROVE | REJECT | CHANGE_CRITERION | ESCALATE
```

Пользователь выбирает:

- `APPROVE` — качество устраивает, checkpoint frozen;
- `REJECT + reason` — результат не соответствует ожиданию;
- `CHANGE_CRITERION` — первоначальная rubric была неполной/ошибочной;
- `ESCALATE` — требуется отдельное продуктовое решение.

Raw trace доступен по ссылкам, но не является основным интерфейсом приёмки.

## 11. Классификация расхождений

Любой agent `FAIL` или user `REJECT` сначала классифицируется. Нельзя автоматически менять workflow до определения типа проблемы.

### `workflow_defect`

Реализация нарушает frozen TestCase, invariant или rubric. Разрешён bounded autonomous repair.

### `test_case_defect`

Вход, expected outcome, checkpoint или criterion сформулированы неверно/неполно. Изменить TestCase новой version, пометить зависимые результаты stale и повторить затронутый путь.

### `judge_miscalibration`

CheckpointEvaluator неправильно оценил приемлемый результат. Добавить calibration example, обновить judge/rubric version и повторно проверить прежние verdicts.

### `input_or_data_defect`

Fixture повреждён, неполон, устарел либо не соответствует preconditions. Исправить/заменить fixture, не маскировать проблему кодовым patch.

### `environment_or_integration_defect`

Причина находится в deployment, credentials, provider, network, storage или test environment. Repair subject запрещён без доказанной причинности.

### `ambiguous_product_decision`

Нет утверждённого ответа, какое поведение правильно. Остановиться и запросить решение пользователя/contract owner.

### `harness_defect`

Recorder, collector, executor, replay или acceptance logic дали неполное/ложное evidence. Результат run инвалидируется; сначала исправляется и повторно квалифицируется harness.

Classification сохраняет evidence, alternatives, confidence и owner. Низкая уверенность либо конфликт evaluator/user автоматически эскалируется, а не превращается в workflow patch.

## 12. Автономный repair loop

Автономный repair разрешён только для подтверждённого `workflow_defect`.

```text
failure evidence
  → reproduce
  → localize probable cause
  → bounded BugSpec
  → first Red
  → approved write scope
  → minimal Green
  → Refactor inside scope
  → deterministic verification
  → targeted replay
  → independent checkpoint evaluation
  → user review
```

`BugSpec` содержит:

- failed criterion и evidence bundle;
- minimal reproduction;
- probable cause и alternatives considered;
- included/excluded scope;
- invariants и permissions;
- first Red и required regressions;
- allowed files/components;
- rollback recipe;
- attempt/token/cost budget;
- exit/escalation conditions.

Repairer работает в изолированном worktree/namespace. Он не видит hidden expected answer сверх TestCase и не получает production mutation permissions.

Verifier проверяет:

- что first Red действительно падал до исправления;
- что Green вызван изменением behavior, а не ослаблением assertion;
- что diff ограничен BugSpec;
- что required regressions проходят;
- что новый output не hardcoded под единственный fixture;
- что targeted replay достиг исправленного checkpoint.

## 13. Replay protocol

Один тип replay не решает одновременно задачу скорости и доказательности. Использовать три уровня.

### 1. `Targeted replay`

Быстрая итерация от последнего проверенного совместимого checkpoint до исправленной точки.

Разрешён, если:

- checkpoint snapshot имеет hash и provenance;
- schemas/state совместимы с новым code/config;
- изменённый код не влияет на upstream state;
- external mutations безопасно изолированы;
- resume capability реально проверена.

Targeted replay ускоряет debugging, но не является final acceptance evidence.

### 2. `Clean checkpoint replay`

Новый run от исходного input до исправленного checkpoint. Он проверяет, что fix работает вместе с upstream path и не зависит от старого snapshot.

Обязателен после успешного targeted replay перед окончательным user approval исправленного checkpoint, если patch затрагивает upstream behavior либо совместимость state не доказана.

### 3. `Full clean replay`

Новый end-to-end run от initial input до terminal outcome на exact candidate version. Обязателен перед final acceptance/release.

Правила всех replay:

- повторять action semantics, а не копировать конечный state;
- target run не наследует pass flags и receipts;
- заново выполнять preflight;
- drift ведёт к stop/new baseline, а не silent adaptation;
- запрещены closest-match action substitution и пропуск шагов;
- provider-output pinning маркируется offline и не заменяет live revalidation;
- внешние mutations требуют idempotency, readback и compensation;
- запись `queued` не считается исполненным replay.

## 14. Progressive autonomy

Первый unknown workflow запускается в `calibration` mode: пользователь утверждает каждый критический semantic checkpoint.

После approval:

- frozen input/output/evidence становятся regression case;
- user rejection становится calibration case;
- confirmed defect становится failure regression;
- rubric и judge получают новую version;
- replay history сохраняет model/context/tool versions.

Следующие runs могут переходить по уровням:

- `L0 manual calibration` — human approval на каждом checkpoint;
- `L1 assisted` — agent evaluates, human подтверждает blocking checkpoints;
- `L2 supervised autonomy` — agent auto-passes calibrated checkpoints, human видит exceptions и final review;
- `L3 qualified autonomy` — routine regressions проходят автоматически, human нужен только для drift/high-risk/ambiguity;
- `L4 release gate` — разрешён только после qualification harness, production observation и отдельного approval.

Autonomy повышается по checkpoint/risk slice, а не для workflow целиком. Новый criterion, subject drift, model/tool change или repeated disagreement понижает соответствующий checkpoint до calibration mode.

## 15. Evidence и trust boundaries

Hard fact нельзя подтвердить boolean `passed: true` от Runner, subject, caller или semantic evaluator.

`EvidenceCollector` независимо получает:

- database/event-store receipts;
- state/API readback;
- test runner output на exact commit;
- artifact hashes и validator results;
- tool call/side-effect receipts;
- browser/network trace;
- authenticated approval event.

Каждый `EvidenceReceipt` содержит:

- run/attempt/checkpoint IDs;
- subject/config versions;
- collector/source и authenticated producer;
- environment/evidence mode;
- timestamp/correlation;
- content/payload hash;
- verification result;
- limitations и expiry.

Evidence levels различать:

- `hard_verified`;
- `semantic_reviewed`;
- `human_calibrated`;
- `offline_simulated`;
- `live_verified`;
- `unverified`.

Journal защищается storage constraints, а не только API convention. Idempotency receipt сохраняется атомарно с mutation либо через durable outbox/transactional protocol.

Если collector недоступен, checkpoint получает `INSUFFICIENT_EVIDENCE`/`BLOCKED`, а не pass.

## 16. Ограничители автономности

Autonomous loop обязан остановиться, когда:

- исчерпан maximum attempts/deadline/token/cost budget;
- дважды повторяется та же probable cause без нового evidence;
- classification неоднозначна;
- пользовательское ожидание конфликтует с frozen contract;
- repair требует расширить BugSpec/write scope;
- нужны новые credentials/permissions;
- затрагивается irreversible/high-blast-radius mutation;
- невозможно получить trusted evidence;
- обнаружен harness defect или trace gap;
- clean replay расходится с targeted replay;
- patch начинает оптимизироваться под один fixture.

При stop пользователь получает не dump логов, а escalation packet:

- что ожидалось;
- что наблюдается;
- что уже проверено/исправлено;
- почему автономный цикл остановлен;
- одно конкретное решение, которое требуется от человека.

## 17. Специализация по объектам

### Workflow

Checkpoint candidates: major state transitions, handoffs, durable writes, approvals, external mutations и terminal artifact. Проверять resume, duplicates, stale inputs и end-to-end outcome.

### Multi-agent system

Дополнительно проверять:

- topology и communication edges;
- typed handoff и acknowledgement;
- role identity и privilege boundaries;
- shared memory ownership/provenance/freshness;
- conflict resolution, loops и deadlocks;
- partial agent failure и restart;
- aggregate token/cost budget;
- attribution decisions/actions конкретной role/version.

Checkpoints ставить на critical handoffs и ownership changes, а не после каждого agent message.

### Agent role

Проверять входной контракт, allowed knowledge/tools/actions, typed output, abstention, escalation и forbidden mutation. Human calibration особенно важна для semantic quality и границы «достаточно данных».

### Skill

Запускать fresh-agent cases без скрытой истории:

- positive/negative trigger;
- естественные paraphrases;
- lazy reference loading;
- task outcome;
- permission/approval boundaries;
- missing file/tool/credential;
- dirty worktree preservation;
- prompt injection;
- clean replay на новой session/environment.

Checkpoint для skill обычно ставится на routing, перед consequential write и на terminal task outcome.

## 18. Scenario matrix

Для первого TestCase выбрать один high-value path. Затем расширять regressions по риску:

- happy path;
- alternate valid branch;
- empty/unknown/ambiguous input;
- invalid input и forbidden action;
- stale context/memory/version;
- provider/tool timeout и malformed response;
- retry/budget exhaustion;
- interruption/resume;
- duplicate delivery;
- concurrency/conflict;
- permission escalation;
- cross-tenant access;
- prompt injection/exfiltration;
- partial side effect/readback failure;
- human rejection и rubric change;
- previously observed production failure.

Не пытаться покрыть всю matrix до первого полезного прогона. Первый slice должен быть узким, но пройти полный calibration/repair/replay lifecycle.

## 19. Проверка самого harness

До использования как release gate harness проходит `HarnessQualification`:

1. Runner сообщает false `passed: true` без receipt.
2. Collector теряет или получает подменённый evidence ref.
3. Один principal пытается дать два approval.
4. Subject/source меняется после snapshot.
5. Replay остаётся только `queued`.
6. External mutation доставляется дважды.
7. Targeted replay проходит, а full clean replay ломается.
8. В workflow внесён seeded defect, неизвестный Evaluator/Runner.
9. User rejection противоречит judge pass для проверки calibration flow.
10. TestCase defect пытаются ошибочно исправить patch workflow.

Измерять false green, false red, inconclusive, trace completeness и seeded-defect detection. Thresholds выводятся из risk policy и qualification data.

Пока qualification не пройден, harness даёт `diagnostic evidence`, но не является единственным release gate.

## 20. Observability и tokenomics

Сохранять:

- TestCase/subject/config/model/tool/judge versions;
- run/attempt/checkpoint/actor IDs;
- state transitions и evidence receipts;
- agent/user verdict disagreements;
- classification и confidence;
- BugSpec, diff, Red/Green и replay lineage;
- tokens/cost/latency по role и attempt;
- human interventions и причины escalation;
- production OutcomeRecord после observation window.

Не сохранять secrets, лишние PII и chain-of-thought.

Оптимизировать:

- `cost_per_calibrated_checkpoint` на первом прогоне;
- `cost_per_detected_material_defect`;
- `cost_per_trusted_accepted_outcome`;
- долю checkpoints, перешедших от manual calibration к supervised autonomy;
- human minutes per accepted run.

Сначала использовать deterministic validators. Semantic judge вызывать только для действительно смысловых критериев. Экономия не должна удалять blocking evidence.

## 21. Реализация и Mastra

Для TypeScript/Node.js Mastra — рекомендуемый первый кандидат, если нужны agents, tools, workflows, memory, suspend/resume и observability.

Возможная архитектура:

- deterministic state machine управляет lifecycle и gates;
- Mastra workflow координирует Runner/Evaluator/Investigator/Repairer/Verifier;
- separate agent sessions обеспечивают role isolation;
- durable store хранит TestCases, checkpoints, journals и receipts;
- collector adapters читают реальные systems of record;
- test runner исполняет deterministic Red/Green;
- browser/API runner исполняет user-visible workflow;
- human approval реализован через suspend/resume;
- budget policy ограничивает repair loops.

Framework не создаёт trust boundary автоматически. Для простого skill достаточно fresh-agent runner, isolated fixtures, test runner и content-addressed artifacts. Для долгоживущих business processes отдельно оценивать Temporal/другой durable engine.

## 22. Минимальный production-ready slice

Первый slice включает:

1. один actual subject manifest;
2. один совместно утверждённый TestCase;
3. один terminal outcome;
4. один-два действительно critical checkpoints;
5. один automatic recorder и trusted collector;
6. agent evaluation + human CheckpointReview;
7. classification хотя бы одного intentional failure;
8. bounded BugSpec и first Red;
9. isolated repair + independent verification;
10. targeted replay;
11. full clean replay;
12. final acceptance и regression artifact;
13. один seeded harness fault;
14. budgets и stop conditions.

Уменьшать scope количеством scenarios/checkpoints. Нельзя уменьшать его self-attested evidence, отсутствием replay или бесконтрольным repair.

## 23. Red lines

Implementation gate блокирован, если:

- TestCase не определяет input, outcome и quality criteria;
- checkpoints выбраны без анализа критических transitions/risk boundaries;
- user не может утвердить rubrics первого calibration run;
- hard evidence планируется принимать от subject/caller;
- Evaluator и Repairer не разделены;
- reject автоматически считается workflow bug без classification;
- repair loop не имеет BugSpec, budgets и stop conditions;
- replay/side-effect policy не определены;
- actual subject/contract versions не закреплены.

Release gate блокирован, если:

- acceptance основан на agent self-verdict;
- user approval или hard receipt отсутствуют для blocking checkpoint первого run;
- `test_case_defect`, `judge_miscalibration` или environment defect замаскированы patch workflow;
- replay только queued/declared;
- выполнен только targeted replay без required clean replay;
- target replay наследует pass flags/evidence;
- repairer подтвердил собственный fix;
- required live integration заменена mock/offline result;
- attempts/budget exceeded, а run продолжен молча;
- harness не ловит seeded false green/trace loss/identity spoofing;
- unresolved critical/high issue или evidence gap спрятан limitation;
- OutcomeRecord создан одновременно с release decision без observation window.

## 24. Шаблон TestingHarnessContract

```markdown
# TestingHarnessContract: <name> v<version>

## Subject
Type/id/version/hash:
Actual contract/config/model/tool refs:
Owner/risk class:

## TestCase
User goal:
Input/provenance/preconditions:
Expected terminal outcome:
Acceptable alternatives:
Quality criteria:
Forbidden outcomes/invariants:

## Checkpoints
Checkpoint IDs and rationale:
Hard invariants:
Semantic rubrics:
Evidence sources:
Human calibration requirements:
Resume compatibility:

## Roles
Designer/Runner/Recorder/Collector/Evaluator:
Investigator/Repairer/Verifier/Approvers:
Authentication/separation of duties:

## Execution
Environment/fixtures:
Attempts/deadline/token/cost budgets:
Stop/escalation conditions:
External mutation policy:

## Classification and repair
Defect taxonomy:
BugSpec/write-scope approval:
First Red/regressions:

## Replay
Targeted replay:
Clean checkpoint replay:
Full clean replay:

## Acceptance and autonomy
Checkpoint review protocol:
Final acceptance:
Regression promotion:
Autonomy level/promotion/rollback:

## Harness qualification
Seeded faults:
Known evidence gaps:
Implementation verdict:
Release verdict:
```

## 25. Self-check

1. Harness тестирует новый workflow, а не требует заранее знать всё его внутреннее поведение?
2. TestCase совместно определяет input, output и качество?
3. Checkpoints минимальны и находятся на критических границах?
4. Каждый criterion наблюдаем и имеет evaluator/evidence?
5. Первый run действительно калибруется пользователем?
6. Пользователь получает CheckpointReview, а не raw-log debugging?
7. Agent FAIL/user REJECT сначала классифицируются?
8. Workflow patch разрешён только для confirmed workflow_defect?
9. TestCase/judge/data/environment defects исправляются в правильном слое?
10. Runner/Evaluator/Repairer/Verifier логически разделены?
11. Repair имеет bounded BugSpec, Red/Green и budgets?
12. Targeted replay используется для скорости, но не выдаётся за final proof?
13. Full clean replay выполнен от initial input?
14. Hard evidence независимо собрано?
15. User approvals и identities аутентифицированы?
16. Autonomy повышается по checkpoint/risk slice после calibration evidence?
17. Loop останавливается при ambiguity, repeated failure или scope expansion?
18. Harness ловит seeded false green и собственные defects?
19. OutcomeRecord отделён от release decision?
20. Первый следующий шаг — один полный calibration/repair/replay slice?
