#!/usr/bin/env python3
"""Валидатор Regression Registry.

Проверяет то, что раздел «CI и validation» в references/regression-registry.md
требует проверять машиной: schema, уникальность id, существование locations,
допустимые значения, owner, quarantine, отсутствие secrets.

Использование:
    python3 validate_registry.py path/to/registry.yaml [--root PROJECT_ROOT] [--strict]

Коды возврата: 0 — ошибок нет, 1 — есть ERROR, 2 — не удалось прочитать вход.
С флагом --strict WARN тоже считается ошибкой.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Нужен pyyaml: python3 -m pip install pyyaml")

SCHEMA = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "registry-entry.schema.json"

SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{16,}"), "похоже на API key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}"), "похоже на GitHub token"),
    (re.compile(r"\bAKIA[0-9A-Z]{12,}"), "похоже на AWS access key"),
    (re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[=:]\s*\S+"), "секрет в открытом виде"),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]{16,}"), "bearer token"),
]

NEEDS_EXECUTION = {"static", "unit", "component", "contract", "integration", "e2e",
                   "security", "performance", "accessibility", "eval", "harness"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"ERROR {where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"WARN  {where}: {message}")


def load_entries(path: Path) -> list[dict]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for key in ("entries", "registry", "tests"):
            if isinstance(doc.get(key), list):
                return doc[key]
        if "id" in doc:
            return [doc]
    raise SystemExit(f"{path}: ожидается список записей либо ключ entries/registry/tests")


def scan_secrets(entry: dict, report: Report, where: str) -> None:
    blob = json.dumps(entry, ensure_ascii=False)
    for pattern, label in SECRET_PATTERNS:
        if pattern.search(blob):
            report.error(where, f"{label}; секреты в Registry запрещены")


def check_entry(entry: dict, index: int, root: Path, ids: set[str], report: Report, validator) -> None:
    where = f"[{index}] {entry.get('id', '<без id>')}"

    for err in sorted(validator.iter_errors(entry), key=lambda e: list(e.path)):
        location = "/".join(str(p) for p in err.path) or "<корень>"
        report.error(where, f"schema: {location}: {err.message}")

    status = entry.get("status")
    level = entry.get("level")

    if status == "active" and not entry.get("owner"):
        report.error(where, "active entry обязана иметь owner")

    if status in {"active", "quarantined"} and level in NEEDS_EXECUTION:
        if not entry.get("command") and not entry.get("procedure"):
            report.error(where, f"level {level} требует command или procedure ref")

    location = entry.get("location")
    if location and status != "draft":
        target = (root / location).resolve()
        if not target.exists():
            base = location.split("::")[0].split("#")[0]
            if not (root / base).exists():
                report.error(where, f"location не существует: {location}")

    if status == "quarantined":
        q = entry.get("quarantine")
        if not isinstance(q, dict):
            report.error(where, "quarantined entry обязана иметь блок quarantine")
        else:
            if not q.get("issue"):
                report.warn(where, "quarantine без ссылки на issue")
            if not q.get("compensating_control"):
                report.warn(where, "quarantine без compensating control")
            expiry = q.get("expiry")
            if expiry:
                try:
                    if _dt.date.fromisoformat(expiry) < _dt.date.today():
                        report.error(where, f"quarantine истёк {expiry}; нужен новый verdict")
                except ValueError:
                    report.error(where, f"quarantine.expiry не дата ISO: {expiry}")
    elif entry.get("quarantine"):
        report.error(where, "блок quarantine заполнен, но status не quarantined")

    if status == "superseded" and not entry.get("supersedes"):
        report.warn(where, "superseded entry без ссылки supersedes")

    sup = entry.get("supersedes")
    if sup and sup not in ids:
        report.error(where, f"supersedes ссылается на неизвестный id: {sup}")

    if entry.get("blocking") and status == "draft":
        report.error(where, "draft entry не может быть blocking gate")

    data = entry.get("data") or {}
    if data.get("classification") == "production":
        report.warn(where, "production data в fixture; проверить privacy и retention")

    scan_secrets(entry, report, where)


def main() -> int:
    parser = argparse.ArgumentParser(description="Валидатор Regression Registry")
    parser.add_argument("registry", type=Path)
    parser.add_argument("--root", type=Path, default=None,
                        help="корень проекта для проверки location (по умолчанию каталог registry)")
    parser.add_argument("--strict", action="store_true", help="считать WARN ошибкой")
    args = parser.parse_args()

    if not args.registry.exists():
        print(f"Файл не найден: {args.registry}", file=sys.stderr)
        return 2

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Нужен jsonschema: python3 -m pip install jsonschema", file=sys.stderr)
        return 2

    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    root = (args.root or args.registry.parent).resolve()
    entries = load_entries(args.registry)
    report = Report()

    seen: dict[str, int] = {}
    ids = {e.get("id") for e in entries if isinstance(e, dict)}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            report.error(f"[{index}]", "запись не является объектом")
            continue
        entry_id = entry.get("id")
        if entry_id in seen:
            report.error(f"[{index}] {entry_id}", f"дублирующийся id, первый раз в [{seen[entry_id]}]")
        elif entry_id:
            seen[entry_id] = index
        check_entry(entry, index, root, ids, report, validator)

    for line in report.errors + report.warnings:
        print(line)

    active = sum(1 for e in entries if isinstance(e, dict) and e.get("status") == "active")
    print(f"\nЗаписей: {len(entries)}, active: {active}, "
          f"ошибок: {len(report.errors)}, предупреждений: {len(report.warnings)}")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
