#!/usr/bin/env python3
"""Заглушка CLI для conformance-теста самого runner.

Не является evidence поведения skill. Проверяет только, что runner корректно
собирает вызовы, различает ответ и judge, разбирает JSON и пишет receipts.
"""

import json
import sys

argv = sys.argv[1:]
is_judge = "--json-schema" in argv

if is_judge:
    payload = json.loads(argv[argv.index("-p") + 1])
    verdict = {
        "observed_phase": "n/a",
        "observed_mode": "n/a",
        "must_include": [
            {"index": i, "verdict": "observed", "evidence": "stub"}
            for i in range(len(payload.get("must_include", {})))
        ],
        "must_not_include": [
            {"index": i, "verdict": "absent", "evidence": "stub"}
            for i in range(len(payload.get("must_not_include", {})))
        ],
        "rubric": {
            "routing": "adequate", "practicality": "adequate", "evidence": "adequate",
            "risk": "adequate", "simplicity": "adequate", "next_step": "adequate",
        },
        "blocking_verdict": "PASS",
        "rationale": "conformance stub",
    }
    print(json.dumps({"type": "result", "is_error": False, "result": json.dumps(verdict, ensure_ascii=False)}, ensure_ascii=False))
else:
    print(json.dumps({"type": "result", "is_error": False, "result": "STUB ANSWER"}, ensure_ascii=False))
