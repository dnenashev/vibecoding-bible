#!/usr/bin/env python3
"""Валидатор skill vibecoding-bible.

Детерминированные проверки, которые иначе пришлось бы делать модели вручную:

1. frontmatter: имя, описание, лицензия;
2. VERSION: формат SemVer и связь с git tag;
3. ссылки: все внутренние markdown-ссылки резолвятся;
4. словарь: enum-токены употребляются согласованно, старая модель не возвращается;
5. корпус forward-cases: id, kind, ожидания, отсутствие захардкоженной версии;
6. установленные копии совпадают с релизным деревом.

Использование: python3 scripts/validate_skill.py [--strict]
Коды возврата: 0 — ошибок нет, 1 — есть ERROR.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Нужен pyyaml: python3 -m pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "vibecoding-bible"
CASES = REPO / "tests" / "forward-cases.yaml"
INSTALLS = [
    Path.home() / ".codex" / "skills" / "vibecoding-bible",
    Path.home() / ".claude" / "skills" / "vibecoding-bible",
]

PHASES = {"UNDERSTAND", "DESIGN", "BUILD", "VERIFY", "SHIP", "LEARN"}
MODES = {"EXPLORE", "BUILD"}
RISKS = {"LOW", "STANDARD", "CRITICAL"}
KINDS = {"positive", "negative", "boundary"}

# Формулировки модели до 2.0.0; допустимы только в разделе переноса vocabulary.md.
LEGACY = [
    ("EXPLORE | BUILD | CRITICAL", "старая одномерная шкала режимов"),
    ("Mode: EXPLORE", "старое поле Mode в шаблоне"),
    ("modes: [", "поле modes в записи Registry заменено на risk"),
    ("Режим строгости", "раздел заменён на «Режим и риск»"),
]

TOKEN = re.compile(r"`([A-Z][A-Z_]{2,}(?: [A-Z]+)?)`")
# Имена файлов и служебные слова — не значения словаря.
NOT_ENUM = {"VERSION", "README", "LICENSE", "SKILL", "CONTRIBUTING", "CHANGELOG", "TODO"}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"ERROR {where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"WARN  {where}: {msg}")


def skill_files() -> list[Path]:
    return sorted([SKILL / "SKILL.md", *(SKILL / "references").glob("*.md"),
                   *(SKILL / "assets" / "templates").glob("*.md")])


def check_frontmatter(report: Report) -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        report.error("SKILL.md", "нет YAML frontmatter")
        return
    raw = text.split("---", 2)[1]
    meta = yaml.safe_load(raw) or {}
    if meta.get("name") != SKILL.name:
        report.error("SKILL.md", f"name={meta.get('name')!r} не совпадает с каталогом {SKILL.name!r}")
    description = meta.get("description", "")
    if not description:
        report.error("SKILL.md", "пустой description")
    elif len(description) > 1024:
        report.error("SKILL.md", f"description {len(description)} символов, лимит 1024")
    if not meta.get("license"):
        report.warn("SKILL.md", "во frontmatter нет license, а в репозитории LICENSE есть")


def check_version(report: Report) -> None:
    version = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        report.error("VERSION", f"не SemVer: {version!r}")
        return
    try:
        tags = subprocess.run(["git", "-C", str(REPO), "tag", "--points-at", "HEAD"],
                              capture_output=True, text=True, timeout=10).stdout.split()
    except Exception:
        tags = []
    if tags and f"v{version}" not in tags:
        report.error("VERSION", f"HEAD помечен {tags}, а VERSION={version}")
    if not tags:
        report.warn("VERSION", f"HEAD не помечен тегом v{version}; для релиза тег обязателен")


def check_links(report: Report) -> None:
    for path in skill_files():
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#")[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                report.error(path.relative_to(REPO).as_posix(), f"битая ссылка: {target}")


def check_vocabulary(report: Report) -> None:
    voc_path = SKILL / "references" / "vocabulary.md"
    voc_text = voc_path.read_text(encoding="utf-8")
    declared = set(TOKEN.findall(voc_text))
    declared |= set(re.findall(r"\b([A-Z][A-Z_]{2,})\b", voc_text))

    for path in skill_files():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO).as_posix()
        if path != voc_path:
            for token in set(TOKEN.findall(text)):
                if token not in declared and token not in NOT_ENUM:
                    report.error(rel, f"токен `{token}` не объявлен в vocabulary.md")
        for pattern, reason in LEGACY:
            if pattern in text and path != voc_path:
                report.error(rel, f"осталась старая формулировка «{pattern}»: {reason}")


def check_corpus(report: Report) -> None:
    if not CASES.exists():
        report.warn("tests", "нет forward-cases.yaml")
        return
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    seen: set[str] = set()
    for index, case in enumerate(doc.get("cases", [])):
        where = f"forward-cases[{index}] {case.get('id', '<без id>')}"
        case_id = case.get("id")
        if not case_id:
            report.error(where, "нет id")
        elif case_id in seen:
            report.error(where, "дублирующийся id")
        else:
            seen.add(case_id)
        if case.get("kind", "positive") not in KINDS:
            report.error(where, f"недопустимый kind: {case.get('kind')}")
        if (phase := case.get("expected_phase")) and phase not in PHASES:
            report.error(where, f"недопустимая фаза: {phase}")
        if (mode := case.get("expected_mode")) and mode not in MODES:
            report.error(where, f"недопустимый delivery mode: {mode}")
        if (risk := case.get("expected_risk")) and risk not in RISKS:
            report.error(where, f"недопустимый risk: {risk}")
        if case.get("expected_mode") and not case.get("expected_risk"):
            report.warn(where, "указан mode без risk: оси заполняются вместе")
        for field in ("must_include", "must_not_include"):
            for item in case.get(field, []):
                if not isinstance(item, str):
                    report.error(where, f"{field}: ожидается строка, получено {type(item).__name__}")
                elif re.search(r"\b\d+\.\d+\.\d+\b", item):
                    report.error(where, f"{field}: захардкожена версия; нужен плейсхолдер {{{{VERSION}}}}")


def check_installs(report: Report) -> None:
    release_tree = SKILL.resolve()
    for install in INSTALLS:
        if not install.exists():
            report.warn(str(install), "skill не установлен в этой среде")
            continue
        if install.is_symlink():
            if install.resolve() != release_tree:
                report.error(str(install), f"симлинк ведёт не в релизное дерево: {install.resolve()}")
            continue
        diff = subprocess.run(["diff", "-rq", str(release_tree), str(install)],
                              capture_output=True, text=True)
        if diff.returncode != 0:
            report.error(str(install), "установленная копия расходится с релизным деревом")


def main() -> int:
    parser = argparse.ArgumentParser(description="Валидатор skill vibecoding-bible")
    parser.add_argument("--strict", action="store_true", help="считать WARN ошибкой")
    args = parser.parse_args()

    report = Report()
    check_frontmatter(report)
    check_version(report)
    check_links(report)
    check_vocabulary(report)
    check_corpus(report)
    check_installs(report)

    for line in report.errors + report.warnings:
        print(line)
    print(f"\nОшибок: {len(report.errors)}, предупреждений: {len(report.warnings)}")
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
