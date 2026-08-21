# Bug repair: от воспроизведения до точного релиза

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
  → READY_FOR_BATCH | urgent hotfix
  → release intent reconciliation
  → composition receipt + batch freeze
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

После Green рассмотреть Primary Red для admission в [`regression-registry.md`](regression-registry.md). Добавлять entry только если test защищает долговечный invariant; иначе сохранить rationale в BugSpec.

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

Опциональный Dev-preview до интеграции полезен для ранней обратной связи. Пользователь может дать `PREVIEW PASS`, подтверждающий исправление конкретного scenario на конкретной preview-сборке. Это не release-grade `QA PASS` и не `ACCEPT`.

## 8. Интегрировать в cumulative head

Integration owner:

1. проверяет diff, scope и evidence repair workspace;
2. интегрирует изменение в чистый актуальный cumulative head;
3. разрешает conflicts без потери invariants;
4. повторяет Primary Red/Green и affected-path verification;
5. проверяет Registry delta и applicable blocking entries;
6. замораживает точный candidate source commit.

Summary repairer или Green на старом head не являются proof после integration. Изменение cumulative head делает несовместимое evidence stale.

Не интегрировать unrelated dirty changes и не переписывать main history.

## 9. Выбрать delivery lane и сформировать release batch

Не связывать каждый небольшой fix с отдельным дорогим релизом. После integration выбрать одну из двух дорожек.

### Release Train — default для несрочных исправлений

Поместить проверенный fix в очередь со статусом `READY_FOR_BATCH`. Для каждой записи сохранить:

- defect/change ID, risk и user-visible scope;
- handoff ID, acceptance criteria и статус в release intent;
- repair и cumulative commits;
- Primary Red, targeted/affected evidence и Registry delta;
- `PREVIEW PASS`, если требовался human preview;
- dependencies, rollout/rollback и owner;
- причину включения в выбранный release batch.

Release trigger задаётся policy проекта: расписанием, допустимым временем ожидания, готовностью связанной группы изменений или явным решением owner. Не придумывать универсальное число fixes или дней. Не держать очередь без owner и максимального срока ожидания.

### Release Composition Gate

Green выбранного head доказывает его внутреннюю корректность, но не полноту относительно принятого release intent. До freeze создать короткий versioned release intent manifest со всеми handoffs, явно принятыми в этот batch.

Для каждого handoff сохранить:

- stable ID, source/base identity и acceptance reference;
- user-visible capabilities и acceptance criteria;
- статус `INTEGRATED | DEFERRED | SUPERSEDED | MISSING`;
- cumulative integration identity либо explicit defer/supersede decision с owner;
- provenance proof и candidate-level capability evidence.

Release Composition Gate проходит, только если каждый handoff из release intent:

1. интегрирован в frozen cumulative head либо явно отложен/заменён владельцем;
2. имеет доказательство происхождения: native ancestry/reachability или явное mapping после squash/rebase/reimplementation;
3. имеет behavioral capability proof на exact candidate; наличие файлов или Green другого branch недостаточно;
4. присутствует в QA coverage matrix, если acceptance требует human/product verification.

Не включать автоматически все исторические feature branches. Gate сверяет только явно утверждённый release intent, но не позволяет молча потерять элемент этого intent.

Перед candidate build integration owner:

1. выбирает только готовые совместимые изменения;
2. сверяет release intent со всеми принятыми handoffs и закрывает `MISSING`;
3. удаляет, откатывает или изолирует change с unresolved blocker, не удерживая без причины весь train;
4. замораживает exact cumulative head, batch/release intent manifests и composition receipt;
5. заново рассчитывает совокупный impact;
6. выбирает все применимые blocking и `always_on` Registry entries для cumulative diff;
7. строит QA matrix из acceptance criteria принятых capabilities;
8. переиспользует совместимое engineering evidence, но получает fresh candidate-bound evidence там, где этого требует risk или environment.

Затем один immutable candidate, один release QA/ACCEPT и один deploy/readback/rollback покрывают весь batch. Финальная QA проверяет применимые изменённые scenarios и critical journeys, а не механически повторяет каждую ручную preview-проверку.

### Urgent hotfix

Не ждать train при активной уязвимости, потере/повреждении данных, ошибке денег или permissions, существенной недоступности либо другом явно срочном impact. Hotfix ускоряет очередь и ограничивает scope, но не отменяет Primary Red, required evidence, exact candidate, applicable approval, readback и rollback/compensation.

`PREVIEW PASS` никогда не становится `ACCEPT` автоматически. Если frozen batch изменился, создать новый candidate и инвалидировать только evidence, реально зависящее от изменившегося subject.

## 10. Собрать immutable candidate

Из clean cumulative head один раз собрать immutable candidate:

- candidate ID и artifact hash;
- exact source commit;
- release intent/batch manifest и composition receipt identities;
- config/schema/dependency versions;
- build logs и required evidence refs;
- supported scope и known constraints;
- install/deploy, readback и rollback metadata.

«Один раз» означает один build на конкретный frozen head. Если source/config/schema изменились, старый candidate не обновлять: создать новый ID, а его QA/ACCEPT начать заново.

Не модифицировать artifact после hash/signing. Не собирать release повторно из другого workspace после QA.

## 11. Провести QA и получить ACCEPT

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

Состояние доставки вести словарём `release_state` из [`vocabulary.md`](vocabulary.md):
immutable candidate — `CANDIDATE`, точный ACCEPT — `ACCEPTED`, выполненные deploy и
readback — `RELEASED`. Не объявлять `RELEASED` по факту сборки кандидата.

## 12. Выполнить release adapter

Universal release controller принимает только accepted immutable candidate и выполняет platform-specific шаги:

- проверить artifact integrity/signature/provenance;
- проверить привязку candidate к release intent и прошедшему composition receipt;
- проверить exact target и authority;
- сохранить previous known-good;
- установить/deploy с ограниченным blast radius;
- подтвердить active version и critical behavior readback;
- проверить single-active-version/unique-target invariant, если применимо;
- rollback/compensation при fail;
- сохранить ReleaseRecord.

Названия команд, codesign, package manager, app location, Launchpad, container registry или cloud rollout принадлежат project adapter, а не универсальному канону.

## 13. Управлять evidence и stale state

Evidence graph связывает:

```text
BugReport → Primary Red → repair commit → cumulative head
→ READY_FOR_BATCH/hotfix → release intent → composition receipt
→ batch manifest → candidate hash
→ QA PASS → ACCEPT → ReleaseRecord
```

Считать downstream evidence stale, если меняется его dependency:

- patch после tests → повторить affected verification;
- cumulative head после integration → пересобрать candidate;
- release intent или handoff decision после composition → создать новую candidate identity и повторить affected composition/QA/approval;
- candidate hash после QA → QA PASS и ACCEPT недействительны;
- target/config после ACCEPT → повторить release preflight или запросить новое approval по risk policy.

Не повторять неизменённые дорогие этапы без причины. Переиспользовать trusted evidence только при совпадающих versions/hashes и доказанной совместимости.

## 14. Масштабировать строгость

### `BUILD` при risk `LOW`

Primary Red, bounded fix, targeted verification и обычный repository integration flow. Для несрочного minor fix предпочитать `READY_FOR_BATCH`, а не отдельный release. Human QA и отдельный release controller — только по применимости.

### `BUILD` при risk `STANDARD`

Изолированный repair предпочтителен; affected-path verification, clean cumulative integration, immutable candidate и explicit release evidence обязательны для пользовательского релиза.

### Risk `CRITICAL`

Требовать separation of duties, independent verifier, authenticated QA/ACCEPT, signed/traceable artifact, canary/blast-radius control, readback и проверенный rollback/compensation.

Не применять desktop-release церемонию к documentation-only или low-risk server fix. Не сокращать exact-candidate chain для денег, PII или необратимых mutations.

## 15. Red lines

Блокировать соответствующий gate, если:

- defect не воспроизведён и patch остаётся speculative;
- Primary Red отсутствует или падает не по причине бага;
- assertion/test ослаблен ради Green;
- repair вышел за утверждённый scope;
- integration выполнена в dirty/unknown head;
- candidate не immutable или не связан с source commit;
- candidate identity не связана с release intent и composition receipt;
- authoritative QA выполнялась на другом build;
- QA/ACCEPT не содержит exact candidate identity;
- artifact изменён после signing/hash/QA;
- required ACCEPT отсутствует до external mutation;
- `PREVIEW PASS` выдан за release QA или ACCEPT;
- несрочный minor fix без причины запускает полный отдельный release pipeline;
- срочный consequential defect оставлен ждать обычный batch;
- batch frozen без manifest, aggregate impact selection или owner;
- release intent содержит `MISSING` либо принятый handoff исчез без explicit defer/supersede decision;
- provenance проверяет только чистоту выбранного head, но не включение handoffs;
- capability gate проверяет наличие файлов вместо принятого behavior;
- QA matrix не покрывает user-visible acceptance criteria release intent;
- release adapter не подтверждает active version/readback/rollback;
- platform-specific procedure выдана за универсальную без project evidence.

## 16. Универсальный BugRepairContract

```markdown
# BugRepairContract: <defect> v<version>

## Report
Expected/observed/impact:
Scenario/environment/version:
Run IDs/screenshots/evidence:

## Repair
Baseline/workspace/write scope:
Primary Red:
Registry admission / entry ID / rejection rationale:
Repair owner/subagent contract:
Targeted/affected/full verification policy:

## Integration
Integration owner/cumulative head:
Post-integration evidence:

## Delivery lane
PREVIEW PASS/evidence:
READY_FOR_BATCH | URGENT_HOTFIX:
Batch ID/manifest/trigger/maximum wait:
Release intent manifest / accepted handoff IDs:
Composition receipt / missing-deferred-superseded decisions:
Aggregate impact/Registry selection:

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

## 17. Adapter конкретного проекта

Release adapter проекта обязан определить: команды сборки immutable candidate, точный artifact target, платформенные проверки целостности и подписи, способ readback и способ rollback. Роли канона остаются теми же, меняются только их реализации.

Развёрнутый пример для desktop-приложения — [`assets/examples/release-adapter-desktop.md`](../assets/examples/release-adapter-desktop.md).

## 18. Self-check

Общий self-check — в [`../SKILL.md`](../SKILL.md). Здесь только то, что проверяется именно этим файлом.

1. Primary Red падает на baseline по правильной причине?
2. Immutable candidate однозначно связан с source/config?
3. ACCEPT содержит candidate identity, scope и approver?
4. Каждый handoff release intent интегрирован либо явно deferred/superseded?
5. QA matrix выведена из acceptance criteria batch, а не случайного smoke-набора?

