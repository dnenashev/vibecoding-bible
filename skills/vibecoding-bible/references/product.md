# Product: от идеи до проверяемого scope

## Содержание

1. Назначение
2. Рабочий протокол
3. Пользователь, проблема и current way
4. Outcome и продуктовая гипотеза
5. Facts, assumptions и unknowns
6. Дешёвая проверка идеи
7. Product Brief
8. User journeys
9. Requirements и acceptance
10. Scope и приоритеты
11. Analytics hypothesis
12. Режимы строгости
13. Антипаттерны
14. Короткие шаблоны
15. Self-check

## 1. Назначение

Применять в фазе `UNDERSTAND` и на продуктовой части `DESIGN`.

Переводить идею, просьбу или симптом в маленький проверяемый продуктовый scope. Не начинать с framework, экрана или AI-функции, пока не понятны пользователь, проблема и ожидаемое изменение.

Считать результатом product work принятое решение:

- строить;
- сначала проверить неизвестное;
- сузить или изменить scope;
- не строить.

Не считать объём документа признаком качества решения.

## 2. Рабочий протокол

1. Назвать пользователя или consumer результата.
2. Описать проблему и существующий способ её решения.
3. Отделить наблюдаемые факты от предположений и неизвестного.
4. Сформулировать ожидаемый outcome и counter-signal.
5. Найти unknown с наибольшим риском для outcome.
6. Выбрать самый дешёвый честный способ проверить его.
7. Сформировать Product Brief и ключевые user journeys.
8. Превратить journeys в проверяемые requirements.
9. Выбрать минимальный законченный vertical slice.
10. Передать подтверждённый scope в architecture и experience design.

Не задавать пользователю длинную анкету. Извлекать известное из разговора и source evidence, показывать только решения и вопросы, которые меняют следующий шаг.

## 3. Пользователь, проблема и current way

Определить:

- кто сталкивается с проблемой;
- в каком контексте и по какому trigger;
- какую задачу или решение пытается завершить;
- как делает это сейчас;
- где теряет время, деньги, качество, контроль или уверенность;
- почему существующий способ всё ещё используется;
- кто получает результат и кто принимает решение о покупке/внедрении.

Описывать проблему через наблюдаемое поведение, а не через отсутствие предполагаемой функции.

Плохо: `пользователю нужен AI-дашборд`.

Лучше: `оператор вручную сверяет три источника перед решением и не видит расхождения вовремя`.

Если пользователь и consumer различаются, зафиксировать обоих. Если проблема не подтверждена, пометить её как hypothesis.

## 4. Outcome и продуктовая гипотеза

Формулировать outcome как наблюдаемое изменение после использования продукта:

```text
Для <пользователь/consumer>
в ситуации <trigger/context>
продукт помогает <завершить действие или принять решение>
так, что <наблюдаемый результат>,
не ухудшая <counter-signal>.
```

Различать:

- `output` — созданный экран, отчёт, сообщение или API response;
- `outcome` — изменившееся действие, решение или состояние;
- `impact` — более дальний бизнес- или пользовательский эффект.

Не обещать impact, если доступно только evidence уровня output или outcome.

Зафиксировать причинную гипотезу: какое изменение поведения продукта должно привести к outcome и почему.

## 5. Facts, assumptions и unknowns

Вести короткий decision-oriented список:

- `fact` — подтверждено интервью, analytics, source/runtime или другим проверяемым evidence;
- `assumption` — принято временно и имеет способ проверки;
- `unknown` — ответа нет; назначены probe и решение, которое зависит от ответа;
- `not_applicable` — неприменимо с короткой причиной.

Приоритизировать unknown по сочетанию:

- способен ли он отменить продукт или выбранный scope;
- насколько дорого ошибиться;
- насколько дёшево получить evidence;
- блокирует ли он необратимое решение.

Не превращать каждую мелочь в исследование. Проверять сначала неизвестное, способное изменить решение.

## 6. Дешёвая проверка идеи

Выбирать experiment по типу риска:

| Риск | Практичная проверка |
|---|---|
| Проблема несущественна | Интервью о реальном прошлом поведении, разбор текущего процесса, support evidence |
| Нет спроса или обязательства | Concierge/pilot, предзаказ, заявка, согласие дать данные или время |
| Решение непонятно | Task-based prototype test без подсказок |
| Решение технически невозможно | Bounded feasibility spike на реальном boundary |
| Экономика не сходится | Cost model на единицу принятого outcome |
| Внедрение невозможно | Проверка permissions, ownership, integration и workflow change |

Для experiment заранее определить:

- hypothesis и главный unknown;
- participant/data/source;
- procedure;
- success/failure signal;
- safety и time/cost box;
- решение `discard | continue | promote`.

Не использовать выдуманные интервью, synthetic demand или mock integration как подтверждение реального спроса и feasibility.

Не назначать произвольное число интервью, примеров или прогонов. Если baseline и variance неизвестны, ограничить probe временем/стоимостью и продолжать до появления повторяющегося сигнала, нового класса failure либо исчерпания budget; решение о promotion всё равно остаётся provisional.

## 7. Product Brief

Собрать Brief после первичного discovery. Держать его коротким и изменяемым до freeze.

Включить:

- target user/consumer;
- trigger и problem/current way;
- expected outcome и counter-signal;
- facts/assumptions/critical unknown;
- value hypothesis;
- ключевой journey;
- минимальный vertical slice;
- exclusions/non-goals;
- validation и analytics hypothesis;
- mode `EXPLORE | BUILD | CRITICAL`;
- open decisions и owners.

Freeze Brief перед build-ready design. При изменении outcome или scope создать новую version и пометить зависимые decisions stale.

## 8. User journeys

Описывать journey от trigger до результата, а не только последовательность экранов.

Для каждого ключевого journey определить:

- actor и goal;
- trigger и preconditions;
- entry point;
- основной путь;
- альтернативные пути;
- missing/invalid input;
- permission/integration failure;
- cancel, retry и recovery;
- terminal success state;
- downstream consumer/action;
- evidence успешного завершения.

Отделять user journey от внутреннего workflow. Один пользовательский шаг может включать несколько системных операций; не раскрывать их пользователю без необходимости.

Приоритизировать сначала один end-to-end journey. Добавлять соседние journeys только если без них slice не работает честно.

## 9. Requirements и acceptance

Писать functional requirement через наблюдаемое поведение:

```text
Когда <условие>, система <поведение>, чтобы <outcome>.
Acceptance: <проверяемые примеры success/failure>.
```

Для каждого requirement определить по применимости:

- actor и permission;
- input и validation;
- expected behavior/output;
- empty/error/retry/cancel path;
- state/persistence effect;
- external side effect;
- acceptance evidence.

Формулировать non-functional requirements по реальному риску:

- availability/reliability;
- response time/capacity;
- privacy/security;
- accessibility;
- compatibility;
- maintainability/operability;
- cost boundary.

Не придумывать универсальные числовые thresholds. Получать их из user need, baseline, regulation, dependency contract или измеримого business constraint. Помечать ещё не подтверждённые значения как assumption.

Не смешивать requirement и implementation decision. `Пользователь может восстановить работу после ошибки` — requirement; `использовать Redis` — возможное architecture decision.

## 10. Scope и приоритеты

Выбирать scope по четырём вопросам:

1. Без какого behavior основной outcome невозможен?
2. Какой риск нужно доказать раньше необратимых решений?
3. Что образует законченный vertical slice?
4. Что можно безопасно отложить без production deception?

Разделить:

- `now` — необходимо для текущего outcome и честной эксплуатации;
- `later` — полезно, но не блокирует outcome;
- `not now` — явно исключено;
- `never/avoid` — противоречит стратегии или создаёт лишний риск.

Не вырезать из slice required error handling, permissions, data integrity, observability или rollback только ради меньшего объёма. Сокращать число journeys, ролей, integrations и вариантов.

Отдельно фиксировать scope traps: «заодно», generalized platform, premature multi-tenancy, custom framework и AI там, где достаточно deterministic logic.

## 11. Analytics hypothesis

Связать measurement с решением, а не со сбором всех событий.

Определить:

- какое действие или решение должно измениться;
- какой observable event/state является leading signal;
- какой downstream outcome подтвердит ценность;
- какой counter-signal обнаружит вред;
- source of truth и owner;
- сегменты, без которых aggregate вводит в заблуждение;
- observation window, заданное доменом;
- какое решение принять для каждого возможного результата.

Не считать page views, clicks или AI score автоматически продуктовой ценностью. Не собирать PII «на будущее». Проверить implementability событий в architecture и production modules.

## 12. Режимы строгости

### EXPLORE

Проверять один критический unknown. Использовать disposable prototype или bounded spike, explicit non-production label и решение о продолжении.

### BUILD

Подтвердить Product Brief, основной journey, requirements, acceptance и analytics hypothesis для production-ready slice. Использовать как default.

### CRITICAL

Добавить независимых reviewers/owners по применимости, misuse/abuse journeys, compliance constraints, failure/recovery requirements и более сильное evidence. Не превращать criticality в длинную общую анкету.

## 13. Антипаттерны

- Начинать discovery с feature list или stack.
- Выдавать мнение пользователя о будущем за факт о прошлом поведении.
- Валидировать problem только реакцией «звучит интересно».
- Подгонять problem под уже выбранное решение.
- Путать AI output с пользовательским outcome.
- Строить все personas и journeys до проверки основного.
- Писать requirements как список технологий.
- Добавлять «масштабируемость» без load/constraint.
- Использовать vanity metrics без связанного решения.
- Называть незавершённый core flow MVP и обещать production-ready.

## 14. Короткие шаблоны

### Product Brief

```markdown
# Product Brief: <name> v<version>
Mode:
User/consumer + trigger:
Problem/current way + evidence:
Expected outcome / counter-signal:
Facts / assumptions / critical unknown:
Value hypothesis:
Primary journey:
Now / later / not now:
Validation:
Analytics hypothesis:
Open decision + owner:
```

### Journey

```markdown
Actor / goal / trigger:
Preconditions / entry:
Main path:
Alternatives and failures:
Recovery/cancel:
Terminal outcome:
Evidence:
```

### Requirement

```markdown
When:
System behavior:
Outcome:
Acceptance examples:
Required evidence:
```

### Experiment card

```markdown
Unknown / hypothesis:
Why it changes the decision:
Source/participant:
Procedure and safety box:
Success/failure signal:
Discard / continue / promote rule:
```

## 15. Self-check

1. Названы реальный пользователь, consumer и trigger?
2. Проблема описана через current behavior, а не отсутствие функции?
3. Outcome отделён от output и дальнего impact?
4. Facts, assumptions и unknowns разделены?
5. Первым проверяется неизвестное, способное изменить решение?
6. Validation использует реальное evidence и заранее заданный decision rule?
7. Основной journey заканчивается downstream outcome?
8. Requirements наблюдаемы и не зашивают преждевременно implementation?
9. Scope образует маленький, но честный vertical slice?
10. Non-functional requirements и thresholds основаны на риске/constraints?
11. Analytics отвечает на решение и содержит counter-signal?
12. Пользователю понятен один следующий шаг?
