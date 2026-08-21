# Release Checklist: <scope>

Candidate/environment:
Owner:
Verdict: READY | READY_WITH_CONSTRAINTS | BLOCKED

## Release intent

Manifest/version:
Accepted handoff IDs:
Explicit deferred/superseded decisions:
Composition receipt:

- [ ] Every intended handoff is integrated, explicitly deferred, or superseded
- [ ] No intended handoff remains MISSING
- [ ] Provenance/reachability or equivalent mapping is verified
- [ ] Accepted capabilities have behavioral evidence on the exact candidate
- [ ] QA coverage is derived from release acceptance criteria

## Exact candidate

- [ ] Source/artifact/config/schema versions frozen
- [ ] Batch manifest and cumulative source scope frozen, if applicable
- [ ] Candidate identity binds the release intent and composition receipt
- [ ] Release scope and limitations explicit

## Evidence

- [ ] Required static/test/build commands pass
- [ ] Aggregate impact recalculated for the final cumulative candidate
- [ ] Applicable blocking Registry entries have fresh evidence
- [ ] Mandatory integrations verified
- [ ] Critical journey passes on required environment
- [ ] Security/performance/accessibility checks pass by risk
- [ ] No blocking skip/todo/unverified criterion

## Delivery

- [ ] Migration/backfill preflight complete
- [ ] Feature flag/canary/blast-radius control ready
- [ ] Deploy procedure reproducible
- [ ] Readback signals defined
- [ ] Rollback/compensation verified
- [ ] Monitoring and incident owner ready

## Decision

Evidence refs:
Constraints/expiry:
Approve/block reason:
OutcomeRecord window/owner:
