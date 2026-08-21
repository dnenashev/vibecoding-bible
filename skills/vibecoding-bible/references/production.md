# Production: безопасность, выпуск, эксплуатация и обучение

## Содержание

1. Назначение
2. Масштабирование строгости
3. Production baseline
4. Threat model
5. Identity, authorization и tenancy
6. Secrets, privacy и abuse
7. Supply chain
8. Data lifecycle
9. Performance и capacity
10. Resilience и recovery
11. Environments и configuration
12. CI/CD и release strategy
13. Deploy, readback и rollback
14. Observability и SLO
15. Incidents, runbooks и disaster recovery
16. Analytics, feedback и support
17. Deprecation и maintenance
18. LEARN и OutcomeRecord
19. Release protocol
20. Шаблон ProductionPlan
21. Self-check

## 1. Назначение

Этот модуль переводит «работает у разработчика» в «безопасно работает для реального пользователя и управляемо меняется после запуска».

Production readiness — это не один deploy. Это способность:

- безопасно выпустить exact candidate;
- увидеть реальное состояние;
- ограничить blast radius;
- восстановиться после failure;
- защитить данные и permissions;
- связать выпуск с пользовательским outcome;
- улучшать или удалить функцию по evidence.

Использовать две фазы lifecycle:

```text
SHIP: prepare → migrate → deploy → readback → observe → promote/rollback
LEARN: outcomes → feedback/incidents → regressions/decisions → next slice
```

## 2. Масштабирование строгости

### `EXPLORE`

Не выпускать spike как production feature. Изолировать environment/data, ограничить стоимость и срок жизни, запретить реальные consequential mutations. В конце удалить либо формально повысить в `BUILD`.

### `BUILD`

По умолчанию требовать реальную configuration, security, migrations, observability, release/readback/rollback и owner эксплуатации для принятого vertical slice.

### `CRITICAL`

Для payments, PII, regulated data, irreversible actions, high autonomy или большого blast radius усилить separation of duties, independent review, canary, audit, recovery exercises и production observation.

Не использовать один фиксированный checklist для всех систем. Усиливать controls там, где failure дорог, трудно обнаружим или необратим.

## 3. Production baseline

До release зафиксировать:

- owner продукта, сервиса и инцидента;
- supported user journey и explicit limitations;
- environments и exact candidate versions;
- data ownership и classification;
- authentication/authorization boundaries;
- mandatory integrations и credential readiness;
- expected workload и critical dependencies;
- logs/metrics/traces и alert ownership;
- deploy, readback, rollback/compensation;
- backup/restore, если state нельзя безопасно восстановить иначе;
- support и deprecation path.

Если обязательный пункт неприменим, написать короткое rationale. Не оставлять consequential область пустой.

## 4. Threat model

Перед проектированием security перечислить:

1. assets: данные, деньги, credentials, actions, availability и reputation;
2. actors: users, admins, services, agents, third parties и attackers;
3. trust boundaries: browser/API, service/service, tenant, provider, storage, CI/CD;
4. entrypoints: UI, API, webhooks, files, queues, tools и admin surfaces;
5. abuse/failure cases и blast radius;
6. preventive, detective и recovery controls.

Начать с нескольких самых дорогих сценариев, а не с энциклопедии угроз. Обновлять threat model при новой integration, permission, data class, agent tool или external mutation.

Для каждого material threat указать owner, control, test и residual risk. Security claim без проверяемого control не считать закрытым.

## 5. Identity, authorization и tenancy

Разделять:

- authentication — кто actor;
- authorization — что ему разрешено;
- tenancy — к чьим данным/ресурсам относится действие;
- approval — кто подтвердил конкретную consequential операцию;
- audit — как позже доказать actor, target и result.

Правила:

- идентичность получать из trusted auth layer, не из caller-supplied header/label;
- проверять authorization server-side на каждом consequential boundary;
- использовать least privilege и короткоживущие scoped credentials;
- не полагаться на скрытие UI controls;
- проверять ownership объекта и tenant scope до read/write;
- защищать admin/support impersonation отдельным approval и audit;
- отзывать sessions/tokens/roles и проверять revocation path;
- отделять service identity от human identity.

Для agents/tools задавать capability-level permissions и forbidden actions. Нельзя давать «агенту в целом» неограниченный production доступ.

## 6. Secrets, privacy и abuse

### Secrets

- хранить secrets в разрешённом secret store;
- не коммитить, не печатать и не передавать их в prompt/log;
- разделять credentials по environment и scope;
- определить rotation/revocation и emergency path;
- сканировать source, artifacts и CI logs;
- не использовать fallback secret в коде.

### Privacy

Для каждого data class определить:

- lawful purpose/consent, если применимо;
- collection minimum;
- storage location и processors;
- access и audit;
- retention/deletion/export;
- masking/redaction в logs и analytics;
- incident notification owner.

Не отправлять PII/secret в AI/provider без разрешённой policy и contract. Не хранить скрытую chain-of-thought; хранить проверяемые decisions/evidence.

### Abuse

Определить misuse cases, rate/cost limits, suspicious behavior signals, block/review path и appeal/support route. Guardrail должен иметь recovery и owner, а не только deny.

## 7. Supply chain

Контролировать:

- dependency provenance и lockfiles;
- vulnerability/license policy;
- minimal permissions CI runners и package scripts;
- signed/verified build artifacts, если risk требует;
- base images, actions/plugins и registries;
- reproducibility либо traceability build;
- update/patch owner;
- SBOM для scope, где это требуется policy или customer contract.

Не обновлять все dependencies автоматически одним непросматриваемым diff. Разделять security patch, behavior change и major migration; каждый получает подходящее evidence.

## 8. Data lifecycle

Для каждого durable state определить owner и source of truth.

### Schema и migrations

- version schema и migration;
- предусмотреть backward/forward compatibility на время rollout;
- проверять migration на representative volume;
- отделять schema change от опасного backfill, если возможно;
- делать resumable/idempotent backfill;
- сохранять progress, failures и reconciliation;
- определить rollback или roll-forward, если reverse migration небезопасна.

### Quality и consistency

- задать constraints и invariants в storage там, где возможно;
- проверять duplicates, orphan records и invalid transitions;
- использовать idempotency/outbox для consequential distributed mutation;
- иметь reconciliation/readback для внешних systems of record;
- не считать accepted request завершённым без подтверждённого terminal state.

### Retention, deletion и backups

- определить retention по purpose/policy;
- реализовать deletion/export включая derived copies и indexes;
- проверить, что backups соответствуют privacy/retention policy;
- шифровать и ограничивать доступ по risk;
- регулярно доказывать restore, а не только наличие backup job.

## 9. Performance и capacity

Начать с user journey и workload:

- expected и burst traffic;
- payload/data size;
- concurrency;
- latency budget по critical path;
- dependency limits;
- resource и monetary cost;
- growth assumption и owner пересмотра.

Измерять tail latency, saturation, error rate и cost, а не только среднее. Проверять cold starts, queue depth, connection pools, cache behavior и slow dependencies по применимости.

Capacity decision связывать с SLO и подтверждённым workload. Если baseline отсутствует, сначала провести измерение; не придумывать universal threshold.

Оптимизировать доказанный bottleneck. Не усложнять архитектуру ради гипотетического масштаба.

## 10. Resilience и recovery

Для каждой critical dependency определить:

- timeout;
- retry только для безопасных/idempotent операций;
- backoff/jitter и общий deadline;
- circuit/bulkhead/queue policy при необходимости;
- fallback: block, degrade, manual или deterministic;
- stale-data policy;
- reconciliation и recovery owner.

Проверять partial failures: network response потерян после mutation, queue доставила duplicate, process упал между state и receipt, provider вернул malformed result.

Не превращать exception в fabricated success. Degraded mode должен быть видим пользователю и observability.

## 11. Environments и configuration

Иметь явные `local/test/staging/production` либо обоснованно меньший набор. Environment обязан отличаться configuration и credentials, а не скрытой веткой бизнес-логики.

Правила:

- configuration versioned и validated при startup/deploy;
- secrets отделены от config;
- production defaults fail closed для опасных действий;
- feature flags имеют owner, purpose, expiry и cleanup;
- environment parity достаточна для проверяемых границ;
- production data не копируется без разрешённой процедуры;
- clock/timezone/locale и regional constraints определены;
- config drift обнаруживается и виден в release evidence.

## 12. CI/CD и release strategy

Pipeline должен быть воспроизводимым и выдавать evidence на exact candidate, связанный с release intent и composition receipt.

Для bug-release с human acceptance применять [`bug-repair.md`](bug-repair.md): authoritative QA и ACCEPT должны ссылаться на immutable candidate, собранный после integration.

Для несрочных небольших fixes по умолчанию использовать `Release Train`: независимо исправлять и проверять каждый defect, накапливать `READY_FOR_BATCH` changes в чистом cumulative head, затем один раз freeze batch, build candidate, выполнить aggregate risk-based verification, QA/ACCEPT и controlled release. Release trigger и maximum wait задаёт project policy; не придумывать универсальный размер batch.

Перед build выполнить `Release Composition Gate`: versioned release intent перечисляет handoffs/capabilities, явно принятые в batch; каждый должен быть `INTEGRATED`, явно `DEFERRED` или `SUPERSEDED`. Проверить provenance в frozen cumulative head и behavioral capability на exact candidate. Чистый Green head или наличие файлов не доказывают полноту release scope.

Минимальный flow:

```text
source candidate
  → static/tests/security/build
  → immutable artifact
  → migration preflight
  → deploy limited scope
  → health + behavior readback
  → observe
  → promote | rollback
```

Выбрать release strategy по blast radius:

- rolling для простого reversible сервиса;
- feature flag для отделения deploy от exposure;
- canary для наблюдения на ограниченном трафике;
- blue/green для быстрого environment rollback;
- shadow для behavior comparison без consequential output;
- manual checkpoint для irreversible/high-risk action.

Отдельная urgent hotfix lane нужна для активной security-проблемы, потери/повреждения данных, денег/permissions, существенной недоступности или другого явно срочного impact. Она не ждёт обычный train, но сохраняет applicable evidence, immutable candidate, approval, readback и rollback/compensation.

Approval не заменяет automated evidence. Автоматизация не отменяет human decision там, где policy его требует.

## 13. Deploy, readback и rollback

Перед deploy:

- проверить candidate, config, schemas, credentials и dependency readiness;
- заморозить release scope и известные limitations;
- определить observable success/failure и decision window;
- проверить rollback/compensation command и owner;
- сохранить previous known-good reference.

После deploy выполнить readback:

- artifact/config version реально активны;
- health и critical dependencies доступны;
- один безопасный critical journey работает;
- metrics/logs/traces поступают;
- migrations/backfills имеют ожидаемый progress;
- unexpected errors/cost/security signals отсутствуют по принятой policy.

Rollback — это исполненная и проверенная способность, не строка «можно откатить». Если schema/data mutation необратима, использовать roll-forward/compensation и ограничивать exposure.

## 14. Observability и SLO

Инструментировать user-visible outcome и critical boundaries.

Сохранять:

- request/run/trace identifiers;
- actor/tenant в безопасной форме;
- versions config/schema/model/rules/tools;
- state transitions и dependency calls;
- latency/errors/retries/queue depth;
- consequential mutation, idempotency, approval и readback;
- cost/usage для paid services;
- deploy/flag/migration events.

Не логировать secrets, лишние PII или chain-of-thought.

SLO выбирать из пользовательского ожидания и business risk. Для каждого SLI указать source, query, window, owner и response action. Alert должен вести к действию; не создавать alert только потому, что metric существует.

Dashboard не заменяет alarm и runbook. Health endpoint не доказывает critical journey.

## 15. Incidents, runbooks и disaster recovery

Определить простой incident loop:

```text
detect → assess impact → contain → communicate → recover → verify → learn
```

Runbook для material failure содержит:

- symptoms и impact;
- dashboards/queries;
- safe diagnostic commands;
- containment и rollback/compensation;
- escalation/communication owners;
- recovery verification;
- data/security follow-up.

После incident:

- сохранить timeline и evidence без обвинений;
- создать минимальный regression;
- исправить system/control, а не только человеческую ошибку;
- обновить runbook/threat model/architecture decision;
- проверить closure action.

Disaster recovery определить через допустимую потерю данных и время восстановления, принятые owner. Из этого вывести backup replication и restore procedure. Проводить restore/failover exercises с безопасным scope; не считать неиспытанный backup готовностью.

## 16. Analytics, feedback и support

До launch определить, какое поведение покажет ценность:

- activation/critical journey completion;
- accepted outcome;
- failures, abandonment и manual intervention;
- latency/cost и support burden;
- guardrail counter-metrics;
- cohort/segment, если он меняет решение.

Event contract должен иметь semantic definition, owner, version, privacy class и validation. Не собирать всё «на будущее».

Связывать quantitative signals с feedback, support и observed outcome. Жалоба пользователя — важное evidence, но не автоматическая truth: воспроизвести, классифицировать и добавить regression.

Support path должен сообщать пользователю статус, обходной путь и owner следующего действия. Не заставлять поддержку читать raw traces или угадывать техническую причину.

## 17. Deprecation и maintenance

Каждая долгоживущая capability требует:

- owner dependencies/security updates;
- compatibility policy;
- data/config migration path;
- documentation/runbook freshness;
- stale feature flags и experiments cleanup;
- deprecation notice и consumer migration;
- safe data export/deletion;
- shutdown/readback после удаления.

Не оставлять параллельные старый и новый paths без expiry. После успешной migration удалить obsolete code/config/permissions по отдельному проверяемому change.

## 18. LEARN и OutcomeRecord

Release decision говорит, что candidate допустимо выпустить. `OutcomeRecord` позже фиксирует, что реально произошло.

OutcomeRecord содержит:

- release/feature/decision reference;
- observation window;
- eligible population/exposure;
- primary и counter-metrics;
- actual usage/cost/manual intervention;
- incidents, overrides и support signals;
- source refs и data limitations;
- attribution confidence;
- verdict: win, loss, inconclusive или harmful;
- next decision и owner.

Не создавать положительный OutcomeRecord в момент deploy. Если данных недостаточно, verdict `inconclusive`.

Использовать LEARN loop:

1. сравнить outcome с baseline/expectation;
2. найти material segment/failure;
3. проверить causality и data quality;
4. превратить подтверждённый defect в regression;
5. обновить architecture/rules/evals/runbook новой version;
6. выбрать один следующий slice, ограничение или removal.

## 19. Release protocol

1. Выбрать обычный release, `Release Train` batch или urgent hotfix по impact/urgency.
2. Freeze release intent: accepted handoffs, capabilities, acceptance criteria и explicit defer/supersede decisions.
3. Выполнить Release Composition Gate: provenance + capability proof + QA coverage matrix.
4. Freeze exact cumulative head, batch manifest, candidate и release scope.
5. Пересчитать aggregate impact и проверить red lines ProjectContract/QualityPlan.
6. Подтвердить fresh applicable artifact/config/schema/integration evidence.
7. Проверить security/privacy/data и operational ownership.
8. Выполнить migration preflight и recovery readiness.
9. Deploy с выбранным blast-radius control.
10. Выполнить readback critical journey и observability.
11. Наблюдать decision window, определённое risk/SLO policy.
12. Promote, constrain или rollback по заранее известным signals.
13. Открыть OutcomeRecord с будущим observation window.

Release `READY` запрещён, если mandatory evidence отсутствует, rollback/compensation неработоспособны, monitoring слеп или owner не определён.

## 20. Шаблон ProductionPlan

```markdown
# ProductionPlan: <scope>

Mode: EXPLORE | BUILD | CRITICAL
Owners: product / service / security / incident
Candidate/environments:

## Risk and security
Assets/trust boundaries/material threats:
Auth/authz/tenancy:
Secrets/privacy/abuse/supply chain:

## Data
Sources of truth/schemas:
Migration/backfill/reconciliation:
Retention/deletion/backups/restore:

## Capacity and resilience
Workload/SLO/dependencies:
Timeout/retry/fallback:
Recovery/DR:

## Delivery
Release intent/accepted handoffs:
Composition receipt/provenance/capability evidence:
QA coverage matrix:
CI artifact/evidence:
Feature flag/canary strategy:
Deploy/readback:
Rollback/compensation:

## Operations
Logs/metrics/traces/alerts:
Runbooks/on-call/support:

## Learn
Analytics/feedback/counter-metrics:
OutcomeRecord window/owner:

## Release verdict
Required evidence refs:
Known constraints:
READY | READY_WITH_CONSTRAINTS | BLOCKED
```

## 21. Self-check

1. Production owner и supported journey определены?
2. Строгость соответствует `EXPLORE`, `BUILD` или `CRITICAL`?
3. Threat model покрывает самые дорогие assets/boundaries?
4. Identity trusted, authorization server-side, tenants изолированы?
5. Secrets/PII защищены на storage, transit, logs и providers?
6. Supply-chain изменения прослеживаемы?
7. Schemas/migrations/backfills versioned, resumable и проверяемы?
8. Retention/deletion/backups/restore реально работают?
9. Capacity и performance основаны на workload/SLO?
10. Dependency failures имеют timeout, bounded retry и честный fallback?
11. Environment/config drift видим?
12. CI выдаёт immutable artifact и evidence на exact candidate?
13. Release intent полностью reconciled с integrated/deferred/superseded handoffs?
14. Capability evidence и QA matrix подтверждают принятый scope exact candidate?
15. Release ограничивает blast radius по риску?
16. Deploy подтверждён readback critical journey?
17. Rollback/compensation исполнены или проверены безопасным drill?
18. Observability показывает user outcome и critical boundaries?
19. Alerts имеют owner/action, runbooks применимы?
20. Incident и disaster recovery процедуры проверены по риску?
21. Analytics/feedback/support ведут к решению, а не к сбору шума?
22. OutcomeRecord отделён от release verdict и имеет observation window?
