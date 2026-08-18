# Bug repair: от воспроизведения до точного релиза

## Содержание

1. Назначение
2. Базовый протокол
3. Зафиксировать BugReport
4. Изолировать repair
5. Создать Primary Red
6. Выбрать repair owner
7. Проверить исправление
8. Интегрировать в cumulative head
9. Собрать immutable candidate
10. Провести QA и получить ACCEPT
11. Выполнить release adapter
12. Управлять evidence и stale state
13. Масштабировать строгость
14. Red lines
15. Универсальный BugRepairContract
16. Пример Schema adapter
17. Self-check

## 1. Назначение

Использовать этот протокол для бага, который требуется не только исправить в коде, но и безопасно довести до пользовательской проверки и релиза.

Цель — сохранить четыре разные истины:

- defect воспроизведён;
- code fix прошёл engineering verification;
- пользователь проверил exact candidate;
- release controller установил именно принятый candidate и подтвердил результат.

Не считать локальный Green, Dev-preview, `QA PASS` другого build или устное «выглядит нормально» доказательством готовности релиза.

## 2. Базовый протокол

```text
BugReport
  → isolated repair workspace
  → Primary Red
  → bounded repair
  → targeted + risk-based verification
  → integration into clean cumulative head
  → immutable candidate
  → candidate QA
  → exact ACCEPT
  → release adapter
  → readback | rollback
```

Каждый переход привязывать к exact source, artifact и evidence. Не переносить approval между разными candidate hashes.

Если реализация заблокирована отсутствующим repository или доступом, всё равно дать короткий исполнимый контракт: `BugReport → Primary Red → targeted/risk-based verification → cumulative integration → immutable candidate QA → exact ACCEPT → release adapter`. Не выдумывать команды или evidence.

## 3. Зафиксировать BugReport

Самостоятельно извлечь доступные данные и запросить только действительно блокирующее.

Минимум:

- expected и observed behavior;
- воспроизводимый scenario/input;
- environment, version/build и timestamp;
- run/request/trace ID, если существует;
- screenshot/video/log fragment, если помогает увидеть symptom;
- impact, affected users/data и workaround;
- reporter и источник expectation.

Run ID и screenshot полезны, но не обязательны для каждого бага. Не блокировать воспроизводимый defect из-за отсутствия декоративного поля.

До patch различить подтверждённые facts, гипотезы и неизвестные. Не объявлять root cause по одному screenshot.

## 4. Изолировать repair

Сначала проверить project instructions, status и существующие dirty changes.

Отдельный branch/worktree предпочтителен, когда:

- main/cumulative head должен оставаться стабильным;
- repair выполняет сабагент или другой owner;
- параллельно интегрируются другие изменения;
- fix затрагивает несколько файлов или требует Dev-build;
- нужен точный independent diff и disposable environment.

Для тривиального локального fix отдельный worktree не обязателен, если repository workflow разрешает текущую branch, worktree чист и isolation ничего не улучшает.

Называть workspace по defect/change, а не обязательно `feature-*`. Не трогать main напрямую, если утверждён integration-owner flow.

## 5. Создать Primary Red

До production patch добавить или запустить один главный тест, который:

- воспроизводит observable defect;
- падает на baseline по ожидаемой причине;
- проверяет контракт, а не внутреннюю реализацию;
- становится regression после fix;
- находится на самом дешёвом достаточном уровне.

Если bug возникает только на boundary, дополнить Primary Red integration/E2E probe. Не заменять реальную причину source-string assertion или mock success.

Сохранить baseline candidate и Red evidence. Если defect не воспроизводится, продолжать diagnosis, а не писать speculative patch.

## 6. Выбрать repair owner

Сабагент не обязателен. Делегировать bounded repair, когда это сохраняет контекст оркестратора, имеет независимый write scope и отдельно проверяемый результат.

Передать `SubagentTaskContract`:

- BugReport и Primary Red;
- allowed read/write scope;
- frozen invariants;
- запрещённое ослабление tests;
- required verification;
- stop/escalation conditions.

Оркестратор сохраняет root-cause decision, approvals, integration и final verification. Repairer не принимает собственный fix и не расширяет scope молча.

## 7. Проверить исправление

После минимального Green выполнить по impact:

1. Primary Red → Green;
2. targeted tests затронутого модуля;
3. соседние regressions и реальные boundaries;
4. project-required lint/type/build/security checks;
5. полный verify только когда его требует repository policy, shared/core impact или risk mode.

Не привязывать универсальный канон к `npm run verify`. Использовать exact commands проекта.

Tests не ослаблять, required checks не отключать, retry не выдавать за исправление flakiness. Зафиксировать exact commit/config/environment каждого результата.

Опциональный Dev-preview до интеграции полезен для ранней обратной связи, но не создаёт release-grade `QA PASS`.

## 8. Интегрировать в cumulative head

Integration owner:

1. проверяет diff, scope и evidence repair workspace;
2. интегрирует изменение в чистый актуальный cumulative head;
3. разрешает conflicts без потери invariants;
4. повторяет Primary Red/Green и affected-path verification;
5. замораживает точный candidate source commit.

Summary repairer или Green на старом head не являются proof после integration. Изменение cumulative head делает несовместимое evidence stale.

Не интегрировать unrelated dirty changes и не переписывать main history.

## 9. Собрать immutable candidate

Из clean cumulative head один раз собрать immutable candidate:

- candidate ID и artifact hash;
- exact source commit;
- config/schema/dependency versions;
- build logs и required evidence refs;
- supported scope и known constraints;
- install/deploy, readback и rollback metadata.

«Один раз» означает один build на конкретный frozen head. Если source/config/schema изменились, старый candidate не обновлять: создать новый ID, а его QA/ACCEPT начать заново.

Не модифицировать artifact после hash/signing. Не собирать release повторно из другого workspace после QA.

## 10. Провести QA и получить ACCEPT

Авторитетный human QA проводить на isolated runtime именно immutable candidate после integration.

QA evidence содержит:

- candidate ID/hash;
- scenario и environment;
- expected/observed result;
- screenshots/run IDs при необходимости;
- `QA PASS | QA FAIL` и authenticated approver;
- limitations и timestamp.

Human QA обязательна, если acceptance зависит от UX, визуального результата, продукта или другого смысла, который не закрыт automated evidence. Для полностью deterministic low-risk change она может быть `not_applicable` по project policy.

После required `QA PASS` получить точный `ACCEPT`, привязанный к candidate ID/hash, release scope и evidence. Не трактовать «ок», сказанное про Dev-preview или другой build, как ACCEPT.

До required ACCEPT не выполнять installation/deploy/external mutation.

## 11. Выполнить release adapter

Universal release controller принимает только accepted immutable candidate и выполняет platform-specific шаги:

- проверить artifact integrity/signature/provenance;
- проверить exact target и authority;
- сохранить previous known-good;
- установить/deploy с ограниченным blast radius;
- подтвердить active version и critical behavior readback;
- проверить single-active-version/unique-target invariant, если применимо;
- rollback/compensation при fail;
- сохранить ReleaseRecord.

Названия команд, codesign, package manager, app location, Launchpad, container registry или cloud rollout принадлежат project adapter, а не универсальному канону.

## 12. Управлять evidence и stale state

Evidence graph связывает:

```text
BugReport → Primary Red → repair commit → cumulative head
→ candidate hash → QA PASS → ACCEPT → ReleaseRecord
```

Считать downstream evidence stale, если меняется его dependency:

- patch после tests → повторить affected verification;
- cumulative head после integration → пересобрать candidate;
- candidate hash после QA → QA PASS и ACCEPT недействительны;
- target/config после ACCEPT → повторить release preflight или запросить новое approval по risk policy.

Не повторять неизменённые дорогие этапы без причины. Переиспользовать trusted evidence только при совпадающих versions/hashes и доказанной совместимости.

## 13. Масштабировать строгость

### `BUILD/lite`

Primary Red, bounded fix, targeted verification и обычный repository integration flow. Human QA и отдельный release controller — только по применимости.

### `BUILD/standard`

Изолированный repair предпочтителен; affected-path verification, clean cumulative integration, immutable candidate и explicit release evidence обязательны для пользовательского релиза.

### `CRITICAL`

Требовать separation of duties, independent verifier, authenticated QA/ACCEPT, signed/traceable artifact, canary/blast-radius control, readback и проверенный rollback/compensation.

Не применять desktop-release церемонию к documentation-only или low-risk server fix. Не сокращать exact-candidate chain для денег, PII или необратимых mutations.

## 14. Red lines

Блокировать соответствующий gate, если:

- defect не воспроизведён и patch остаётся speculative;
- Primary Red отсутствует или падает не по причине бага;
- assertion/test ослаблен ради Green;
- repair вышел за утверждённый scope;
- integration выполнена в dirty/unknown head;
- candidate не immutable или не связан с source commit;
- authoritative QA выполнялась на другом build;
- QA/ACCEPT не содержит exact candidate identity;
- artifact изменён после signing/hash/QA;
- required ACCEPT отсутствует до external mutation;
- release adapter не подтверждает active version/readback/rollback;
- platform-specific procedure выдана за универсальную без project evidence.

## 15. Универсальный BugRepairContract

```markdown
# BugRepairContract: <defect> v<version>

## Report
Expected/observed/impact:
Scenario/environment/version:
Run IDs/screenshots/evidence:

## Repair
Baseline/workspace/write scope:
Primary Red:
Repair owner/subagent contract:
Targeted/affected/full verification policy:

## Integration
Integration owner/cumulative head:
Post-integration evidence:

## Candidate and QA
Candidate ID/source/artifact hash:
QA policy/result/evidence:
Exact ACCEPT/approver:

## Release
Adapter/target/authority:
Integrity/readback/rollback:
ReleaseRecord/verdict:
```

Заполнять только применимые поля. Отсутствующий screenshot не заменять выдуманным; отсутствующий required approval считать blocker.

## 16. Пример Schema adapter

Для desktop-приложения Schema универсальные роли могут отображаться так:

- `release:prepare` собирает immutable candidate из clean cumulative head и выдаёт subject/evidence;
- пользователь запускает isolated candidate и даёт `QA PASS`, связанный с candidate hash;
- точный `ACCEPT` разрешает изменение `/Applications/Schema.app`;
- `schema-release-controller` проверяет codesign, устанавливает candidate, выполняет readback/rollback и подтверждает единственный экземпляр Schema в Launchpad.

Это пример adapter contract. Другой проект подставляет собственные commands, artifact target и platform checks.

## 17. Self-check

1. BugReport описывает expected/observed и воспроизводимый scenario?
2. Isolation соразмерна риску и сохраняет main/dirty worktree?
3. Primary Red падает на baseline по правильной причине?
4. Repair owner имеет bounded scope и не принимает собственный fix?
5. Verification выбрана по impact, а не по привычной команде?
6. Integration выполнена в clean current cumulative head?
7. Immutable candidate однозначно связан с source/config?
8. Авторитетный QA проверяет именно этот candidate?
9. ACCEPT содержит candidate identity, scope и approver?
10. До required ACCEPT не было install/deploy mutation?
11. Release adapter доказал integrity, active version, readback и rollback?
12. Stale evidence инвалидируется только по реальным dependencies?
13. Platform-specific детали не стали universal requirement?
14. Пользователю виден один следующий gate?
