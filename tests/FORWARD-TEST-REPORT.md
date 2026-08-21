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

## Release Train regression — 2026-08-19

A fresh agent received the candidate skill and a user request about repeated hour-long release cycles for minor bugs; it did not receive tests, expected properties, development history, or reviewer conclusions. It separated per-fix Red/targeted verification/preview from release-grade candidate evidence, accumulated compatible fixes as `READY_FOR_BATCH` on a clean cumulative head, required a project-owned trigger and maximum wait, froze one batch manifest and immutable candidate, selected blocking plus `always_on` Registry checks by aggregate impact, and performed one candidate QA/ACCEPT/deploy/readback/rollback cycle. It preserved an urgent hotfix lane without weakening exact-candidate gates. Verdict: passed.

## Release Composition Gate regression — 2026-08-20

A fresh agent received candidate `1.2.0` and a release regression where an accepted Workflow Hub handoff remained on a sibling history while the selected release head, shallow file gate, QA sample, and installation controller all passed. It did not receive tests, expected properties, prior conclusions, memories, or Git history. The agent correctly separated head correctness from release-intent completeness, introduced a versioned accepted-handoff manifest with blocking `MISSING`, required ancestry or explicit equivalent mapping, behavioral capability proof on the exact candidate, manifest-derived QA coverage, and candidate binding to the composition receipt. It preserved impact-based Registry selection and correctly left the installation controller unchanged. Verdict: passed.

## Portable Agent Execution Harness — 2026-08-21

Two fresh agents received candidate `1.2.0`, one natural prompt each, and no tests, expected properties, development history or prior conclusions.

- `design_portable_proprietary_agent_harness` passed: the response separated a deterministic core, data-defined WorkflowPacks, HostAdapter, ProjectAdapter, evidence store and authenticated approval channel; kept durable state outside chat; defined stage/revision/subject semantics; and covered wrong-stage, stale-revision, self-approval, missing-receipt, subject-drift and duplicate-mutation faults.
- `use_existing_agent_execution_harness` initially needed a targeted repair: the response correctly kept the existing harness authoritative, bound work/evidence to the current stage and exact subject, separated reports/receipts/approvals and avoided a parallel chat state machine, but did not explicitly state the bounded manual fallback for a short low-risk task when the harness is unavailable. The entrypoint was tightened at the minimal general layer and rerun fresh. The rerun explicitly separated a bounded manual process for short reversible low-risk work from mandatory stop-and-restore behavior for durable or consequential work, while preserving TDD, evidence, security, release-composition and rollback policy above the harness.

Verdict: passed after targeted repair and fresh rerun.
