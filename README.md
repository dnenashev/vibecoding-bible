# Вайбкодинг Библия

**Одна точка входа: от идеи до работающего и управляемого цифрового продукта.**

`vibecoding-bible` — открытая vendor-neutral методология, упакованная как Codex-compatible skill. Её правила подходят и для Claude Code, других coding agents или собственного agent harness. Она помогает сделать сайт, SaaS, API, mobile/desktop app, CLI, automation, data product или AI/agent system — и не спутать быстро написанный код с готовым продуктом.

Skill работает как senior product-and-engineering partner: определяет текущую фазу, выбирает уровень строгости, подключает только нужные правила и заканчивает одним проверяемым следующим шагом.

Текущая версия: [`2.0.0`](skills/vibecoding-bible/VERSION).

## Быстрый старт

Попросите Codex установить skill:

```text
Установи skill из https://github.com/dnenashev/vibecoding-bible/tree/main/skills/vibecoding-bible
```

Начните новую задачу:

```text
$vibecoding-bible хочу создать сервис для подготовки коммерческих предложений
```

Или принесите существующий проект:

```text
$vibecoding-bible разберись, почему checkout ломается, и исправь production-ready
```

## Как работает Библия

```text
UNDERSTAND → DESIGN → BUILD → VERIFY → SHIP → LEARN
```

- `UNDERSTAND` — пользователь, проблема, outcome и главное неизвестное.
- `DESIGN` — requirements, journeys, architecture, data, integrations и interface.
- `BUILD` — repository reality, маленькие slices, Red → Green → Refactor.
- `VERIFY` — risk-based tests, AI evals, workflow TestingHarness и evidence.
- `SHIP` — security, migrations, CI/CD, deploy, readback и rollback.
- `LEARN` — analytics, feedback, incidents, cost и реальный OutcomeRecord.

Skill не заставляет каждый запрос начинать с нуля. Он находит текущую фазу и проверяет только нужные prerequisites.

## Две оси: режим и риск

Предназначение работы и цена ошибки — разные вещи, поэтому они задаются отдельно.

| Delivery mode | Для чего |
|---|---|
| `EXPLORE` | Reversible spike без production claim, ограниченный временем и стоимостью |
| `BUILD` | Маленький production-ready vertical slice; режим по умолчанию |

| Risk | Для чего |
|---|---|
| `LOW` | Обратимое изменение с малым blast radius и без чувствительных данных |
| `STANDARD` | Реальный продукт; уровень по умолчанию |
| `CRITICAL` | Payments, PII, regulated data, high autonomy и необратимые действия |

Оси независимы: быстрый эксперимент на реальных платёжных данных — это `EXPLORE + CRITICAL`,
где time box берётся от режима, а изоляция и запрет production-записи — от риска.

Эксперимент не становится production автоматически. При этом изменение текста кнопки не требует процесса уровня платёжной системы.

До версии 2.0.0 это была одна шкала `EXPLORE | BUILD | CRITICAL`. Правило переноса — в
[`references/vocabulary.md`](skills/vibecoding-bible/references/vocabulary.md).

## Что можно попросить

| Запрос | Что сделает skill |
|---|---|
| «У меня есть идея, но я не понимаю, с чего начать» | Найдёт пользователя, проблему, outcome и самый дешёвый validation step |
| «Сделай приложение» | Сформирует requirements, выберет простой stack и проведёт через полный lifecycle |
| «Спроектируй API или архитектуру» | Определит boundaries, data ownership, contracts, failure и migration paths |
| «Реализуй функцию правильно» | Создаст risk-scaled contract и выполнит Red → Green → Refactor |
| «Почему всё ломается?» | Построит reproduction, локализует boundary и исправит root cause |
| «Мелкие fixes слишком дорого релизить по одному» | Соберёт проверенные изменения в Release Train и выпустит один immutable batch |
| «Сделай удобный интерфейс» | Проработает journey, IA, states, accessibility и подходящую design system |
| «Как проверить AI-функцию?» | Спроектирует EvalSuite с risk-based slices и calibrated judge |
| «Как впервые протестировать workflow?» | Совместно задаст checkpoints и автономно выполнит diagnosis/repair/replay |
| «Как вести долгую работу агента без потери состояния?» | Подключит совместимый внешний harness или спроектирует переносимый state/evidence/approval loop |
| «Можно выпускать?» | Проверит exact evidence, integrations, security, deploy/readback/rollback |
| «Что улучшать после запуска?» | Свяжет usage, feedback, cost и downstream outcome |

## Основные правила

- Маленький scope, но production-ready внутри принятой границы.
- Никаких production mocks, hardcoded success и fabricated evidence.
- Изменение behavior начинается с подтверждённого Red.
- Перед consequential действием фиксируется проверяемое ожидание; запись задним числом не является evidence.
- Дорогое действие выполняется после того, как исчерпан вывод из уже собранных артефактов.
- Самая простая архитектура, достаточная для реальных constraints.
- Deterministic rules остаются в коде; AI получает bounded decisions.
- Permissions, idempotency, readback и rollback для внешних mutations.
- Security, data, accessibility и operations усиливаются по риску.
- AI calls имеют token/cost budgets и измеримый accepted outcome.
- Implementation readiness и release readiness — разные verdicts.
- Release Composition Gate не позволяет потерять принятый handoff в зелёном candidate.
- Пользователь получает один следующий шаг, а не весь канон сразу.

## Opinionated defaults без lock-in

- Для TypeScript/Node agent runtime первой оценивается Mastra, если действительно нужны agents, workflows, tools и memory.
- Для web UI с `components.json` используется actual shadcn project context.
- Для bounded AI calls может быть правильнее обычный provider SDK.
- Для long-running business process может потребоваться отдельный durable engine.

Framework и design system — conditional defaults, а не универсальные зависимости.

## Архитектура skill

```text
skills/vibecoding-bible/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── assets/templates/
│   ├── product-brief.md
│   ├── project-contract.md
│   ├── adr.md
│   ├── bug-spec.md
│   ├── belief-notes.md
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
    ├── vocabulary.md
    ├── host-adapters.md
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

`vocabulary.md` — единственный источник публичных enum: фазы, delivery mode, risk, глубина контракта, вердикты, уровни evidence. `host-adapters.md` сопоставляет роли канона с примитивами конкретной среды.

`SKILL.md` содержит lifecycle и routing. References загружаются лениво, поэтому запрос про обычный UI не тратит контекст на multi-agent orchestration, а AI eval не загружает deployment runbook без необходимости.

## Версионирование

Каноническая версия находится в [`skills/vibecoding-bible/VERSION`](skills/vibecoding-bible/VERSION). Git tag `vX.Y.Z` указывает на release commit с тем же значением:

- `PATCH` — совместимое исправление или уточнение;
- `MINOR` — новая обратно совместимая capability;
- `MAJOR` — несовместимое изменение contract или поведения.

Поля `version` внутри EvalSuite, TestingHarness или Registry относятся только к соответствующему artifact.

## Практические artifacts

Skill включает короткие шаблоны:

- Product Brief;
- risk-scaled ProjectContract;
- Architecture Decision Record;
- BugSpec;
- BeliefNotes — durable-форма Context Capsule с разделом `Refuted` и лимитом в одну страницу;
- exact-candidate Bug Repair protocol;
- Release Train для пакетной доставки minor fixes и urgent hotfix lane;
- Release Composition Gate: release intent, handoff provenance и capability completeness;
- AgentHarnessContract для переносимого execution harness над proprietary agents;
- Required Test Registry;
- Release Checklist;
- Operations Runbook.

Агент заполняет только применимые поля. Пользователь не обязан проходить анкету вручную.

## Границы доверия

Библия задаёт operating system, но не заменяет фактический source и актуальную документацию:

- README не доказывает runtime behavior;
- unit test не доказывает live integration;
- `passed: true` не является hard evidence;
- отсутствие credentials не разрешает выдумать результат;
- offline eval не равен production outcome;
- advice/diagnosis не разрешает внешние mutations;
- быстро меняющийся API проверяется по installed version и official docs.

Пользователю достаточно обратиться к `$vibecoding-bible`: skill сам применит доступные специализированные skills, connectors и официальные источники, если они нужны задаче.

Если среда уже предоставляет совместимый execution harness, он ведёт durable stages, evidence и human approvals, а Библия остаётся policy layer. Codex Harness — один из возможных adapters, не обязательная зависимость канона.

## Установка через системный installer

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo dnenashev/vibecoding-bible \
  --path skills/vibecoding-bible
```

После установки начните новую задачу, чтобы Codex обнаружил skill.

## Развитие и качество

Skill проходит `quick_validate.py` и fresh-agent forward-tests на разных типах проектов и фазах lifecycle. Аудит и phased roadmap находятся в [`docs/AUDIT-AND-ROADMAP.md`](docs/AUDIT-AND-ROADMAP.md).

Ошибки и предложения: [GitHub Issues](https://github.com/dnenashev/vibecoding-bible/issues).

## Методологическая оговорка

Это независимая инженерная интерпретация, а не официальная или сертифицированная реализация упомянутых подходов.

- Lean AI: value before technology, устранение waste и короткие feedback loops.
- Oper8: versioned context, rules, evals, autonomy, decisions и outcomes.
- Cold-start eval: практическая адаптация идей Михаила Карпова / AI Product Club.
- Mastra, Temporal, LangGraph, CrewAI, Agno, OpenAI и shadcn рассматриваются как инструменты, а не обязательные части канона.

## Лицензия

[MIT](LICENSE)
