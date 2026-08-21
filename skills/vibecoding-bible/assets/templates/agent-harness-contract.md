# AgentHarnessContract: <name> v<version>

## Purpose and scope

Users/outcome:
Why external harness is needed:
Included workflows/hosts/projects:
Excluded/non-goals:
Risk mode/owners:

## Portable architecture

Harness Core responsibility:
Session/Event Store:
Evidence Store:
Approval Channel:
HostAdapter boundary/capabilities:
ProjectAdapter boundary/permissions:
Optional UI:

## WorkflowDefinition

ID/version/input schema/required capabilities:
Initial/terminal states:
WorkflowPack artifacts/migrations:

| Stage | Objective | Allowed actions | Required evidence | Outcomes | Approval | Budget/stop |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

## Session and identity

Session state/revision:
Subject/config/environment fingerprint:
Host/project binding:
Stale and invalidation rules:

## Evidence and decisions

Receipt types/producers/trust:
Expectation policy per stage / committed-before-action proof:
Artifact/log storage and redaction:
Human identity/decision binding:
Self-attestation policy:

## Runtime and recovery

Start/bind/rebind/resume:
Idempotency/concurrency/event IDs:
Crash/reconciliation/replay:
Cancel/rollback/compensation:
Manual fallback:

## Security and budgets

Least privilege/secrets/privacy:
Attempts/deadline/token/cost caps:
Audit/retention/deletion:

## Conformance

Wrong stage/stale revision/subject drift:
Missing receipt/self-approval/spoofed decision:
Duplicate mutation/crash/recovery:
Unsupported capability/new workflow without core change:
Fault injection/qualification:

## Delivery

First Red:
Minimal vertical slice:
Required evidence:
Known constraints:
Implementation verdict:
Release verdict:
