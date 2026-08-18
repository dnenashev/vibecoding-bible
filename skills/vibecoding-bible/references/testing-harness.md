# TestingHarness v2.1: калибровка и экономный replay

## Содержание

1. Назначение
2. Базовый протокол
3. Роли и доверие
4. Совместно сформировать TestCase
5. Выбрать checkpoints и критерии
6. Провести первый прогон
7. Классифицировать расхождение
8. Выполнить автономный repair
9. Выполнить replay
10. Повышать автономность постепенно
11. Специализировать проверки
12. Проверить сам harness
13. Ограничить автономный цикл
14. Минимальный рабочий slice
15. Red lines
16. Шаблон TestingHarnessContract
17. Self-check

## 1. Назначение

Использовать `TestingHarness` для первого контролируемого испытания нового или существенно изменённого workflow, multi-agent system, agent role или skill.

Первый прогон не означает режим `EXPLORE`. Наследовать `EXPLORE`, `BUILD` или `CRITICAL` от предназначения и риска subject; production-bound workflow по умолчанию остаётся `BUILD`.

Harness нужен, когда ещё неизвестно, проходит ли subject весь путь, сохраняет ли качество в критических точках и соответствует ли ожиданию пользователя.

Главная цель — убрать ручной технический debugging. Человек вместе с агентом определяет качество и принимает смысловые checkpoints. Harness сам исполняет subject, собирает evidence, классифицирует сбой, исправляет подтверждённый дефект и повторяет прогон.

Не применять этот протокол к простой deterministic функции, которую достаточно доказать обычными tests из [`quality.md`](quality.md).

Разделять:

- `EvalSuite` измеряет вероятностное AI-поведение на наборе cases;
- `TestingHarness` проверяет execution path, checkpoints, repair и replay конкретного subject.

Semantic evaluator может использовать EvalSuite, но его verdict не доказывает state, handoff, side effect или recovery. Общие AI rules брать из [`ai-systems.md`](ai-systems.md), release и operational controls — из [`production.md`](production.md).

## 2. Базовый протокол

Использовать модель `Interactive Calibration + Autonomous Repair`:

```text
analyze subject
  → co-design TestCase
  → agree critical checkpoints and quality
  → freeze exact versions
  → run and evaluate checkpoint
  → human calibration
  → classify mismatch
  → bounded repair when allowed
  → replay and final acceptance
  → promote accepted cases to regressions
```

Первый прогон калибрует понимание качества. Последующие прогоны используют подтверждённые criteria как regressions и требуют меньше ручных approvals.

Не просить пользователя читать raw logs. Показывать компактный review и один выбор.

## 3. Роли и доверие

Разделять логические роли:

- `HarnessDesigner` формирует TestCase с пользователем;
- `Runner` запускает subject;
- `Recorder` пишет execution journal;
- `EvidenceCollector` читает hard facts из systems of record;
- `CheckpointEvaluator` применяет frozen rubric;
- `Investigator` классифицирует расхождение;
- `Repairer` исправляет подтверждённый `workflow_defect`;
- `Verifier` независимо запускает tests и replay;
- `HumanApprover` калибрует качество;
- `ReleaseApprover` принимает final release decision.

Несколько ролей могут использовать одну model family, но не одну самоподтверждающую сессию.

Обязательные границы:

- Runner не подтверждает собственный hard pass;
- Evaluator не редактирует subject;
- Repairer не верифицирует и не выпускает свой fix;
- semantic verdict не заменяет hard evidence;
- caller-supplied role label не является authenticated identity;
- subject не принимает сам себя.

Hard evidence получать независимо: test output на exact candidate, state/API readback, database/event receipt, artifact hash, side-effect receipt или authenticated approval.

Каждый receipt связывать с run, checkpoint, subject/config versions, authenticated producer, environment, timestamp и payload hash. Если trusted evidence недоступно, ставить `INSUFFICIENT_EVIDENCE` или `BLOCKED`, а не `PASS`.

## 4. Совместно сформировать TestCase

Сначала изучить actual source/config и предложить draft. Не заставлять пользователя заполнять пустую анкету.

TestCase содержит:

- id, version, owner и risk class;
- subject type и source/build/config/model/tool versions или hashes;
- цель пользователя;
- input, provenance, preconditions и environment;
- acceptable terminal outcome и допустимые альтернативы;
- quality criteria, forbidden outcomes/actions и invariants;
- checkpoints и rubrics;
- required hard, semantic и human evidence;
- attempts/deadline/token/cost budgets;
- external mutation, rollback и final acceptance policy.

Для deterministic результата задавать точное observable state/schema/value. Для вероятностного — quality dimensions, acceptable alternatives, blocking failures и ambiguity policy, а не один эталонный текст.

Test fixtures разрешены только в test environment, имеют version/provenance и не выдаются за live evidence. Недоступную обязательную integration отмечать blocker или отдельным manual path; не заменять её mock success.

После согласования freeze TestCase и exact subject/config versions. Изменение frozen input, criterion или subject создаёт новую version и делает зависимые результаты stale.

## 5. Выбрать checkpoints и критерии

Предложить минимальный набор checkpoints после анализа subject. Оставлять checkpoint только там, где происходит:

- существенное преобразование контекста или critical AI decision;
- handoff, смена owner или durable write;
- freeze важного artifact;
- external side effect;
- permission/approval boundary;
- переход к дорогому, необратимому или high-blast-radius действию;
- terminal outcome.

Не останавливаться после каждого технического шага.

Для checkpoint зафиксировать expected observable state, blocking invariants, semantic rubric, evidence sources, acceptable branches, resume compatibility, human-review policy и rollback boundary.

Для criterion определить observable condition, blocking/advisory status, deterministic/semantic/human evaluator, evidence source, acceptable alternatives и действие при ambiguity/failure.

Не придумывать universal threshold, repetitions или sample size. Выводить их из риска, baseline/variance и цены false pass/false fail через EvalSuite policy.

## 6. Провести первый прогон

### До запуска

1. Изучить actual subject и critical path.
2. Отделить facts, assumptions и unknowns.
3. Совместно утвердить TestCase, checkpoints и criteria.
4. Утвердить budgets, permissions и mutation policy.
5. Freeze TestCase и subject/config versions.

### На каждом checkpoint

1. Runner исполняет subject, Recorder и Collector собирают journal/receipts.
2. Execution останавливается, Evaluator применяет frozen rubric.
3. Пользователь получает компактный `CheckpointReview`.
4. `APPROVE` замораживает checkpoint и продолжает run.
5. `REJECT`, agent `FAIL` или недостаток evidence запускает classification.
6. Только подтверждённый workflow defect поступает в repair loop.
7. После repair/replay checkpoint снова проходит независимую оценку и human review.

Формат review:

```text
Checkpoint: research_ready
Verdict: PASS | FAIL | INSUFFICIENT_EVIDENCE
Criteria: blocking results + visible advisory limitations
Evidence: artifact/state/validator receipt refs
Uncertainty: what is not proven
Recommendation: APPROVE | REJECT | CHANGE_CRITERION | ESCALATE
```

Действия пользователя:

- `APPROVE` — quality/evidence устраивают;
- `REJECT + reason` — результат не соответствует ожиданию;
- `CHANGE_CRITERION` — rubric была неполной или ошибочной;
- `ESCALATE` — требуется продуктовое, risk или permission решение.

После terminal outcome проверить exact candidate по выбранному replay scope, получить final human acceptance и превратить approvals/rejections/defects в regression cases. Не перезапускать неизменённый upstream только ради формальной «чистоты».

Если regression pack становится обязательным gate проекта, зарегистрировать его одной entry по [`regression-registry.md`](regression-registry.md). Не дублировать каждый checkpoint/case в root Registry.

## 7. Классифицировать расхождение

До любого patch выбрать тип или эскалировать ambiguity.

| Тип | Значение | Действие |
|---|---|---|
| `workflow_defect` | Subject нарушает frozen contract | Разрешить bounded repair |
| `test_case_defect` | Ошибочны input/outcome/checkpoint/criterion | Создать новую TestCase version |
| `judge_miscalibration` | Evaluator неверно понял качество | Обновить rubric/judge и перепроверить verdicts |
| `input_or_data_defect` | Fixture неполон, повреждён или stale | Исправить data layer, не subject |
| `environment_or_integration_defect` | Сбой deployment, credentials, provider, storage или network | Исправить boundary/environment |
| `harness_defect` | Recorder, collector, replay или acceptance дали ложное evidence | Инвалидировать run и исправить harness |
| `ambiguous_product_decision` | Не определено правильное поведение | Остановиться и запросить owner decision |

Сохранять evidence, рассмотренные alternatives, confidence и owner. Низкая уверенность или конфликт agent/user ведут к `ESCALATE`, а не speculative patch.

Изменение TestCase, rubric или judge требует новой version и повторной проверки затронутых результатов.

## 8. Выполнить автономный repair

Repair разрешён только для подтверждённого `workflow_defect`:

```text
reproduce → localize → BugSpec → Red → minimal Green
→ regression → targeted replay → independent evaluation → human review
```

BugSpec содержит failed criterion/evidence, minimal reproduction, probable cause, included/excluded scope, invariants, allowed write scope, first Red, regressions, rollback, budgets и stop conditions.

Repairer работает в изолированном namespace/worktree и не получает hidden expected answer или production mutation permissions.

Verifier независимо подтверждает:

- Red падал до fix по ожидаемой причине;
- Green получен изменением behavior, не ослаблением assertion;
- diff остался в BugSpec;
- required regressions проходят;
- результат не hardcoded под fixture;
- replay действительно исполнен.

## 9. Выполнить replay

### Targeted replay — для скорости

Возобновить run от последнего совместимого checkpoint до исправленной точки. Разрешать только при hashed/provenanced snapshot, совместимых state/schema, неизменном upstream, изолированных/idempotent side effects и доказанном resume.

Targeted replay подтверждает исправленный checkpoint. Для final evidence дополнить его проверкой затронутого downstream-пути и terminal invariants.

### Clean checkpoint replay — при затронутом upstream

Запустить новый run от initial input до исправленного checkpoint, если patch затронул upstream behavior или совместимость snapshot не доказана.

### Финальная проверка — по затронутому пути

По умолчанию не запускать workflow заново от initial input. Перед acceptance:

1. подтвердить неизменность upstream source/config/input и совместимость checkpoint snapshot;
2. выполнить targeted replay исправленной точки;
3. пройти от неё весь затронутый downstream-путь до terminal outcome;
4. заново проверить terminal invariants и external side effects через readback/reconciliation;
5. собрать coverage map: какие checkpoints подтверждены свежим replay, а какие — trusted receipts неизменённого upstream.

Full clean replay — опциональная эскалация, а не стандартный gate. Рассматривать его только когда impact analysis не может доказать границу изменения: менялся upstream contract, snapshot несовместим или недостоверен, обнаружен cross-stage state leak, затронута orchestration topology либо targeted/downstream evidence противоречат друг другу. Даже тогда сначала оценить token/time/cost и выбрать более узкий clean segment, если он даёт достаточное evidence.

Для дорогих или необратимых external side effects не повторять весь workflow ради проверки. Использовать idempotency, sandbox, recorded fixtures с provenance, state readback, reconciliation или compensation drill — в зависимости от claim.

Для любого replay:

- повторять actions, а не копировать конечный state;
- не наследовать pass flags и receipts;
- выполнять preflight заново и останавливаться при drift;
- не делать silent substitution или skip;
- считать `queued` неисполненным replay;
- маркировать pinned provider output как offline evidence;
- защищать mutations idempotency, readback и compensation.

## 10. Повышать автономность постепенно

Начинать новый или изменённый checkpoint в `calibration` mode. После human approval сохранять input/output/evidence как regression; rejection — как calibration case; confirmed defect — как failure regression.

Повышать автономность по checkpoint и risk slice:

1. `calibration` — human review каждого critical checkpoint;
2. `assisted` — human подтверждает blocking checkpoints;
3. `supervised` — calibrated checkpoints проходят автоматически, human видит exceptions/final review;
4. `qualified` — routine regressions автоматизированы, ambiguity/drift/high risk возвращают human review.

Новый criterion, subject/model/tool drift, repeated disagreement или failure понижает затронутый checkpoint обратно в calibration.

Не повышать автономность всего workflow по одному удачному run.

## 11. Специализировать проверки

| Subject | Дополнительные проверки |
|---|---|
| Workflow | transitions, resume, stale input, duplicates, partial side effect, terminal artifact |
| Multi-agent | handoff/ack, role identity, privileges, shared-memory provenance, conflicts, loops/deadlocks, partial failure, attribution |
| Agent role | allowed context/tools/actions, output, abstention, escalation, forbidden mutation |
| Skill | fresh-agent trigger/routing, paraphrases, reference loading, missing resources, dirty worktree, prompt injection, permissions, task outcome |

Расширять regressions по риску: valid/invalid/ambiguous input, stale version, tool timeout, budget exhaustion, interruption/resume, duplicate/concurrency conflict, permission escalation, partial readback и human criterion change.

Не покрывать всю matrix до первого полезного run. Сначала провести один high-value path через полный calibration/repair/replay lifecycle.

## 12. Проверить сам harness

До использования harness как единственного release gate провести fault injection. Seeded defect не должен быть известен Runner, Evaluator или Repairer заранее.

Проверить применимые атаки:

- false `passed: true` без receipt;
- потерянный/подменённый evidence ref;
- один principal выдаёт два approvals;
- subject изменился после snapshot;
- replay остался `queued`;
- duplicate external mutation;
- targeted replay прошёл, но затронутый downstream-путь или terminal invariant упал;
- harness принял stale upstream receipt после изменения source/config/input;
- seeded workflow defect;
- user reject против agent pass;
- TestCase defect направлен в workflow repair.

Измерять false green, false red, inconclusive, trace completeness и seeded-defect detection. Thresholds выводить из risk policy и qualification evidence.

До qualification использовать harness как diagnostic evidence, но не как единственный release gate.

## 13. Ограничить автономный цикл

Остановить repair и эскалировать при:

- исчерпанном attempt/deadline/token/cost budget;
- повторе одной причины без нового evidence;
- ambiguous classification или конфликте с frozen TestCase;
- расширении BugSpec/write scope;
- необходимости новых credentials/permissions;
- необратимой/high-risk mutation;
- недоступном trusted evidence;
- harness defect/trace gap;
- расхождении clean и targeted replay;
- оптимизации patch под один fixture.

Показать пользователю expected/observed, уже проверенное, причину остановки и один необходимый decision — не dump логов.

## 14. Минимальный рабочий slice

Провести один high-value TestCase через весь protocol:

- actual subject manifest и frozen TestCase;
- минимальные critical checkpoints;
- automatic journal и trusted evidence;
- evaluation и CheckpointReview;
- classification intentional failure;
- bounded BugSpec, Red/Green и independent verification;
- targeted replay для repair;
- targeted replay и проверка всего затронутого downstream-пути;
- coverage map для fresh и повторно используемого evidence;
- regression artifact и seeded harness fault;
- budgets и stop conditions.

Уменьшать scope числом scenarios/checkpoints и replay только затронутого пути. Не убирать trust boundary, classification, bounded repair, terminal verification или evidence coverage.

## 15. Red lines

### Implementation block

- Нет input, terminal outcome, quality criteria или минимальных critical checkpoints.
- Пользователь не может утвердить rubrics первого run.
- Subject/TestCase/config versions не закреплены.
- Hard evidence принимается от subject/caller.
- Evaluator и Repairer не разделены.
- Reject автоматически считается workflow defect.
- Repair не имеет BugSpec, Red, budget и stop conditions.
- Replay/side-effect policy не определены.

### Acceptance/release block

- Acceptance основан на self-verdict или неаутентифицированном approval.
- Blocking checkpoint не имеет receipt/human calibration.
- Не-workflow defect замаскирован patch subject.
- Replay объявлен/queued или наследует старые pass/evidence.
- Не проверен затронутый downstream-путь или terminal invariants.
- Старый upstream receipt переиспользован без проверки version/hash и snapshot compatibility.
- Repairer подтвердил собственный fix.
- Required live integration заменена offline/mock result.
- Budget превышен, но loop продолжен молча.
- Harness не ловит seeded false green, trace loss или identity spoofing.
- Critical evidence gap скрыт как advisory limitation.
- OutcomeRecord объявлен в момент release без observation window.

## 16. Шаблон TestingHarnessContract

```markdown
# TestingHarnessContract: <name> v<version>

## Subject
Type/id/version/hash; contract/config/model/tool refs; owner/risk:

## TestCase
Goal; input/provenance/preconditions:
Terminal outcome/alternatives; quality/forbidden outcomes/invariants:

## Checkpoints
IDs/rationale; hard invariants/rubrics; evidence; human calibration; resume:

## Roles and trust
Runner/Recorder/Collector/Evaluator; Investigator/Repairer/Verifier/Approvers:
Authentication/separation:

## Execution
Environment/fixtures; attempts/deadline/token/cost budgets:
Stop conditions; external mutation policy:

## Classification and repair
Defect/evidence; BugSpec/write scope; first Red/regressions:

## Replay
Targeted checkpoint; affected downstream path; terminal verification:
Reused upstream receipts and compatibility proof; optional clean-segment trigger:

## Acceptance and autonomy
CheckpointReview; final acceptance; regressions; autonomy promotion/rollback:
Regression Registry entry/admission status:

## Qualification
Seeded faults/results; known gaps; implementation/release verdicts:
```

Заполнять только применимые поля. Хранить links/hashes на evidence, не вставлять raw logs.

## 17. Self-check

1. TestCase совместно определяет input, outcome и quality?
2. Subject и criteria заморожены по version/hash?
3. Checkpoints минимальны и стоят на critical boundaries?
4. Пользователь получает CheckpointReview, а не ручной debugging?
5. Hard evidence собрано независимо, roles/approvals аутентифицированы?
6. `FAIL`/`REJECT` сначала классифицируется?
7. Patch разрешён только для `workflow_defect`?
8. Repair имеет bounded BugSpec, Red/Green и independent verifier?
9. Targeted replay подтверждает исправленную точку?
10. Затронутый downstream-путь и terminal invariants проверены на exact candidate?
11. Переиспользованный upstream evidence привязан к неизменным versions/hashes и совместимому snapshot?
12. Full clean не запускается без конкретного risk trigger и оценки стоимости?
13. Autonomy повышается по checkpoint/risk slice после calibration?
14. Loop останавливается при ambiguity, budget или scope expansion?
15. Harness проверен seeded faults и false-green cases?
16. Required live evidence не заменено offline result?
17. Final acceptance и OutcomeRecord не перепутаны?
18. Обязательный regression pack зарегистрирован одной entry без duplication?
19. Следующий шаг — один calibration/repair/replay slice с минимальным достаточным scope?
