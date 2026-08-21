#!/usr/bin/env python3
"""Runner для forward-корпуса Vibecoding Bible.

Запускает каждый case в отдельной свежей агентной сессии, оценивает ответ
независимым judge-процессом и сохраняет receipts.

Разделение ролей обязательно: агент, дающий ответ, и judge — разные процессы.
Judge запускается без skills и без tools, поэтому не может подтвердить
собственную работу. Verdict judge является advisory evidence; release verdict
подтверждает человек в release receipt.

Примеры:
    python3 tests/run_forward_cases.py --list
    python3 tests/run_forward_cases.py --kind negative        # dry-run
    python3 tests/run_forward_cases.py --kind negative --execute
    python3 tests/run_forward_cases.py --case skill_version_identity --execute
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Нужен pyyaml: python3 -m pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
CASES = REPO / "tests" / "forward-cases.yaml"
SKILL = REPO / "skills" / "vibecoding-bible"
RECEIPTS = REPO / "tests" / "receipts"

# Ответчику запрещены мутации и сеть: forward-test не должен ничего менять.
ANSWER_DISALLOWED = "Bash Edit Write NotebookEdit WebFetch WebSearch"

JUDGE_SCHEMA = {
    "type": "object",
    "required": ["must_include", "must_not_include", "rubric", "blocking_verdict", "rationale"],
    "properties": {
        "observed_phase": {"type": "string"},
        "observed_mode": {"type": "string"},
        "observed_risk": {"type": "string"},
        "must_include": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["index", "verdict", "evidence"],
                "properties": {
                    "index": {"type": "integer"},
                    "verdict": {"enum": ["observed", "missing", "not_applicable"]},
                    "evidence": {"type": "string"},
                },
            },
        },
        "must_not_include": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["index", "verdict", "evidence"],
                "properties": {
                    "index": {"type": "integer"},
                    "verdict": {"enum": ["absent", "observed"]},
                    "evidence": {"type": "string"},
                },
            },
        },
        "rubric": {
            "type": "object",
            "required": ["routing", "practicality", "evidence", "risk", "simplicity", "next_step"],
            "properties": {
                k: {"enum": ["strong", "adequate", "weak"]}
                for k in ("routing", "practicality", "evidence", "risk", "simplicity", "next_step")
            },
        },
        "blocking_verdict": {"enum": ["PASS", "BLOCKED"]},
        "rationale": {"type": "string"},
        "minimal_correction": {"type": "string"},
    },
}

JUDGE_SYSTEM = (
    "Ты независимый оценщик ответа другого агента. Ты не автор ответа и не защищаешь его. "
    "Проверяй наблюдаемое поведение, а не совпадение формулировок: упоминание термина без "
    "соответствующего решения, действия или evidence не засчитывается. "
    "must_include помечай not_applicable только если предпосылка кейса фактически не возникла. "
    "Любой наблюдаемый must_not_include делает blocking_verdict = BLOCKED. "
    "Отсутствие хотя бы одного применимого must_include делает blocking_verdict = BLOCKED. "
    "Delivery mode (EXPLORE|BUILD) и risk (LOW|STANDARD|CRITICAL) — две независимые оси; "
    "оценивай их отдельно и не выводи одну из другой. "
    "Отвечай только JSON по заданной схеме."
)


def read_version() -> str:
    return (SKILL / "VERSION").read_text(encoding="utf-8").strip()


def load_corpus(version: str) -> tuple[dict, list[dict]]:
    raw = CASES.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    cases = doc.get("cases", [])
    for case in cases:
        case.setdefault("kind", "positive")
        src = case.get("expected_version_from")
        if src and src != "VERSION":
            raise SystemExit(f"{case['id']}: expected_version_from поддерживает только VERSION")
        for field in ("must_include", "must_not_include"):
            items = case.get(field, [])
            for item in items:
                if not isinstance(item, str):
                    raise SystemExit(
                        f"{case['id']}.{field}: ожидается строка, получено {type(item).__name__}. "
                        "Частая причина — двоеточие внутри plain scalar в YAML."
                    )
            case[field] = [item.replace("{{VERSION}}", version) for item in items]
    return doc, cases


def select(cases: list[dict], args) -> list[dict]:
    picked = cases
    if args.case:
        wanted = set(args.case)
        picked = [c for c in picked if c["id"] in wanted]
        missing = wanted - {c["id"] for c in picked}
        if missing:
            raise SystemExit(f"Неизвестные case id: {', '.join(sorted(missing))}")
    if args.kind:
        picked = [c for c in picked if c["kind"] in args.kind]
    if args.limit:
        picked = picked[: args.limit]
    return picked


def run_cli(argv: list[str], timeout: int) -> dict:
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)  # иначе вложенный запуск блокируется
    proc = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout, env=env, cwd=str(REPO)
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        detail = proc.stderr.strip() or proc.stdout.strip()
        return {"ok": False, "error": (detail or f"exit {proc.returncode}")[:2000]}
    # CLI отдаёт exit 0 и на прикладных ошибках — проверять is_error, а не код возврата.
    if payload.get("is_error"):
        return {"ok": False, "error": str(payload.get("result", "CLI вернул is_error"))[:2000]}
    if proc.returncode != 0:
        return {"ok": False, "error": f"exit {proc.returncode}: {str(payload.get('result',''))[:500]}"}
    return {"ok": True, "payload": payload}


def answer_case(case: dict, args) -> dict:
    argv = [
        args.cli, "-p", case["prompt"],
        "--output-format", "json",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--disallowed-tools", ANSWER_DISALLOWED,
    ]
    if args.model:
        argv += ["--model", args.model]
    if args.max_budget_usd:
        argv += ["--max-budget-usd", str(args.max_budget_usd)]
    return run_cli(argv, args.timeout)


def judge_case(case: dict, answer_text: str, args) -> dict:
    include = case.get("must_include", [])
    exclude = case.get("must_not_include", [])
    prompt = json.dumps(
        {
            "case_id": case["id"],
            "kind": case["kind"],
            "user_prompt": case["prompt"],
            "expected_phase": case.get("expected_phase"),
            "expected_mode": case.get("expected_mode"),
            "expected_risk": case.get("expected_risk"),
            "expected_engagement": case.get("expected_engagement"),
            "must_include": {i: t for i, t in enumerate(include)},
            "must_not_include": {i: t for i, t in enumerate(exclude)},
            "agent_answer": answer_text,
        },
        ensure_ascii=False,
    )
    argv = [
        args.cli, "-p", prompt,
        "--output-format", "json",
        "--json-schema", json.dumps(JUDGE_SCHEMA, ensure_ascii=False),
        "--system-prompt", JUDGE_SYSTEM,
        "--tools", "",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--strict-mcp-config",
    ]
    if args.judge_model:
        argv += ["--model", args.judge_model]
    return run_cli(argv, args.timeout)


def extract_text(payload: dict) -> str:
    for key in ("result", "text", "content"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return json.dumps(payload, ensure_ascii=False)[:20000]


def extract_json(payload: dict) -> dict | None:
    text = extract_text(payload)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def write_report(run_dir: Path, meta: dict, results: list[dict]) -> Path:
    lines = [
        f"# Forward-test run: {meta['run_id']}",
        "",
        f"Skill VERSION / commit: {meta['skill_version']} / {meta['skill_commit']}",
        f"Answer model / judge model: {meta['model']} / {meta['judge_model']}",
        f"Corpus cases: {meta['selected']} из {meta['total']}",
        f"Environment / date: {meta['host']} / {meta['started']}",
        "",
        "Judge verdict является advisory evidence. Release verdict подтверждает человек.",
        "",
    ]
    for res in results:
        lines += [f"## Case {res['case_id']} ({res['kind']})", ""]
        if res.get("error"):
            lines += [f"Infrastructure error: {res['error']}", ""]
            continue
        j = res["judge"]
        lines += [
            f"Observed phase/mode/risk: {j.get('observed_phase', '?')} / "
            f"{j.get('observed_mode', '?')} / {j.get('observed_risk', '?')}",
            f"Expected: {res.get('expected_phase', '-')} / {res.get('expected_mode', '-')} / "
            f"{res.get('expected_risk', '-')}",
            "",
            "Must include:",
        ]
        for item in j.get("must_include", []):
            lines.append(f"- [{item['verdict']}] {item['evidence']}")
        lines += ["", "Must not include:"]
        for item in j.get("must_not_include", []):
            lines.append(f"- [{item['verdict']}] {item['evidence']}")
        rubric = j.get("rubric", {})
        lines += [
            "",
            "Rubric: " + ", ".join(f"{k}={v}" for k, v in rubric.items()),
            f"Blocking verdict: {j.get('blocking_verdict')}",
            f"Rationale: {j.get('rationale', '')}",
            f"Minimal correction: {j.get('minimal_correction', '-')}",
            "",
        ]
    blocked = [r["case_id"] for r in results if r.get("judge", {}).get("blocking_verdict") == "BLOCKED"]
    errored = [r["case_id"] for r in results if r.get("error")]
    lines += [
        "## Run verdict",
        "",
        f"Blocked cases: {', '.join(blocked) if blocked else 'нет'}",
        f"Infrastructure errors: {', '.join(errored) if errored else 'нет'}",
        f"Judge advisory: {'BLOCKED' if blocked or errored else 'PASS'}",
        "Reviewer confirmation: PENDING",
        "",
    ]
    path = run_dir / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Прогон forward-корпуса Vibecoding Bible")
    parser.add_argument("--case", action="append", help="id кейса; можно повторять")
    parser.add_argument("--kind", action="append", choices=["positive", "negative", "boundary"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--list", action="store_true", help="показать кейсы и выйти")
    parser.add_argument("--execute", action="store_true", help="реально запускать агентов")
    parser.add_argument("--cli", default="claude")
    parser.add_argument("--model")
    parser.add_argument("--judge-model")
    parser.add_argument("--max-budget-usd", type=float)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    version = read_version()
    doc, cases = load_corpus(version)
    picked = select(cases, args)

    if args.list or not picked:
        for case in picked or cases:
            print(f"{case['kind']:<9} {case['id']:<42} {case.get('expected_phase', '-')}")
        print(f"\nВсего: {len(picked or cases)} (корпус: {len(cases)}), skill VERSION {version}")
        return 0

    if not args.execute:
        print("Dry-run. Будут запущены свежие сессии для кейсов:\n")
        for case in picked:
            print(f"  {case['kind']:<9} {case['id']}")
        print(
            f"\n{len(picked)} × 2 вызова агента (ответ + judge). "
            "Добавьте --execute для реального прогона."
        )
        return 0

    started = _dt.datetime.now().astimezone()
    run_id = started.strftime("%Y-%m-%dT%H-%M-%S")
    run_dir = RECEIPTS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id,
        "started": started.isoformat(timespec="seconds"),
        "skill_version": version,
        "skill_commit": git_commit(),
        "corpus_version": doc.get("version"),
        "model": args.model or "session default",
        "judge_model": args.judge_model or args.model or "session default",
        "host": sys.platform,
        "selected": len(picked),
        "total": len(cases),
        "answer_disallowed_tools": ANSWER_DISALLOWED,
    }

    results: list[dict] = []
    for index, case in enumerate(picked, 1):
        print(f"[{index}/{len(picked)}] {case['id']} … ", end="", flush=True)
        record = {
            "case_id": case["id"],
            "kind": case["kind"],
            "expected_phase": case.get("expected_phase"),
            "expected_mode": case.get("expected_mode"),
            "expected_risk": case.get("expected_risk"),
        }
        answer = answer_case(case, args)
        if not answer["ok"]:
            record["error"] = f"answer: {answer['error']}"
            print("ошибка ответа")
        else:
            answer_text = extract_text(answer["payload"])
            record["answer"] = answer_text
            verdict = judge_case(case, answer_text, args)
            if not verdict["ok"]:
                record["error"] = f"judge: {verdict['error']}"
                print("ошибка judge")
            else:
                parsed = extract_json(verdict["payload"])
                if parsed is None:
                    record["error"] = "judge вернул неразбираемый ответ"
                    print("ошибка judge")
                else:
                    record["judge"] = parsed
                    print(parsed.get("blocking_verdict", "?"))
        results.append(record)
        (run_dir / f"{case['id']}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    (run_dir / "run.json").write_text(
        json.dumps({"meta": meta, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = write_report(run_dir, meta, results)
    print(f"\nReceipts: {run_dir}\nОтчёт: {report}")

    blocked = any(r.get("judge", {}).get("blocking_verdict") == "BLOCKED" for r in results)
    errored = any(r.get("error") for r in results)
    if errored:
        return 2
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
