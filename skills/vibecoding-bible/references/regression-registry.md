# Regression Registry: библиотека обязательных проверок

## 1. Назначение

`Regression Registry` — version-controlled индекс проверок, которые защищают долговечные product/system invariants и могут блокировать выпуск.

Он нужен, чтобы:

- не терять тесты, появившиеся из bugs, incidents, contracts и threat models;
- выбирать минимальный достаточный набор по change impact;
- не позволять агенту молча пропустить известный critical regression;
- связывать release verdict с точными commands и evidence;
- сохранять инженерную память независимо от конкретной сессии или агента.

Registry не является копией test suite и не означает «запускать всё всегда».

## 2. Что хранит Registry

Разделять три слоя:

```text
Registry entry → зачем и когда проверка обязательна
Native test/eval/harness artifact → исполняемая проверка
Evidence record → результат запуска на exact candidate
```

В Registry хранить metadata и ссылки. Реальный unit/integration/E2E test оставлять рядом с кодом по conventions проекта. Eval cases оставлять внутри versioned EvalSuite. Workflow cases — внутри frozen TestCase/regression pack.

| Проверка | Что указывает Registry entry |
|---|---|
| Обычный software test | Native test path + command |
| AI behavior | EvalSuite version + gate command |
| Workflow/agent/skill | Frozen TestCase pack + harness procedure |
| Human/platform gate | Versioned manual procedure + approver policy |

Не хранить в Registry `passed: true`, raw logs, screenshots или историю всех runs. Они быстро устаревают и принадлежат CI/release evidence.

## 3. Где хранить

Сначала использовать существующий канонический registry проекта, если он уже есть.

Default для нового проекта:

```text
.vibecoding/quality/required-tests.yaml
```

Требования:

- файл находится в version control;
- один root registry предпочтительнее нескольких несвязанных списков;
- paths и commands разрешаются относительно repository root;
- изменение Registry проходит review как изменение release policy;
- secrets, PII и большие fixtures в manifest не помещать.

Для monorepo использовать root registry с package/component ownership. Делить на package registries только когда команды действительно автономны; root index должен оставаться единой точкой обнаружения.

## 4. Когда создавать и обновлять

Создать Registry, когда проект имеет хотя бы один долговечный blocking regression или несколько независимых test commands, выбор которых агент иначе должен угадывать.

Обновить его при:

- исправлении production/user-visible defect;
- incident postmortem или discovered security failure;
- новом critical contract, permission или data invariant;
- добавлении обязательного integration/E2E/recovery check;
- появлении EvalSuite или TestingHarness gate;
- изменении команды, location, owner, applicability или lifecycle status;
- признании проверки stale, quarantined, superseded или deprecated.

Не создавать Registry ради disposable `EXPLORE` spike без production claim.

## 5. Схема записи

Минимальная запись:

```yaml
id: payments.no-duplicate-charge
protects: Один заказ не создаёт два денежных списания
source:
  type: bug | incident | requirement | contract | handoff | threat | eval | harness
  ref: incident-142
level: integration
location: tests/payments/idempotency.test.ts
command: npm test -- idempotency
blocking: true
risk: [STANDARD, CRITICAL]
applicability:
  paths: [src/payments/**]
  components: [payments]
  contracts: [payment-state-v2]
  always_on: false
environment: test
data:
  fixtures: [payment-timeout]
  classification: synthetic
owner: payments
status: active
quarantine: null
stale_when:
  - payment state machine changes
supersedes: null
```

Допустимые `level`: `static`, `unit`, `component`, `contract`, `integration`, `e2e`, `security`, `performance`, `accessibility`, `eval`, `harness`, `manual`.

`command` может быть deterministic procedure ref для manual/platform check. Не выдумывать команду, если repository ещё не определил исполняемый path; держать запись `draft`, пока он не появится.

ID делать стабильным и смысловым. Не привязывать его к номеру строки или временному имени branch.

## 6. Admission policy

Добавлять проверку, если она защищает хотя бы одно:

- durable product/domain invariant;
- ранее подтверждённый defect или incident;
- дорогой failure mode на реальной boundary;
- permission, tenancy, privacy или security guarantee;
- migration/recovery/rollback capability;
- обязательный AI slice или workflow acceptance gate;
- явно принятый feature handoff или product capability, потеря которых сделает release неполным;
- customer/contractual release requirement.

Не добавлять:

- duplicate существующей проверки без нового coverage;
- assertion implementation detail, не защищающий behavior;
- случайный flaky test без понятного expected contract;
- одноразовый debug probe;
- test, который проходит только на hardcoded fixture и не ловит заявленный риск;
- entry без owner или executable verification path для `active` status.

Admission утверждает integration/quality owner. Автор теста может предложить запись, но не должен единолично объявлять собственный слабый check release gate при risk `CRITICAL`.

## 7. Выбор применимых проверок

Перед изменением:

1. получить reality snapshot и change scope;
2. определить затронутые paths, components, contracts, data, permissions и integrations;
3. выбрать все `active` entries, чья applicability пересекается с impact;
4. добавить `always_on` entries для соответствующего risk/gate;
5. создать Primary Red, даже если нового defect ещё нет в Registry;
6. записать selected IDs и причины исключения пограничных entries в QualityPlan/ProjectContract.

Не запускать весь Registry по умолчанию. Сначала выполнить cheapest trustworthy selected checks; усилить до boundary/E2E/release evidence по риску.

Если impact невозможно честно ограничить — расширить selection или остановиться для clarification. Не исключать тест только ради скорости.

## 8. Выполнение и release gate

Использовать Registry в трёх точках:

### BUILD

- запустить Primary Red и выбранные быстрые entries;
- после Green выполнить affected regressions;
- обновить Registry при появлении нового долговечного invariant.

### VERIFY

- выполнить все применимые blocking entries на требуемых environments;
- проверить реальные boundaries и candidate identity;
- сохранить evidence отдельно от manifest.

### SHIP

- заново выбрать entries по final cumulative candidate impact;
- сверить release intent с integrated/deferred/superseded handoffs;
- убедиться, что все применимые blocking entries имеют fresh evidence;
- подтвердить accepted capabilities behavioral проверками на exact candidate, а не только существованием файлов;
- любой fail, unresolved skip, expired quarantine или missing required environment блокирует release.

Registry определяет policy, но не доказывает исполнение. ReleaseRecord должен ссылаться на exact run evidence.

## 9. Жизненный цикл записи

Использовать статусы:

- `draft` — предложена, но ещё не является gate;
- `active` — применяется при matching impact;
- `quarantined` — временно неисправна; не считается pass;
- `superseded` — заменена другой entry с явной ссылкой;
- `deprecated` — invariant или product path удалён с доказательством.

Quarantine требует:

- reason/issue;
- owner;
- expiry;
- affected scope;
- compensating control;
- отдельный release verdict.

Удаление или ослабление blocking entry является изменением release policy. Требовать rationale и evidence, что invariant исчез, перенесён или лучше защищён другой проверкой.

## 10. Evidence и stale state

Evidence record связывать с:

- Registry version/commit и selected entry IDs;
- exact source/artifact/config/schema candidate;
- command/procedure и environment;
- timestamp, result и artifact/log reference;
- authenticated runner/approver по риску.

Результат становится stale, если изменилось то, от чего он зависит: source path, protected contract, fixture, environment, toolchain, model/context/rules, judge или Registry entry.

Не инвалидировать дорогой evidence без dependency change. Не переиспользовать pass при несовпадающих hashes или недоказанной совместимости.

## 11. Связь с Bug Repair

После Green оценить Primary Red для admission:

1. подтверждён ли defect;
2. защищает ли test долговечный observable invariant;
3. ловит ли он root cause на правильном уровне;
4. есть ли owner и стабильная команда;
5. нужна ли более сильная boundary entry.

Если да — добавить `active` entry со `source.type: bug|incident` до integration/release. Если нет — сохранить test нативно, но записать краткую причину отказа в BugSpec.

Не добавлять каждый локальный unit test в Registry. Registry хранит обязательные gates, а не каталог всей test suite.

## 12. Связь с EvalSuite и TestingHarness

Для AI capability создать одну Registry entry, указывающую на versioned EvalSuite и её gate command/status policy. Не дублировать каждый eval case в root manifest.

Для workflow/agent/skill создать entry, указывающую на frozen TestCase/regression pack и harness procedure. Accepted/rejected/defect cases остаются внутри pack; Registry определяет, когда pack обязателен.

Примеры:

```yaml
level: eval
location: evals/support-summary/v3
command: npm run eval:support-summary
```

```yaml
level: harness
location: harness/research-workflow/v2
command: npm run harness:research
```

## 13. CI и validation

Минимальная automation должна проверять:

- YAML/schema parse;
- unique stable IDs;
- существование locations и commands/procedure refs;
- допустимые status/mode/level;
- owner для active entries;
- quarantine reason/owner/expiry;
- отсутствие secrets и запрещённых PII;
- selected blocking entries действительно исполнены до release verdict.

Перед исполнением просмотреть Registry diff. Новая или изменённая `command` является изменением executable project policy; не запускать её как доверенную только потому, что она находится в manifest.

Не строить отдельный framework, если CI проекта может прочитать manifest небольшим script. Сначала достаточно versioned YAML, schema validation и явного selection report.

Skill поставляет готовую реализацию этих проверок:

```bash
python3 scripts/validate_registry.py path/to/registry.yaml --root .
```

Схема записи — [`assets/schemas/registry-entry.schema.json`](../assets/schemas/registry-entry.schema.json);
схема eval case — [`assets/schemas/eval-case.schema.json`](../assets/schemas/eval-case.schema.json).
Валидатор проверяет schema, уникальность id, существование `location`, наличие `command`
или `procedure` для исполняемых levels, owner у `active`, срок и полноту quarantine,
целостность `supersedes` и отсутствие secrets. Ненулевой код возврата блокирует gate.
Валидатор не заменяет прогон самих проверок: он подтверждает целостность манифеста, а не поведение системы.

## 14. Red lines

Блокировать соответствующий gate, если:

- применимый `active + blocking` test failed, skipped или не запускался;
- entry удалена/ослаблена только ради Green;
- Registry содержит fabricated command, location или evidence;
- pass хранится в manifest и переиспользуется без candidate identity;
- test code скопирован в Registry вместо ссылки на source of truth;
- production bug не рассмотрен для admission;
- quarantine не имеет owner, issue или expiry;
- EvalSuite/harness cases продублированы и начали расходиться;
- selection исключает matching critical entry без rationale;
- capability entry доказывает только наличие source-файла и не проверяет accepted behavior;
- Registry Green используется вместо отдельной проверки полноты release intent;
- agent запускает всё без impact analysis, создавая постоянный waste.

## 15. Минимальный рабочий slice

Для первого внедрения:

1. скопировать [`assets/templates/required-tests.yaml`](../assets/templates/required-tests.yaml) в `.vibecoding/quality/required-tests.yaml`;
2. добавить один существующий critical regression;
3. проверить schema/path/command;
4. связать его с одним QualityPlan;
5. запустить на exact candidate и сохранить evidence ref;
6. добавить selection в CI только после доказанной пользы.

Не мигрировать сотни тестов сразу. Начать с нескольких проверок, которые уже защищают дорогие failures.

## 16. Self-check

Общий self-check — в [`../SKILL.md`](../SKILL.md). Здесь только то, что проверяется именно этим файлом.

1. IDs стабильны и unique?
2. Каждая active entry защищает observable invariant?
3. Native location и executable command/procedure существуют?
4. Applicability позволяет выбрать минимальный достаточный набор?
5. Quarantine имеет reason, owner, expiry и control?

