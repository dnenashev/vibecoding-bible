# Forward-test report: universal lifecycle candidate

Date: 2026-08-04
Candidate: working tree based on `135a936`
Runtime: fresh Codex subagent session per case; exact provider/model identifier was not exposed
Reviewer: integration orchestrator

## Method

- Each run received the candidate skill and one natural user request.
- Agents were told not to inspect `tests/` or `docs/AUDIT-AND-ROADMAP.md`.
- No run inherited the development conversation or another case.
- Review used behavioral properties from `forward-cases.yaml`, not exact wording.
- Failed patterns were fixed in the smallest general rule and rerun fresh.

## Distinct scenarios

| Scenario | Phase/mode | Result |
|---|---|---|
| Idea without repository | UNDERSTAND / EXPLORE | Passed after rerun |
| Multi-tenant invoice SaaS | DESIGN / BUILD | Passed |
| Production payment integration | DESIGN / CRITICAL | Passed after rerun |
| Responsive shadcn dashboard | DESIGN / BUILD | Passed with honest repository blocker |
| Offline mobile/desktop notes | DESIGN / BUILD | Passed after rerun |
| Post-launch AI summary review | LEARN / BUILD | Passed |
| First AI workflow calibration | VERIFY / inherited subject risk | Passed after rerun |
| Duplicate-charge incident | SHIP / CRITICAL | Passed |
| PII-sensitive AI spike | UNDERSTAND / EXPLORE | Passed after rerun |
| Medical-document release audit | SHIP / CRITICAL | Passed |
| Duplicate submission with dirty worktree | BUILD / BUILD | Passed with honest repository blocker |
| Desktop GUI bug through exact-candidate release | BUILD / BUILD | Passed after rerun |
| Required Test Registry across code and AI workflows | VERIFY / BUILD | Passed after rerun |
| Canonical skill version identity | VERIFY / BUILD | Passed |

Coverage: 14 distinct requests, all lifecycle phases, and all three risk modes.

## Gaps found and corrections

1. A missing repository could make the whole conversation sound `BLOCKED`. The entrypoint now limits `BLOCKED` to the exact implementation/release gate and still gives a bounded, unverified draft.
2. A high-risk integration blocker initially omitted useful safety boundaries. The entrypoint now requires mandatory boundaries, unknowns, and one continuation path without inventing vendor details.
3. A design response could freeze a cross-platform stack before real constraints. DESIGN now requires platform/team/runtime/deployment constraints or an explicitly provisional hypothesis.
4. An EXPLORE response invented a convenient sample count. Product discovery now uses time/cost boxes and adaptive stopping when baseline and variance are unknown.
5. The first TestingHarness run was treated as `EXPLORE` merely because it was new. Harness mode now inherits the subject's intended use and risk.

## Blocking review

- No tested response fabricated repository inspection, credentials, vendor API, runtime evidence, or successful mutation.
- No tested response treated mocks, unit tests, or self-attested pass as release evidence.
- CRITICAL cases preserved payment, PII, medical-data, tenant, approval, readback, and recovery boundaries.
- Responses ended with one actionable next step or one honest blocker.
- No agent edited project files or performed external mutations during forward tests.

## Release verdict

`READY`. Structural validation, publication, and installed-source parity were completed for the lifecycle release.

## Replay-policy regression — 2026-08-04

A fresh agent received a five-stage expensive workflow with a repaired fourth checkpoint. It correctly reused version-matched upstream evidence, replayed from checkpoint 3 through the terminal outcome, required readback for side effects, and reserved full clean replay only for explicit stale-state or cross-stage risk. Verdict: passed.

## Bug-repair regression — 2026-08-18

A fresh agent received a desktop visual defect, parallel changes in main, required user QA, and a protected system installation target. The first run preserved the exact-candidate release chain but omitted the explicit Primary Red while blocked on a missing repository. The minimal contract was tightened and rerun fresh. The rerun correctly produced repair isolation, Primary Red, affected-path verification after cumulative integration, immutable candidate identity, candidate-bound QA and ACCEPT, installation readback, and rollback. Verdict: passed.

## Regression Registry — 2026-08-18

A fresh agent received a repository with scattered tests, forgotten regressions, and wasteful full-suite runs. The first run correctly designed native-test references, impact selection, lifecycle states, and separate candidate evidence but omitted the aggregate entries for AI suites and workflow packs. Their universal mapping was made explicit and rerun fresh. The rerun kept executable tests in native locations, represented EvalSuite and TestingHarness packs as single entries, selected active gates by impact, preserved Primary Red admission, required exact-candidate evidence, and treated quarantine as unresolved rather than pass. Verdict: passed.

## Version identity — 2026-08-18

A fresh agent was asked to resolve the conflict between an unversioned skill and nested `version: 1` fields. It read the canonical `VERSION`, answered `1.0.0`, identified the nested value as a Registry-format version, and treated commit/tag only as supporting release identity. It also correctly reported that the candidate was not yet published before the release commit and tag. Verdict: passed.
