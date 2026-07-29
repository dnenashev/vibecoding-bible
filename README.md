# Вайбкодинг Библия

`vibecoding-bible` — открытый Codex skill для управляемой разработки production-ready AI-продуктов. Он помогает превратить хаотичный вайбкодинг в проверяемый процесс: цель → ограниченный vertical slice → архитектура → harness → guardrails → доказательство результата.

Скилл работает как разговорный senior-инженер и системный диагност. Он помогает:

- проектировать AI-продукты, agent workflows и multi-agent systems;
- проводить `VibecodingProjectContract` preflight;
- выбирать между обычным кодом, provider SDK, Mastra и durable orchestration;
- строить context, memory, permissions, observability и release gates;
- применять TDD с обязательным Red → Green → Refactor;
- запрещать production mocks, fake integrations и hardcoded success;
- считать tokenomics и `cost_per_accepted_outcome`;
- использовать сабагентов без потери контекста оркестратора;
- соблюдать actual shadcn composition и conformance для web UI.

## Установка

Попросите Codex установить skill из GitHub:

```text
Установи skill из https://github.com/dnenashev/vibecoding-bible/tree/main/skills/vibecoding-bible
```

Или используйте системный skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo dnenashev/vibecoding-bible \
  --path skills/vibecoding-bible
```

После установки начните новый turn и вызовите skill явно:

```text
$vibecoding-bible спроектируй production-ready архитектуру этой AI-функции
```

## Примеры запросов

```text
$vibecoding-bible почему агент постоянно ломает соседний код?

$vibecoding-bible спроектируй harness, память и guardrails для этого workflow

$vibecoding-bible проведи pressure-test архитектуры перед реализацией

$vibecoding-bible реализуй feature через Contract → Red → Green → Refactor
```

## Состав

```text
skills/vibecoding-bible/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── core-principles.md
    ├── project-contract.md
    ├── agent-frameworks.md
    └── subagent-policy.md
```

`SKILL.md` содержит основной routing и рабочий протокол. Детальные правила загружаются лениво из `references/`, чтобы не расходовать контекст без необходимости.

## Методологическая оговорка

Это независимая практическая интерпретация, а не официальный материал и не сертифицированная реализация упомянутых методологий или продуктов.

- Раздел Lean AI вдохновлён принципами Lean thinking: ценность до технологии, устранение waste и уважение роли человека. См. материалы [Lean Enterprise Institute](https://tech.lean.org/journal/lean-ai-navigating-hype).
- Раздел Oper8 вдохновлён публичным [справочником методики Oper8 от Кактус.AI](https://kkts.ai/methodology).
- Mastra, Temporal, LangGraph, CrewAI, Agno, OpenAI и shadcn упоминаются как инструменты или варианты архитектуры. Все названия и товарные знаки принадлежат соответствующим владельцам.

## Статус

Пакет проходит стандартный `quick_validate.py` из системного `skill-creator` Codex. Методология развивается через применение на реальных проектах, regression cases и evidence-backed обновления.

## Лицензия

[MIT](LICENSE)
