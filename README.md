# Вайбкодинг Библия

**Одна точка входа: от идеи до работающего и управляемого цифрового продукта.**

`vibecoding-bible` — открытый Codex skill для создания software с помощью AI. Он помогает сделать сайт, SaaS, API, mobile/desktop app, CLI, automation, data product или AI/agent system — и не спутать быстро написанный код с готовым продуктом.

Skill работает как senior product-and-engineering partner: определяет текущую фазу, выбирает уровень строгости, подключает только нужные правила и заканчивает одним проверяемым следующим шагом.

Текущая версия: [`1.0.0`](skills/vibecoding-bible/VERSION).

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

## Три режима строгости

| Режим | Для чего |
|---|---|
| `EXPLORE` | Reversible spike без production claim, ограниченный временем и стоимостью |
| `BUILD` | Маленький production-ready vertical slice; режим по умолчанию |
| `CRITICAL` | Payments, PII, regulated data, high autonomy и необратимые действия |

Эксперимент не становится production автоматически. При этом изменение текста кнопки не требует процесса уровня платёжной системы.

## Что можно попросить

| Запрос | Что сделает skill |
|---|---|
| «У меня есть идея, но я не понимаю, с чего начать» | Найдёт пользователя, проблему, outcome и самый дешёвый validation step |
| «Сделай приложение» | Сформирует requirements, выберет простой stack и проведёт через полный lifecycle |
| «Спроектируй API или архитектуру» | Определит boundaries, data ownership, contracts, failure и migration paths |
| «Реализуй функцию правильно» | Создаст risk-scaled contract и выполнит Red → Green → Refactor |
| «Почему всё ломается?» | Построит reproduction, локализует boundary и исправит root cause |
| «Сделай удобный интерфейс» | Проработает journey, IA, states, accessibility и подходящую design system |
| «Как проверить AI-функцию?» | Спроектирует EvalSuite с risk-based slices и calibrated judge |
| «Как впервые протестировать workflow?» | Совместно задаст checkpoints и автономно выполнит diagnosis/repair/replay |
| «Можно выпускать?» | Проверит exact evidence, integrations, security, deploy/readback/rollback |
| «Что улучшать после запуска?» | Свяжет usage, feedback, cost и downstream outcome |

## Основные правила

- Маленький scope, но production-ready внутри принятой границы.
- Никаких production mocks, hardcoded success и fabricated evidence.
- Изменение behavior начинается с подтверждённого Red.
- Самая простая архитектура, достаточная для реальных constraints.
- Deterministic rules остаются в коде; AI получает bounded decisions.
- Permissions, idempotency, readback и rollback для внешних mutations.
- Security, data, accessibility и operations усиливаются по риску.
- AI calls имеют token/cost budgets и измеримый accepted outcome.
- Implementation readiness и release readiness — разные verdicts.
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
    ├── production.md
    ├── project-contract.md
    ├── evals.md
    └── testing-harness.md
```

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
- exact-candidate Bug Repair protocol;
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
