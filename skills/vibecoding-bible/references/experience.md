# Experience: понятный и доступный продукт

## Содержание

1. Назначение
2. Рабочий протокол
3. UX до визуального polish
4. Information architecture
5. Interaction design
6. Состояния и ошибки
7. Content design
8. Accessibility
9. Responsive и adaptive behavior
10. Правила для разных surfaces
11. Design system и shadcn
12. Usability validation
13. Handoff в build и verify
14. Антипаттерны
15. Короткие шаблоны
16. Self-check

## 1. Назначение

Применять в фазе `DESIGN`, а затем при `BUILD` и `VERIFY` для любого пользовательского или операторского interface.

Проектировать experience, в котором человек понимает:

- где он находится;
- что может сделать;
- что произошло;
- что делать дальше;
- как отменить действие или восстановиться после ошибки.

Не сводить experience design к цветам, компонентам и красивому mockup.

## 2. Рабочий протокол

1. Получить Product Brief и ключевой user journey.
2. Назвать surface, device/context и constraints.
3. Определить information architecture и vocabulary.
4. Спроектировать основной interaction path.
5. Добавить состояния, ошибки, recovery и permissions.
6. Проверить accessibility и responsive/adaptive behavior.
7. Применить существующий design system или выбрать минимальный default.
8. Описать screen/interaction contracts до визуального polish.
9. Проверить journey на representative tasks.
10. Передать build-ready states, content и acceptance evidence.

Не начинать с component gallery. Сначала доказать, что flow понятен и завершает пользовательскую задачу.

## 3. UX до визуального polish

Начать с:

- actor и goal;
- trigger и entry point;
- частоты и срочности задачи;
- device, input method и environment;
- уровня знаний пользователя;
- цены ошибки;
- необходимых данных и permissions;
- terminal outcome.

Сделать основной путь коротким, но не скрывать критическую информацию или контроль. Убирать шаги, не меняющие решение, безопасность или evidence.

Использовать progressive disclosure: показывать обязательное сейчас, дополнительные детали — по запросу или контексту. Не прятать риски, цену и последствия внешнего действия.

Оптимизировать не число экранов само по себе, а effort до принятого outcome.

## 4. Information architecture

Организовывать interface вокруг пользовательских объектов и действий, а не внутренней структуры database или команды разработки.

Определить:

- основные объекты и их понятные имена;
- отношения и иерархию объектов;
- главные действия для каждого объекта;
- global и contextual navigation;
- search/filter/sort при реальной необходимости;
- location/orientation cues;
- способ вернуться или отменить;
- source of truth для спорных названий.

Использовать один термин для одного понятия. Не менять vocabulary между navigation, labels, errors и документацией.

Проверить IA вопросами:

- найдёт ли пользователь нужный объект без знания внутренней системы;
- понимает ли разницу соседних разделов;
- видит ли current scope, account, tenant или environment;
- не смешаны ли создание, управление и аналитика в одном перегруженном view.

## 5. Interaction design

Для каждого действия определить:

- явный affordance;
- preconditions и доступность;
- input и validation timing;
- immediate feedback;
- progress для долгой операции;
- success confirmation;
- retry/cancel/undo;
- effect на state и внешние systems;
- keyboard/touch/assistive path по surface.

Предпочитать безопасные defaults и обратимые действия. Для consequential mutation показывать exact target, scope и последствия до подтверждения.

Не требовать повторно вводить уже известные данные без privacy/security причины. Не блокировать пользователя из-за необязательного поля.

Для async operation отделять `запрос принят` от `операция завершена`. Показывать статус, freshness и путь к актуальному результату.

## 6. Состояния и ошибки

Проектировать состояния до implementation:

- initial;
- loading или progressive loading;
- empty-first-use;
- empty-filtered;
- partial data;
- success;
- validation error;
- permission/authentication error;
- integration/network failure;
- timeout/rate limit;
- stale/conflict;
- offline/degraded;
- canceled;
- irreversible/partially completed mutation;
- retry/recovery;
- unsupported state/version.

Для каждой ошибки сообщать:

1. Что произошло понятным языком.
2. Что сохранилось или изменилось.
3. Что пользователь может сделать сейчас.
4. Где получить помощь или reference ID, если self-recovery невозможен.

Не обвинять пользователя. Не показывать raw stack trace, provider secret или внутреннюю topology. Сохранять технические детали в безопасном diagnostic evidence.

Не использовать бесконечный spinner без статуса, timeout и recovery path.

## 7. Content design

Писать коротко, конкретно и на языке пользователя.

Для labels и actions:

- называть действие глаголом;
- отражать реальный эффект;
- избегать неоднозначного `OK`, если можно назвать действие;
- сохранять терминологию во всём journey;
- помещать важное предупреждение рядом с решением;
- не прятать limitation в tooltip или legal text.

Для confirmation:

- назвать exact object/target;
- объяснить обратимость;
- показать стоимость/срок/permission impact по применимости;
- не использовать dark patterns и заранее выбранное опасное действие.

Для AI-generated content обозначать существенную uncertainty, source/freshness и доступный путь correction там, где это влияет на решение. Не перегружать interface внутренними AI-терминами.

## 8. Accessibility

Считать accessibility частью correctness, а не дополнительным polish.

Проверить по применимости:

- semantic structure и landmarks;
- доступное имя каждого control;
- keyboard navigation и отсутствие traps;
- видимый, логичный focus;
- screen reader reading order и dynamic announcements;
- contrast и отсутствие color-only meaning;
- масштабирование текста и reflow;
- touch/pointer target и spacing;
- reduced motion;
- captions/transcripts/alt text;
- понятные validation errors и связь с полем;
- timeout extension и отсутствие неожиданной потери данных.

Использовать native controls и platform conventions раньше custom behavior. Проверять фактический interface инструментами и representative assistive path; visual inspection не заменяет accessibility evidence.

Не придумывать уровень conformance. Выбирать применимые требования из продукта, рынка и regulation, затем фиксировать их в acceptance.

## 9. Responsive и adaptive behavior

Проектировать не набор скриншотов, а правила изменения layout и interaction.

Определить:

- приоритет контента на узком пространстве;
- stacking, wrapping и overflow;
- navigation transformation;
- behavior таблиц, графиков и сложных editors;
- touch/keyboard/pointer differences;
- portrait/landscape или window resizing;
- loading и performance constraints на слабом device/network;
- continuity при смене device/context.

Не уменьшать desktop layout до нечитаемого mobile view. Если задача на mobile принципиально другая, использовать adaptive flow.

Проверять минимум representative narrow, wide и zoomed states, выбирая размеры из supported platforms, а не из универсальной магической сетки.

## 10. Правила для разных surfaces

### Web

Учитывать browser navigation, URL/deep link, refresh, responsive behavior, keyboard, network variability и accessibility semantics.

### Mobile

Следовать platform conventions, учитывать lifecycle/background, permissions, interrupted flow, touch, offline, limited space и store constraints.

### Desktop

Учитывать resizable windows, keyboard shortcuts, menus, multi-window, filesystem/OS permissions и долгие professional workflows.

### CLI

Проектировать help, discoverable commands, stdin/stdout/stderr, exit codes, non-interactive mode, confirmation для destructive action, progress без поломки pipes и machine-readable output.

### Automation и API-only product

Считать experience контрактом интегратора/оператора: понятные schemas, validation, status, error taxonomy, idempotency, observability, docs/examples и recovery.

### Conversational/AI interface

Показывать capability boundaries, confirmation перед consequential tool action, provenance по необходимости, возможность correction и ясный handoff при uncertainty.

Не переносить web component rules механически на CLI, mobile или API.

## 11. Design system и shadcn

Сначала использовать существующий design system проекта. Получить actual tokens, components, variants и conventions из source; не реконструировать их по screenshot или памяти.

Design system обязан помогать:

- сохранять consistency;
- кодировать accessibility и states;
- уменьшать дублирование;
- ускорять безопасные изменения.

Не создавать custom component, если существующий покрывает interaction честно. Не искажать interaction только ради повторного использования неподходящего component.

Для web-проекта с `components.json` использовать actual shadcn project context и доступный shadcn workflow. Проверять registry/component API для exact project setup. Считать shadcn conditional default для подходящего web stack, а не универсальной зависимостью.

Для проекта без shadcn не мигрировать design system без отдельной причины и scope. Для mobile/desktop/CLI использовать native или принятые project conventions.

## 12. Usability validation

Проверять experience на задачах, а не вопросом «нравится ли дизайн».

Для каждого critical journey:

1. Дать participant/representative actor реалистичный goal и input.
2. Не раскрывать правильный путь.
3. Наблюдать точки hesitation, ошибки, обходные пути и recovery.
4. Отделить defect interface от knowledge/domain gap.
5. Исправить причину и повторить representative task.
6. Превратить подтверждённый failure в regression/acceptance case.

Собирать по необходимости:

- task completion и terminal outcome;
- critical errors;
- time/effort относительно baseline;
- recovery success;
- comprehension/decision confidence;
- accessibility evidence;
- qualitative reason behind failure.

Не устанавливать универсальное число participants или threshold. Выбирать силу evidence по риску, вариативности аудитории и цене ошибки.

Для EXPLORE разрешать prototype evidence с explicit limitations. Для BUILD проверять implemented representative journey. Для CRITICAL добавлять независимую проверку high-impact paths и assistive use cases по риску.

## 13. Handoff в build и verify

Передать не только mockup, а build-ready Experience Contract:

- journey и surface;
- IA/vocabulary;
- view/screen responsibilities;
- actions и permissions;
- states/errors/recovery;
- content/copy;
- responsive/adaptive rules;
- accessibility acceptance;
- analytics events, связанные с product hypothesis;
- visual references/tokens/components;
- open unknowns и owner;
- required evidence.

Указывать frozen version. При изменении journey, state model или consequential copy создать новую version и проверить зависимые tests/implementation.

Не объявлять handoff завершённым, если отсутствуют error, empty, loading или permission states для основного journey.

## 14. Антипаттерны

- Начинать с visual style до user journey.
- Копировать competitor screen без понимания context.
- Проектировать только happy path.
- Скрывать critical action за icon без accessible label.
- Использовать modal для каждого решения.
- Показывать spinner вместо operation state.
- Делать disabled action без объяснения.
- Подменять usability личным вкусом или screenshot review.
- Использовать placeholder как единственный label.
- Передавать разработке только картинку без states и behavior.
- Делать собственные controls там, где native semantic control подходит.
- Навязывать shadcn, web layout или visual UI неподходящему surface.

## 15. Короткие шаблоны

### Experience Brief

```markdown
User/goal/trigger:
Surface/context/constraints:
Primary journey:
Information objects/vocabulary:
Main actions and permissions:
Critical states/recovery:
Accessibility requirements:
Responsive/adaptive rules:
Design system/components:
Validation task/evidence:
Open unknown + owner:
```

### Screen или view contract

```markdown
Responsibility:
Entry/preconditions:
Content/data/freshness:
Actions and effects:
Initial/loading/empty/success/error states:
Retry/cancel/undo/recovery:
Keyboard/touch/assistive behavior:
Responsive behavior:
Analytics tied to outcome:
Acceptance evidence:
```

### Error contract

```markdown
Condition:
User-facing explanation:
State preserved/changed:
Primary recovery action:
Fallback/support/reference ID:
Diagnostic evidence without sensitive data:
```

## 16. Self-check

1. Experience начинается с user goal и journey, а не компонентов?
2. Vocabulary и IA понятны без знания внутренней системы?
3. Основной путь минимален, но не скрывает риск и последствия?
4. Loading, empty, partial, error, permission и recovery states определены?
5. Async accepted и completed states не перепутаны?
6. Content называет действие и реальный эффект?
7. Accessibility встроена в behavior и acceptance?
8. Responsive описан правилами, а не только несколькими картинками?
9. Surface-specific conventions соблюдены?
10. Existing design system проверен по source?
11. shadcn применён только к подходящему web context?
12. Usability проверена representative task без подсказки?
13. Handoff содержит states, behavior и evidence, а не только mockup?
14. Пользователю понятен один следующий шаг?
