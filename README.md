# Вайбкодинг Библия

**Код генерируется быстро. Система должна оставаться управляемой.**

`vibecoding-bible` — открытый Codex skill для разработки production-ready AI-продуктов. Он превращает вайбкодинг из серии импровизированных промптов в проверяемый инженерный цикл: цель → контракт → Red → Green → integration evidence → release gate.

Скилл работает как разговорный senior-инженер: находит самое опасное неизвестное, ограничивает scope, проектирует архитектуру и harness, а затем требует доказательства, что результат действительно готов к эксплуатации.

## Быстрый старт

Попросите Codex установить skill из GitHub:

```text
Установи skill из https://github.com/dnenashev/vibecoding-bible/tree/main/skills/vibecoding-bible
```

Начните новую задачу и вызовите skill явно:

```text
$vibecoding-bible разбери мой проект и предложи один безопасный следующий шаг
```

Или сразу дайте конкретную задачу:

```text
$vibecoding-bible спроектируй и реализуй production-ready оплату подписки
```

## Зачем он нужен

AI-агент может быстро написать локально работающий код и одновременно увеличить системный риск:

- заменить недоступную интеграцию mock-данными и назвать функцию готовой;
- доказать unit-тестом то, что должно быть проверено на integration, E2E или live-уровне;
- потерять важные решения после сжатия контекста, сломать соседний код или выполнить внешнюю мутацию без readback и rollback;
- раздувать число model calls и стоимость workflow без измеримого роста полезного результата.

`vibecoding-bible` добавляет между намерением и кодом явные контракты, границы автономности, TDD, evidence levels, token budgets и отдельную проверку готовности к релизу.

## Для кого

- Для founders и solo builders, которые вайбкодят реальные сервисы, а не одноразовые демо.
- Для инженеров и tech leads, внедряющих AI coding в существующий продукт.
- Для команд, которые строят agents, workflows, multi-agent systems, память и tool use.
- Для тех, кому нужно диагностировать, почему агент зацикливается, теряет контекст или ломает проект.

Для disposable-прототипа без пользователей, данных и последствий полный production-контур может быть избыточен. Скилл умеет уменьшать scope, но не называет хрупкий runtime «достаточно хорошим MVP».

## Как это работает

```text
Реальный outcome
  → VibecodingProjectContract
  → самый дорогой failure mode
  → минимальный production-ready vertical slice
  → implementation gate
  → первый поведенческий Red test
  → Green и Refactor
  → integration / E2E / live evidence
  → release gate, readback и rollback
```

Перед существенным изменением скилл создаёт полный или delta-контракт и выносит отдельные verdicts:

- `READY`, `READY_WITH_CONSTRAINTS` или `BLOCKED` — можно ли начинать реализацию;
- `KEEP_LOCAL`, `DELEGATE`, `PARALLELIZE` или `DECOMPOSE_FIRST` — как организовать работу и сохранить контекст;
- отдельный release verdict — достаточно ли evidence для выпуска.

Implementation readiness не считается release readiness.

## Что можно попросить

| Запрос | Что делает скилл |
|---|---|
| «Почему агент постоянно ломает проект?» | Находит системную причину и самый опасный failure mode |
| «Спроектируй архитектуру AI-функции» | Фиксирует границы, контракты, инварианты, integrations и rollback |
| «Построй agent harness» | Проектирует context, memory, tools, permissions, evals и observability |
| «Как тестировать workflow или multi-agent system?» | Проектирует trusted evidence, checkpoints, repair, clean replay и acceptance |
| «Как проверить agent role или skill?» | Создаёт fresh-agent cases, routing/permission probes и fault-injection qualification |
| «Разнеси мой подход» | Проводит pressure-test по наиболее дорогому сценарию провала |
| «Реализуй фичу правильно» | Выполняет Contract → Red → Green → Refactor и собирает release evidence |
| «Когда вызывать сабагента?» | Оценивает риск compaction и формирует `SubagentTaskContract` |

По умолчанию ответ остаётся разговорным и заканчивается одним конкретным следующим шагом. Код и артефакты создаются тогда, когда пользователь просит реализацию или задача действительно этого требует.

## Пример поведения

Запрос:

```text
$vibecoding-bible реализуй оплату подписки
```

Скилл не начинает с генерации checkout-компонента. Сначала он:

1. Осматривает фактическое состояние репозитория и действующие project instructions.
2. Отделяет известные факты от assumptions и unknowns.
3. Фиксирует payment invariants, permissions, idempotency и границы внешних мутаций.
4. Создаёт delta `VibecodingProjectContract` и называет первый failing behavioral test.
5. Реализует минимальный Green без production mocks и hardcoded success.
6. Проверяет реальную интеграцию на требуемом уровне, usage/cost, observability, readback и rollback.
7. До изменения кода сообщает, можно ли начинать реализацию; после evidence — готов ли результат к релизу.

Если credentials или live access отсутствуют, результат будет честно помечен как blocked или потребует manual verification — fabricated evidence не используется.

## Инженерный канон

- **Production-ready внутри выбранного scope.** Маленький vertical slice допустим; хрупкий runtime — нет.
- **Никаких mocks в production path.** Test doubles разрешены только в test-only composition root и не заменяют live evidence.
- **TDD.** Изменение поведения начинается с Red test; assertions не ослабляются ради Green.
- **EvalSuite lifecycle.** Cold-start cases проходят expert labeling, judge calibration, per-slice gates, CI regressions и пополняются production outcomes.
- **Evidence-backed TestingHarness.** Workflow, multi-agent system, agent role и skill проходят versioned scenarios, independent evidence collection, Red→Green repair и clean replay; self-attested pass запрещён.
- **Tokenomics.** Каждый runtime AI call получает pre-call budget и post-call settlement; оптимизируется `cost_per_accepted_outcome`.
- **Lean AI и Oper8.** Ценность идёт раньше технологии; контекст, память, автономность и outcomes имеют явные контракты.
- **Agent frameworks по необходимости.** Для TypeScript/Node.js Mastra рассматривается первой, но обычный код, provider SDK или durable orchestration могут быть правильнее.
- **Контекст оркестратора защищён.** Сабагент вызывается для длинной bounded-задачи, когда compaction угрожает исходному диалогу и решениям, а не просто потому, что задача большая.
- **UI следует actual shadcn context.** Компоненты, semantic tokens и composition проверяются по реальному проекту, а не угадываются.
- **Внешние мутации управляемы.** Требуются permissions, idempotency, approval, readback и rollback.

## Архитектура скилла

```text
skills/vibecoding-bible/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── core-principles.md
    ├── project-contract.md
    ├── evals.md
    ├── testing-harness.md
    ├── agent-frameworks.md
    └── subagent-policy.md
```

`SKILL.md` содержит routing, режимы и основной рабочий протокол. Детальные правила загружаются лениво:

- [`core-principles.md`](skills/vibecoding-bible/references/core-principles.md) — production readiness, Lean AI, Oper8, mocks, TDD, tokenomics, shadcn и evidence;
- [`project-contract.md`](skills/vibecoding-bible/references/project-contract.md) — `VibecodingProjectContract`, gates и red lines;
- [`evals.md`](skills/vibecoding-bible/references/evals.md) — cold-start eval, judge calibration, slices, guardrails и production regression lifecycle;
- [`testing-harness.md`](skills/vibecoding-bible/references/testing-harness.md) — универсальный harness для workflows, multi-agent systems, agent roles и skills: trusted evidence, repair, replay и acceptance;
- [`agent-frameworks.md`](skills/vibecoding-bible/references/agent-frameworks.md) — Mastra, alternatives, memory, tools и orchestration;
- [`subagent-policy.md`](skills/vibecoding-bible/references/subagent-policy.md) — compaction risk, delegation verdicts и `SubagentTaskContract`.

Так канон остаётся подробным, но не расходует контекст на правила, которые не относятся к текущей задаче.

## Установка через системный installer

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo dnenashev/vibecoding-bible \
  --path skills/vibecoding-bible
```

После установки начните новую задачу, чтобы Codex обнаружил skill.

## Границы доверия

Скилл задаёт инженерный процесс и guardrails, но не гарантирует production readiness сам по себе. Verdict зависит от доступного repository и runtime evidence.

- Исходный код и README не заменяют runtime-проверку.
- Unit tests не доказывают работу внешней интеграции.
- Отсутствие credentials не разрешает подменить live result.
- Framework не заменяет permissions, evals, observability и release gate.
- Самодекларация `passed: true`, supervisor confidence или запись `replay queued` не являются hard evidence; required facts подтверждает независимый collector.
- Advice или diagnosis не дают разрешения изменять проект или внешние системы.

## Статус и развитие

Текущий канал разработки — `main`. Пакет проходит стандартный `quick_validate.py` из системного `skill-creator` Codex. Методология развивается через применение на реальных проектах, regression cases и evidence-backed обновления.

Ошибки и предложения можно оставить в [GitHub Issues](https://github.com/dnenashev/vibecoding-bible/issues).

## Методологическая оговорка

Это независимая практическая интерпретация, а не официальный материал и не сертифицированная реализация упомянутых методологий или продуктов.

- Раздел Lean AI вдохновлён принципами Lean thinking: ценность до технологии, устранение waste и уважение роли человека. См. материалы [Lean Enterprise Institute](https://tech.lean.org/journal/lean-ai-navigating-hype).
- Раздел Oper8 вдохновлён публичным [справочником методики Oper8 от Кактус.AI](https://kkts.ai/methodology).
- Cold-start часть EvalSuite адаптирует идеи раздатки Михаила Карпова / AI Product Club [«Cold-start eval»](https://drive.google.com/file/d/1RfWeSkRn5MgI8QVNc5ZAriymZsnlI31K/view); её численные ориентиры используются как эвристики, а не универсальные нормы.
- Mastra, Temporal, LangGraph, CrewAI, Agno, OpenAI и shadcn упоминаются как инструменты или варианты архитектуры. Все названия и товарные знаки принадлежат соответствующим владельцам.

## Лицензия

[MIT](LICENSE)
