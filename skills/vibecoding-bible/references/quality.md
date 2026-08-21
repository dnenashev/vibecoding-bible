# Quality: практичная стратегия проверки продукта

## Содержание

1. Назначение
2. Сначала риск, потом тесты
3. Минимальная стратегия по режимам
4. Пирамида проверок
5. Static, types и lint
6. Unit и component
7. Contract и integration
8. End-to-end
9. Property, fuzz и concurrency
10. Security, performance и accessibility
11. Test data и изоляция
12. Flakiness
13. Debugging feedback loop
14. Evidence и release matrix
15. Граница с AI-проверками
16. Шаблон QualityPlan
17. Self-check

## 1. Назначение

Этот модуль отвечает на простой вопрос: **каким минимальным набором проверок доказать, что выбранный scope работает и безопасен для выпуска**.

Не измерять качество количеством тестов. Проверять наблюдаемое поведение, дорогие failure modes и реальные границы системы.

Использовать общий цикл:

```text
risk → expected behavior → cheapest trustworthy check → stronger boundary evidence → release verdict
```

Не требовать от маленькой обратимой задачи тестовой бюрократии уровня платёжной системы. Не выпускать consequential behavior по одному unit test.

## 2. Сначала риск, потом тесты

Для изменяемого scope зафиксировать:

- кто и как использует результат;
- что должно произойти на happy path;
- что нельзя допустить;
- какие данные, permissions и внешние side effects затронуты;
- цена false pass, false fail и недоступности;
- насколько легко обнаружить и откатить ошибку;
- какие границы чаще всего ломаются: UI, API, storage, provider, queue, device или human handoff.

Затем выбрать проверки, которые закрывают эти риски. Не добавлять тест, если непонятно, какое решение он защищает.

Если проект имеет библиотеку обязательных проверок или нуждается в ней, полностью прочитать [`regression-registry.md`](regression-registry.md). Выбрать применимые entries по impact; не запускать весь Registry автоматически.

Для каждого acceptance criterion указать:

- required evidence level;
- точную команду или процедуру;
- blocking или advisory статус;
- environment и необходимые данные;
- ожидаемый observable result;
- owner исправления при fail.

## 3. Минимальная стратегия по режиму и риску

### Mode `EXPLORE`

Проверять только гипотезу и самые опасные ограничения:

- выполнить один representative path;
- проверить, что spike не затрагивает production и реальные данные;
- поставить time/cost box;
- явно маркировать результат как non-production;
- в конце выбрать `discard`, `continue` или `promote`.

Не строить полную regression suite для идеи, которую можно выбросить. Перед promotion в `BUILD` создать нормальный QualityPlan.

### Mode `BUILD`

Это режим по умолчанию. Требовать:

- static/type/lint проверки, применимые к стеку;
- unit/component coverage изменённой логики;
- contract/integration evidence на затронутых границах;
- один полный critical user journey;
- проверки ошибок, permissions и recovery;
- release evidence на exact candidate.

### Risk `CRITICAL`

Применимо и к `EXPLORE`, и к `BUILD`. Для денег, PII, regulated data, высокого autonomy или большого blast radius усилить:

- threat-driven negative tests;
- tenant/permission isolation;
- migration, rollback и recovery drills;
- concurrency, duplicate delivery и partial failure;
- независимое review consequential changes;
- canary и production monitoring;
- более сильный evidence для каждой red line.

Силу проверок выводить из риска и принятой reliability policy. Не придумывать универсальное число cases, coverage percentage или latency threshold.

## 4. Пирамида проверок

Использовать самый дешёвый уровень, который действительно ловит нужный failure, но не останавливаться ниже реальной границы риска.

| Уровень | Проверяет | Не заменяет |
|---|---|---|
| Static/type/lint | синтаксис, типы, локальные policy violations | runtime behavior |
| Unit | изолированную domain logic | integration и user journey |
| Component | компонент с контролируемыми зависимостями | реальный provider/storage |
| Contract | совместимость schema/interface | доступность и поведение integration |
| Integration | реальные границы в sandbox/test environment | полный пользовательский путь |
| E2E | критический путь через собранную систему | длительный production outcome |
| Production observation | реальную работу и последствия | причинность без анализа |

Предпочитать много быстрых deterministic checks и несколько сильных boundary/E2E checks. Не заменять integration сетью mocks.

## 5. Static, types и lint

Включить только проверки, которые реально соответствуют стеку:

- compiler/type checker;
- formatter check;
- linter;
- schema/config validation;
- dependency и secret scanning;
- generated-code drift check;
- migration validation;
- dead-link/documentation check, если docs входят в product surface.

Новая warning в blocking command считается failure, если policy не объявляет её advisory. Не скрывать ошибку общим disable/ignore. Исключение делать локальным, обоснованным и проверяемым.

## 6. Unit и component

Unit test должен описывать behavior, а не внутреннюю реализацию.

Начинать изменение поведения с минимального Red:

1. воспроизвести требуемое поведение или defect;
2. убедиться, что test падает по ожидаемой причине;
3. сделать минимальный Green;
4. refactor без ослабления assertion;
5. запустить соседние regressions.

Unit tests особенно полезны для:

- state transitions;
- validation и normalization;
- authorization policy;
- calculations и mapping;
- retry/idempotency decisions;
- deterministic fallback;
- parsing и serialization.

Component tests использовать для UI, service modules и adapters на контролируемых границах. Проверять observable input/output/state, loading/error/empty states и accessibility semantics.

Test double разрешён только на внешней границе в test-only composition root. Он не является live integration evidence.

## 7. Contract и integration

Contract tests проверяют обе стороны интерфейса:

- request/response schema;
- events и version compatibility;
- database constraints;
- tool/function schemas;
- error taxonomy;
- timeout/retry/idempotency semantics.

Integration test должен обращаться к реальной тестовой реализации границы: sandbox provider, test database, queue, storage, auth или browser runtime.

Проверять не только happy path:

- invalid и missing input;
- timeout и malformed response;
- rate limit и retry exhaustion;
- duplicate delivery;
- permission denied;
- partial side effect;
- readback mismatch;
- stale schema/config.

Если mandatory integration недоступна, отметить scope `BLOCKED` или ограничить release честным manual path. Не подменять отсутствие доступа fabricated success.

## 8. End-to-end

Выбрать немного critical journeys, которые проходят через собранную систему от реального entrypoint до observable outcome.

E2E должен фиксировать:

- exact candidate/version и environment;
- preconditions и isolated namespace;
- действия пользователя или клиента;
- важные state transitions;
- terminal state и readback;
- cleanup либо безопасно сохранённый audit artifact.

Проверять основной путь, один дорогой failure/recovery path и затронутые permissions. Не превращать E2E в дублирование всех unit cases.

Flaky E2E не является release evidence, пока причина не локализована. Retry может измерять нестабильность, но не должен молча превращать failure в pass.

## 9. Property, fuzz и concurrency

Добавлять эти проверки, когда структура риска их оправдывает.

Использовать property-based tests для:

- инвариантов на широком пространстве inputs;
- round-trip serialization;
- ordering, totals и conservation rules;
- parsers и transformations.

Использовать fuzzing для недоверенного input, file/protocol parsers и security boundaries.

Использовать concurrency/chaos tests для:

- duplicate requests и race conditions;
- locking и optimistic concurrency;
- queue redelivery;
- crash между mutation и receipt;
- failover и retry storms.

Сохранять минимальный reproduction и seed, если инструмент его предоставляет.

## 10. Security, performance и accessibility

### Security

Выводить security tests из threat model. Как минимум проверить применимые сценарии:

- unauthenticated и unauthorized access;
- cross-tenant data access;
- input injection и unsafe file handling;
- secret/PII exposure в output/logs;
- CSRF/SSRF/XSS либо platform-specific threats;
- privilege escalation и forbidden mutation;
- dependency/config regression.

### Performance

Сначала зафиксировать реальный workload и SLO/constraint. Затем измерять:

- latency distribution, а не один удачный request;
- throughput и saturation;
- resource/cost growth;
- cold start и tail behavior;
- degradation при dependency failure.

Не объявлять произвольные universal limits. Threshold должен следовать из user journey, capacity plan или подтверждённого baseline.

### Accessibility

Для визуальных интерфейсов сочетать automated checks и реальную keyboard/screen-reader проверку critical journey. Проверять focus, labels, semantics, contrast, errors, reduced motion и responsive reflow.

Для CLI проверять exit codes, stderr/stdout, help, non-interactive use и доступность машинно-читаемого output. Для mobile/desktop учитывать platform accessibility и lifecycle states.

## 11. Test data и изоляция

Test data должна иметь owner, provenance, classification и cleanup/retention policy.

Использовать:

- минимальные versioned fixtures;
- synthetic data, явно маркированные как test-only;
- anonymized/approved samples, если synthetic data не воспроизводит риск;
- уникальный namespace на run;
- deterministic clock/IDs только внутри test composition;
- безопасный cleanup с точным target.

Не копировать production PII в test environment без legal/security основания. Не позволять параллельным runs делить mutable state без явного isolation contract.

## 12. Flakiness

Flaky test — defect теста, продукта или environment, а не обычный шум.

При нестабильности:

1. сохранить exact run, seed, timing и environment;
2. определить, детерминирован ли ожидаемый behavior;
3. локализовать race, shared state, clock, network или provider variance;
4. исправить причину либо честно перевести проверку в statistical/eval protocol;
5. не повышать retry count без stop rule и наблюдения dispersion.

Quarantine допустим только с owner, issue, expiry и отдельным release решением. Required check нельзя молча исключать.

## 13. Debugging feedback loop

Диагностировать до patch:

```text
reproduce → collect evidence → localize boundary → form hypothesis → falsify alternatives → Red → minimal fix → regression → stronger-path verification
```

Сначала проверить recent diff, exact error, input/state и boundary receipts. Не менять несколько слоёв одновременно.

BugSpec должен содержать:

- expected и observed behavior;
- минимальный reproduction;
- evidence и probable boundary;
- included/excluded scope;
- first Red;
- required regression/evidence;
- rollback и stop condition.

После production defect добавить минимальный regression на правильном уровне. Не писать E2E, если unit test точнее ловит причину; не ограничиваться unit, если defect возник только на integration boundary.

Если fix проходит отдельную интеграцию, candidate QA и release, применить [`bug-repair.md`](bug-repair.md). Авторитетный `QA PASS` привязывать к immutable candidate после integration; проверка другой Dev-сборки является только preview evidence.

Для серии несрочных minor fixes отделять repair verification от release verification: каждый fix получает собственный Red, targeted/affected evidence и при необходимости `PREVIEW PASS`, затем входит в `READY_FOR_BATCH`. После freeze общего cumulative head один раз пересчитать aggregate impact, выбрать применимые Registry gates и получить candidate-bound evidence для всего batch. Не запускать полный release pipeline после каждого небольшого fix и не переносить preview approval на итоговый candidate.

## 14. Evidence и release matrix

Создать короткую матрицу, а не длинный список команд:

| Risk/criterion | Required level | Command/procedure | Candidate/environment | Result/ref | Blocking |
|---|---|---|---|---|---|
| core behavior | unit + integration | ... | ... | ... | yes |
| critical journey | E2E | ... | ... | ... | yes |
| authorization | integration/security | ... | ... | ... | yes |
| performance constraint | load/capacity | ... | ... | ... | by policy |
| accessibility | automated + manual | ... | ... | ... | by policy |

Release verdict относится только к exact source/config/schema/environment evidence. После значимого изменения затронутые результаты становятся stale.

Для release batch матрица перечисляет batch manifest и cumulative diff. Совместимое engineering evidence отдельных fixes можно переиспользовать; проверки, зависящие от artifact, environment или совокупного взаимодействия изменений, должны быть fresh для итогового immutable candidate.

Отдельно проверить completeness: release intent manifest должен сопоставлять каждый принятый handoff и capability с provenance, automated evidence и применимым human QA scenario. Green выбранного head, существование workflow-файлов или smoke нескольких соседних функций не доказывают, что весь принятый product scope вошёл в candidate.

Fail, unresolved skip/todo, missing credential или unverified required path нельзя выдавать за Green. Advisory limitation должна быть видимой и не скрывать red line.

`Regression Registry` хранит долговечную policy и ссылки на native tests. Эта матрица хранит selection и evidence для текущего candidate. Не смешивать их и не записывать pass-флаги в Registry.

## 15. Граница с AI-проверками

Для deterministic AI-adjacent behavior использовать обычные tests: schema, permission, tool args, budgets, state transitions и side effects.

Прочитать [`evals.md`](evals.md), если проверяется вероятностное AI behavior, prompt/model/context/retrieval, semantic judge или acceptance threshold.

Прочитать [`testing-harness.md`](testing-harness.md), если впервые испытывается consequential workflow, multi-agent system, agent role или skill и нужны calibration checkpoints, autonomous repair и replay.

Не копировать весь EvalSuite или TestingHarness в обычный QualityPlan. Сослаться на их version/status и включить только результат соответствующего release gate.

## 16. Шаблон QualityPlan

```markdown
# QualityPlan: <scope>

Delivery mode: EXPLORE | BUILD
Risk: LOW | STANDARD | CRITICAL
Candidate/environment:
Registry path/version:

## Risks
Critical journey:
Forbidden outcomes:
Expensive boundaries:

## Registry selection
Selected Registry IDs:
Exclusions with rationale:

## Release composition
Release intent / accepted handoff IDs:
Composition receipt / provenance:
Capability and QA coverage:

## Test matrix
| Criterion/risk | Test level | Command/procedure | Blocking | Evidence ref |
|---|---|---|---|---|

## Data and environment
Fixtures/provenance/classification:
Isolation/cleanup:
Required integrations/credentials:

## Non-functional
Security:
Performance/capacity:
Accessibility:
Recovery/concurrency:

## AI-specific routing
EvalSuite: not_applicable | <version/status>
TestingHarness: not_applicable | <version/status>

## Release
Known gaps/constraints:
Verdict and owner:
```

## 17. Self-check

1. Проверки выведены из рисков, а не из привычного checklist?
2. Первый Red воспроизводит observable behavior или defect?
3. Выбран самый дешёвый достаточный уровень теста?
4. Реальные boundaries проверены integration evidence?
5. Есть один полный critical journey?
6. Negative, permission и recovery paths покрыты по риску?
7. Test doubles остаются test-only и не выданы за live evidence?
8. Test data разрешена, изолирована и очищается безопасно?
9. Flaky check не превращён в pass retries?
10. Security tests следуют threat model?
11. Performance criteria следуют SLO/workload, а не выдуманному числу?
12. Accessibility проверена для затронутого interface?
13. Required fail/skip/todo/missing evidence блокирует release?
14. AI behavior правильно направлено в EvalSuite или TestingHarness?
15. Применимые blocking Registry entries выбраны и исполнены?
16. Release intent reconciled с фактическим candidate без `MISSING` handoffs?
17. Capability и QA coverage проверяют принятый behavior, а не наличие файлов?
18. Verdict относится к exact candidate и не устарел?
