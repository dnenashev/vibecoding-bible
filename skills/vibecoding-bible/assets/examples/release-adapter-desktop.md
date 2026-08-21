# Пример: release adapter для desktop-приложения

Иллюстрация к разделу «Выполнить release adapter» в [`references/bug-repair.md`](../../references/bug-repair.md). Это пример одного проекта, а не требование канона: другой проект подставляет собственные commands, artifact target и platform checks.

Для desktop-приложения Schema универсальные роли могут отображаться так:

- `release:prepare` сначала сверяет release intent, accepted handoffs, provenance и capability evidence, затем собирает immutable candidate из clean cumulative head и выдаёт subject/evidence;
- пользователь запускает isolated candidate и даёт `QA PASS`, связанный с candidate hash;
- точный `ACCEPT` разрешает изменение `/Applications/Schema.app`;
- `schema-release-controller` проверяет codesign, устанавливает candidate, выполняет readback/rollback и подтверждает единственный экземпляр Schema в Launchpad.

Это пример adapter contract. Другой проект подставляет собственные commands, artifact target и platform checks.
