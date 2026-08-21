# EvalSuite: от cold start до production outcomes

## 1. Назначение

`EvalSuite` — versioned executable specification вероятностного поведения AI-функции. Он переводит словесное требование в воспроизводимые cases с ожидаемым поведением, срезами, критериями и release policy.

Eval не заменяет `VibecodingProjectContract`, архитектуру, security или business outcome. Он является частью контракта для AI-поведения:

```text
ProjectContract определяет зачем, границы и риск
  → EvalSuite определяет проверяемое AI-поведение
  → release evidence доказывает exact implementation
  → OutcomeRecord показывает реальный downstream outcome
```

Offline score — гипотеза о production behavior, а не доказательство довольного пользователя или бизнес-эффекта.

## 2. Когда EvalSuite обязателен

Создать или обновить EvalSuite, если изменение затрагивает:

- prompt, system instructions, model или model parameters;
- ContextPack, retrieval, memory или Rulebook;
- agent decision, tool selection или autonomy;
- structured output, classification, extraction, generation или ranking;
- judge, fallback, guardrail или acceptance threshold;
- AI framework/runtime/provider либо значимую версию зависимости;
- production defect, drift или новый пользовательский срез.

Для полностью deterministic behavior использовать обычные tests. Не заменять точный assertion LLM-judge там, где результат можно проверить кодом.

## 3. Жизненный цикл

```text
cold_start
  → expert_labeled
  → judge_calibrated
  → ci_regression
  → shadow_or_canary
  → production_enriched
  → stale | superseded
```

- `cold_start` — cases получены из доменной экспертизы до production traces.
- `expert_labeled` — owner утвердил expected behavior и удалил либо переклассифицировал невалидные cases.
- `judge_calibrated` — automated judge сопоставлен с human gold set.
- `ci_regression` — frozen suite запускается на изменениях AI behavior.
- `shadow_or_canary` — offline результат проверяется на live-like traffic без недопустимого blast radius.
- `production_enriched` — реальные failures и outcomes пополняют regression corpus.
- `stale` — upstream model/context/rules/tools или product policy изменились без revalidation.
- `superseded` — новая frozen version заменила предыдущую.

Frozen EvalSuite не редактировать молча. Создать новую version и связать с exact ProjectContract, code commit, model, ContextPack, Rulebook, tools и judge.

Если suite является обязательным project gate, зарегистрировать её одной entry по [`regression-registry.md`](regression-registry.md). Cases остаются внутри EvalSuite; root Registry не должен их дублировать.

## 4. Контракт EvalSuite

Зафиксировать:

- `id`, `version`, `status`, owner, created/frozen timestamps;
- одну AI capability или decision boundary;
- consumer и downstream use;
- source/provenance, data classification, consent и retention;
- case schema и expected behavior policy;
- floor, ceiling, dimensions и named slices;
- primary metric, counter-metrics и red-line failures;
- per-slice acceptance thresholds и blocking flags;
- ambiguity, abstention, fallback и human-review policy;
- candidate model/context/rules/tools versions и run config;
- judge type/version/criteria и calibration evidence;
- repetitions, variance policy, token/cost budget и deadline;
- admission policy для новых regressions;
- связь offline results с `OutcomeRecord` и observation window.

Одна suite проверяет одну ясную capability. Если формулировка содержит независимые поведения, разделить её на suites или явно независимые slices с отдельными owners и thresholds.

## 5. Cold-start протокол

Использовать, когда production traces и реальные users ещё отсутствуют.

### Шаг 1. Сформулировать одно поведение

Записать одну строку без скрытого второго действия:

```text
Для <consumer> система по <input> должна принять/вернуть <bounded behavior>,
чтобы <downstream decision> мог <expected outcome>.
```

Если критерий успеха нельзя проверить по case, behavior ещё не определён.

### Шаг 2. Собрать рабочий контекст

Добавить только разрешённые representative inputs, schemas, domain rules, examples и expected output contract. Удалить secrets и неразрешённые PII. Зафиксировать provenance и snapshot/version каждого источника.

### Шаг 3. Найти floor

Создать самый простой честный case, который capability должна решать стабильно. Floor фиксирует нижнюю границу, а не среднюю сложность.

Если floor систематически падает, не расширять набор: пересмотреть feasibility, context, tools, scope или сам product promise.

### Шаг 4. Найти ceiling

Создать case на границе либо за текущими возможностями. Полезный ceiling выявляет, где модель должна ошибиться, отказаться, запросить данные или передать решение человеку.

Если ни один case не падает, suite может быть насыщена и не различать версии. Повысить сложность или проверить leakage.

### Шаг 5. Определить dimensions и slices

Назвать факторы, которые реально меняют сложность, например:

- длина, шум, язык и формат input;
- редкость домена и freshness;
- число сущностей и похожесть имён;
- неполнота, отрицание и ложная предпосылка;
- location ключевого факта в длинном context;
- tool availability, permission и retrieval quality;
- required abstention или external action risk.

Изменять по возможности один фактор за раз. Не принимать перефразировки одного case за новое покрытие.

### Шаг 6. Заполнить пространство между floor и ceiling

Использовать AI как генератор candidate variations, но не как владельца truth. Для каждого candidate доменный expert должен:

1. проверить реалистичность input;
2. утвердить expected behavior и verification method;
3. назначить dimensions/slices;
4. удалить duplicate, leaked и неразрешённый case;
5. определить risk и blocking flag.

По мере появления реальных данных заменять часть synthetic cases production regressions. Synthetic corpus не должен навсегда оставаться единственным evidence.

## 6. Схема eval case

Машинная схема — [`assets/schemas/eval-case.schema.json`](../assets/schemas/eval-case.schema.json).
Поля ниже описывают её содержательно.

Минимальная запись:

```yaml
id: case-001
input: {}
expected:
  behavior: ""
  format: ""
  scope: ""
verification: ""
slices: []
source:
  type: synthetic | expert | production_regression
  reference: ""
risk: low | medium | high | critical
blocking: true
ambiguityPolicy: answer | clarify | abstain | human_review
```

Не хранить hidden chain-of-thought как expected output. Проверять observable answer, decision, tool call, state transition или отказ.

Для вероятностного поведения Red принимает форму воспроизводимого probe: eval case с
заранее объявленным критерием, а не assert над одним прогоном. Правило то же —
критерий объявляется до прогона и не переписывается под полученный результат.

## 7. Неоднозначность и abstention

Case с несколькими защитимыми содержательными ответами не использовать для проверки одного exact answer. Выбрать одно:

- уточнить input до однозначности;
- определить множество допустимых outputs;
- проверить требование задать blocking question;
- проверить abstention/fallback;
- проверить передачу на human review.

Если неоднозначность встречается в production, не удалять сам сценарий из coverage: превратить правильную реакцию на неоднозначность в expected behavior.

## 8. Judge и калибровка

### Порядок проверок

1. Сначала deterministic validation: schema, types, required fields, exact invariants, permissions и tool effects.
2. LLM-judge использовать только для semantic criteria, которые нельзя надёжно проверить кодом.
3. Финальный release result приводить к policy verdict `PASS`/`FAIL`, сохраняя причины и violated criterion.

Judge получает input, expected policy, actual output и нумерованные criteria. Он не исправляет ответ и не подменяет evaluator.

### Калибровка

До использования judge как release gate:

- собрать human-labeled gold set по основным slices и risk classes;
- измерить agreement, false pass и false fail отдельно;
- исследовать disagreement и исправлять прежде всего размытые criteria;
- определить risk-based допустимые ошибки, а не универсальный процент;
- version и freeze judge prompt/model/config;
- повторять calibration после значимого изменения judge или distribution.

Для consequential decisions разделять candidate и judge model/provider, если self-preference, shared failure modes или leakage могут исказить verdict. Независимость не отменяет human calibration.

## 9. Прогон и чтение результата

Каждый run связывать с exact:

- EvalSuite version;
- candidate model/provider и parameters;
- ContextPack, Rulebook, tools и code commit;
- judge version;
- timestamp, environment и seed, если доступен;
- token usage, cost, attempts и deadline.

При stochastic output выполнять заранее определённое число повторов и сохранять dispersion. Скачок score между одинаковыми runs не называть progress/regression без variance analysis.

Не принимать решение по aggregate score в одиночку. Читать:

- pass rate и sample size по каждому blocking slice;
- false-pass-sensitive red lines;
- abstention/fallback rate;
- latency и cost per accepted outcome;
- variance и unstable cases;
- изменения относительно frozen baseline.

Маленький slice с единичными cases не поддерживает точный численный вывод. Расширить coverage либо использовать conservative/manual gate.

## 10. Guardrail и product decision

Для каждого consequential slice определить:

```text
threshold passed → разрешённый product path
threshold missed → fallback | clarify | abstain | human review | block
red-line failure → release BLOCKED независимо от aggregate score
```

Threshold выбирать из цены ошибок, autonomy level и fallback, а не из привычного значения. Чем выше blast radius и необратимость, тем сильнее evidence и human control.

Eval сообщает, где capability приемлема. Product owner решает, какие slices включать, ограничивать или исключать из production promise.

## 11. Production enrichment

После запуска:

1. Связывать sampled decisions с feedback и `OutcomeRecord` после observation window.
2. Триажить failures, incidents, overrides и high-cost cases.
3. Добавлять минимальный reproduction как новый Red regression.
4. Проверять provenance, privacy, expected behavior и slice.
5. Создавать новую EvalSuite version; не переписывать frozen history.
6. Сравнивать offline movement с online primary/counter-metrics.
7. Помечать suite stale при distribution, model, rules, context или tool drift.

Human correction не становится truth автоматически: проверить её по Rulebook и outcome evidence.

## 12. Red lines

Implementation или release блокируется в соответствующем scope, если:

- consequential AI behavior не имеет owner и versioned EvalSuite;
- expected answers сгенерированы AI и не утверждены ответственным expert;
- cases содержат secrets/PII без разрешённого handling;
- suite состоит из duplicates, leakage или одного happy-path slice;
- required ambiguity/abstention behavior не проверяется;
- judge используется без calibration либо превышает допустимый false-pass risk;
- aggregate score скрывает failure blocking slice;
- sample size, repetitions или release threshold заявлены без risk tolerance, baseline/variance и статистического rationale;
- exact model/context/rules/tools/judge/run config не зафиксированы;
- offline score выдан за production или business outcome;
- required threshold не достигнут, а fallback отсутствует;
- production defect не превращён в regression без документированной причины.

## 13. Стартовые ориентиры

Floor/ceiling, небольшой discovery corpus, human gold set и repeated runs могут быть полезными cold-start эвристиками. Они не являются release-нормами.

Если пользователь спрашивает «сколько cases?» или «какой pass rate?», не придумывать точное число. Разделить:

- `discovery seed` — минимальный набор для обнаружения dimensions и failure categories;
- `release sample` — набор, поддерживающий заявленный risk/reliability claim;
- `production evidence` — live distribution и downstream outcomes.

Размер release sample и threshold выводить в таком порядке:

1. Зафиксировать цену false pass/false fail, максимальный допустимый risk и blocking red lines.
2. Получить либо явно оценить prevalence каждого consequential slice.
3. Запустить discovery seed и оценить baseline failure rate и variance.
4. Выбрать confidence/power или maximum uncertainty, которую допускает product owner.
5. Рассчитать per-slice sample size и repetitions; продолжать adaptive collection, пока coverage и uncertainty не достигли принятой policy.

При нуле observed failures односторонняя верхняя граница истинной failure rate зависит от `n` и confidence; использовать exact binomial interval либо приближение `-ln(alpha) / n`, а не утверждать, что «ноль ошибок» доказывает надёжность.

Если risk target, baseline или variance неизвестны, честный ответ: release sample size и pass threshold пока `unknown`. Разрешено предложить маленький provisional seed для следующего обратимого эксперимента, но обязательно:

- назвать его planning assumption, а не стандартом;
- объяснить, какие dimensions он должен открыть;
- задать adaptive stopping rule;
- не использовать его результат как production release gate.

Детерминированный invariant вроде schema validity или запрета critical false pass может требовать 100% на наблюдённом наборе. Это policy red line, но само по себе не доказывает статистическую частоту ошибки вне набора.

## 14. Human-readable template

```markdown
# EvalSuite: <capability> v<version>

Status / owner / frozenAt:
Consumer / downstream decision:
Source provenance / data policy:
Exact model-context-rules-tools versions:

## Behavior
Capability:
Expected output/action contract:
Ambiguity/abstention/fallback policy:

## Coverage
Floor:
Ceiling:
Dimensions:
Slices and sample sizes:
Case schema/location:

## Metrics and gates
Primary/counter-metrics:
Per-slice thresholds:
Red lines:
Blocking flags:

## Judge
Deterministic checks:
Judge version/criteria:
Calibration set and false pass/false fail:

## Run policy
Parameters/repetitions/variance:
Token-cost budget/deadline:
CI/shadow/canary commands:

## Production link
Regression admission policy:
Regression Registry entry:
OutcomeRecord / observation window:
Stale/supersede conditions:
```

## 15. Self-check

Общий self-check — в [`../SKILL.md`](../SKILL.md). Здесь только то, что проверяется именно этим файлом.

1. Есть floor, ceiling и meaningful dimensions?
2. Deterministic checks выполняются до LLM-judge?
3. Judge откалиброван по false pass и false fail?
4. Thresholds заданы по slices и risk, а не одним средним score?
5. Sample size и thresholds выведены из risk/baseline/variance/confidence, а не придуманы?

## Методологическая основа

Cold-start часть адаптирует идеи раздатки Михаила Карпова / AI Product Club [«Cold-start eval: как собрать первый eval, когда у тебя ноль данных»](https://drive.google.com/file/d/1RfWeSkRn5MgI8QVNc5ZAriymZsnlI31K/view). Это независимая инженерная интерпретация: численные ориентиры источника рассматриваются как эвристики и дополнены требованиями ProjectContract, Oper8, production evidence, privacy, tokenomics и outcome tracking.
