# Vibecoding Bible: аудит и roadmap универсализации

Дата аудита: 2026-08-04
Baseline: `135a936`
Статус: complete

## 1. Цель

Сделать `vibecoding-bible` единой точкой входа для человека, который создаёт цифровой продукт с помощью AI: от сырой идеи и существующего репозитория до выпуска, эксплуатации и улучшения.

Пользователь обращается только к Библии. Библия сама выбирает нужную фазу, уровень строгости, reference, официальный источник или специализированный skill. Она не пытается хранить внутри себя все API и предметные знания мира.

## 2. Текущий verdict

Текущая версия — сильный production-ready AI-engineering skill, но ещё не универсальная система создания любых цифровых продуктов.

Особенно хорошо покрыты:

- Lean AI и Oper8 governance;
- production-ready vertical slices;
- запрет production mocks и fabricated evidence;
- TDD, evidence levels и release gates;
- AI EvalSuite;
- calibration-first TestingHarness;
- context, memory, tools и agent frameworks;
- tokenomics;
- subagent/context-preservation policy;
- external mutation controls;
- conditional Mastra и shadcn defaults.

## 3. Белые пятна

| Область | Текущее покрытие | Требуемая доработка |
|---|---|---|
| Product discovery | Низкое | Пользователь, проблема, current way, validation, outcome |
| Requirements | Частичное | User journeys, functional/non-functional requirements, acceptance |
| General architecture | Частичное | Stack, boundaries, data, APIs, platforms, trade-offs |
| Repository bootstrap | Низкое | Reality snapshot, project map, environment и dependency strategy |
| Implementation workflow | Среднее | Планирование, change slices, debugging, git/change hygiene |
| UX и interface design | Низкое | IA, interaction, content, accessibility, web/mobile/CLI |
| General test strategy | Среднее | Unit/component/contract/integration/E2E/performance/security/a11y |
| Security/privacy | Низкое-среднее | Threat model, auth, tenancy, secrets, supply chain, abuse |
| Data lifecycle | Низкое | Schema, migrations, quality, retention, deletion, backups |
| Delivery/operations | Среднее | CI/CD, environments, flags, canary, incidents, disaster recovery |
| Post-launch learning | Низкое | Analytics, feedback, experiments, support, deprecation |
| Non-AI products | Низкое | Conventional software must be a first-class path |
| Practical artifacts | Низкое | Reusable briefs, ADRs, test/release/runbook templates |
| Skill regression | Частичное | Versioned scenario corpus and repeatable forward-test rubric |

## 4. Архитектурные проблемы текущей версии

1. Skill начинает работу слишком близко к implementation; discovery и product definition недостаточно операциональны.
2. Универсальные правила смешаны с AI-specific правилами и технологическими defaults.
3. Mastra и shadcn занимают слишком высокий уровень в каноне для универсального продукта.
4. `VibecodingProjectContract` слишком тяжёл для маленьких задач, несмотря на full/delta.
5. TestingHarness подробный и сильный, но слишком велик для большинства запросов.
6. Одни и те же инварианты повторяются в SKILL, core, contract и specialized references.
7. Почти все знания представлены prose; не хватает готовых рабочих artifacts.
8. Нет одного lifecycle, связывающего идею, реализацию, выпуск и обучение.

## 5. Целевой lifecycle

```text
UNDERSTAND → DESIGN → BUILD → VERIFY → SHIP → LEARN
```

### UNDERSTAND

- определить пользователя, проблему и current way;
- проверить, нужен ли вообще продукт/AI;
- определить expected outcome и дешёвую проверку главного unknown;
- выбрать уровень строгости.

### DESIGN

- сформировать user journeys и requirements;
- выбрать system boundaries, stack, data и integration contracts;
- определить UX/interface, security и failure modes;
- зафиксировать архитектурные решения.

### BUILD

- получить reality snapshot репозитория;
- разбить работу на маленькие production-ready slices;
- настроить context/agent harness;
- выполнять Contract → Red → Green → Refactor;
- диагностировать причины, не маскировать симптомы.

### VERIFY

- применить risk-based test strategy;
- проверить integration/E2E/security/performance/accessibility;
- применить EvalSuite для вероятностного AI behavior;
- применить TestingHarness для первого сложного workflow;
- собрать release evidence.

### SHIP

- проверить migrations, config, secrets и environments;
- выполнить CI/CD, deploy, canary, readback и rollback;
- настроить observability, SLO, backups и incident ownership;
- выпустить только доказанный scope.

### LEARN

- связать usage, feedback, cost и downstream outcome;
- триажить failures, support и incidents;
- обновлять regressions, docs и architecture decisions;
- определить следующий минимальный improvement.

## 6. Уровни строгости

### `EXPLORE`

Для обратимого исследования или spike без production claim. Обязательны outcome, ограничение времени/стоимости, explicit non-production label и решение: discard, continue или promote.

### `BUILD`

Режим по умолчанию. Маленький scope, но production-ready внутри выбранной границы. Использует delta/full contract по риску.

### `CRITICAL`

Для payments, PII, regulated data, high autonomy, irreversible mutations и большого blast radius. Требует усиленных security, evidence, approvals, canary и recovery gates.

Нельзя незаметно повысить `EXPLORE` до production. Нельзя применять `CRITICAL`-бюрократию к тривиальному reversible изменению.

## 7. Целевая структура skill

```text
skills/vibecoding-bible/
├── SKILL.md
├── VERSION
├── agents/openai.yaml
├── assets/templates/
│   ├── product-brief.md
│   ├── project-contract.md
│   ├── adr.md
│   ├── bug-spec.md
│   ├── agent-harness-contract.md
│   ├── required-tests.yaml
│   ├── release-checklist.md
│   └── operations-runbook.md
└── references/
    ├── core-principles.md
    ├── product.md
    ├── architecture.md
    ├── build.md
    ├── bug-repair.md
    ├── experience.md
    ├── quality.md
    ├── regression-registry.md
    ├── ai-systems.md
    ├── agent-harness.md
    ├── production.md
    ├── project-contract.md
    ├── evals.md
    └── testing-harness.md
```

Deep references загружаются только для соответствующей задачи. Пользователь не обязан знать структуру или вызывать другие skills вручную.

## 8. План реализации

### Phase 1 — Backbone

- [x] Перевести SKILL на lifecycle `UNDERSTAND → DESIGN → BUILD → VERIFY → SHIP → LEARN`.
- [x] Добавить `EXPLORE`, `BUILD`, `CRITICAL`.
- [x] Обновить routing и description для conventional и AI software.
- [x] Сделать ProjectContract risk-scaled.

Acceptance: новый пользователь с одной идеей получает один понятный маршрут; маленькая задача не создаёт тяжёлый контракт.

### Phase 2 — Product и design

- [x] Добавить `product.md`.
- [x] Добавить `architecture.md`.
- [x] Добавить `experience.md`.
- [x] Переместить shadcn из universal canon в conditional web default.

Acceptance: skill умеет пройти от идеи до build-ready design для web, backend/API, mobile/desktop, CLI/automation и AI workflow.

### Phase 3 — Build и quality

- [x] Добавить `build.md`: repository map, context, planning, TDD, debugging, git и delegation.
- [x] Добавить `quality.md`: единая risk-based test strategy.
- [x] Оставить `evals.md` и `testing-harness.md` глубокими optional protocols.
- [x] Убрать дублирование specialized rules из core/SKILL.

Acceptance: обычное software behavior и AI behavior получают правильный тип тестов; debugging не превращается в случайные patches.

### Phase 4 — AI systems и production

- [x] Создать `ai-systems.md` и объединить в нём context, memory, prompts, tools, agents, frameworks и tokenomics.
- [x] Сохранить Mastra как conditional TypeScript default.
- [x] Добавить `production.md`: security, data, performance, delivery, operations и learning.
- [x] Связать SHIP/LEARN с OutcomeRecord.

Acceptance: architecture не зависит от обязательного AI framework, а release включает реальный operational path.

### Phase 5 — Practical kit

- [x] Добавить короткие практические templates.
- [x] Обновить README и examples.
- [x] Добавить repo-level forward-test corpus для разных типов проектов.
- [x] Добавить scoring rubric и release checklist самого skill.

Acceptance: skill создаёт консистентные artifacts и проходит свежие сценарии без скрытого контекста.

### Phase 6 — Simplification and release

- [x] Удалить устаревшее дублирование после миграции.
- [x] Проверить все links/routes/metadata.
- [x] Выполнить `quick_validate.py`.
- [x] Провести fresh-agent forward-tests по lifecycle и risk modes.
- [x] Исправить gaps, опубликовать в `main` и синхронизировать installed skill.

Acceptance: один entrypoint, progressive disclosure, no broken links, clean repository, remote/local commit parity.

### Phase 7 — Portable Agent Execution Harness

- [x] Отделить универсальный execution-control protocol от конкретного coding-agent и фиксированного набора workflows.
- [x] Определить data-driven WorkflowDefinition, StageContract, durable SessionState, evidence, approvals и stale/rebind semantics.
- [x] Разделить replaceable HostAdapter и ProjectAdapter.
- [x] Добавить manual fallback, минимальный implementation slice и conformance/fault tests.
- [x] Связать Agent Execution Harness с ProjectContract, AI systems и TestingHarness без смешения их ролей.
- [x] Добавить AgentHarnessContract и два forward cases.

Acceptance: пользователь может безопасно применить существующий совместимый harness или построить минимальный переносимый harness поверх любого proprietary coding-agent; workflows описываются versioned data, а не ветками конкретного engine.

## 9. Definition of Done

Цель завершена, когда:

1. Skill поддерживает идею, существующий проект, bug, feature, integration, migration, launch и operation.
2. Conventional software и AI systems являются first-class paths.
3. Каждый запрос маршрутизируется к одной фазе и минимальному набору references.
4. Уровень строгости выбирается по risk, а не по размеру документа.
5. Пользователь получает один следующий шаг и не вынужден разбираться в внутренней методологии.
6. Universal principles отделены от Mastra/shadcn defaults.
7. Product, architecture, build, experience, quality, AI и production coverage явны.
8. Templates практически применимы и не содержат декоративной бюрократии.
9. Fresh-agent tests покрывают минимум десять разных запросов и три risk modes.
10. Skill валиден, опубликован, установленная копия идентична source.

## 10. Non-goals

- Не хранить внутри skill все vendor API и предметные знания.
- Не заменять официальную документацию изменяемых технологий.
- Не создавать отдельный framework для вайбкодинга.
- Не добавлять checklist ради checklist.
- Не требовать от пользователя заполнять все templates.
- Не обещать физические действия или domain expertise без соответствующих tools/sources.

## 11. Принцип простоты

Каждая доработка должна уменьшать хотя бы один вид пользовательского труда: выбор следующего шага, ручной debugging, повторный ввод, чтение лишних правил или проверку недоказанных результатов.

Если правило не меняет решение, действие или evidence, его не добавлять.

## 12. Результат

Основная реализация опубликована в `main` коммитом `0d19079`. Текущий candidate добавляет portable Agent Execution Harness; forward-test corpus содержит 21 case, включая два новых сценария harness. Их Green-проверка и публикация выполняются в release-процессе candidate.
