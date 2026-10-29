# V2 security and accounting review

V2 adds policy metadata and repair review records but does not add a second custody system. Bounties, challenger bonds, credits and withdrawals retain the V1 accounting model. A repair review has no payout and cannot alter a finalized prior verdict.

| Property | V2 enforcement | Boundary |
|---|---|---|
| Historical policy immutability | append-only version records, parent version and content commitment | bounded to eight versions per challenge |
| Organizer authority | only the original organizer may propose a correction or fund a re-challenge | organizer identity is the authenticated transaction sender, not external publisher identity |
| Winning evidence binding | exact finalized `VALID` attempt, evidence hash and challenge winner are required | a textual/hypothetical winning attempt remains textual evidence |
| Repair replay safety | one active proposal, review-round and snapshot hash checks, idempotent adjudication key | delayed transactions remain pending until finality |
| Conservative verdicts | tri-state findings; malformed/source-failed evidence becomes `INCONCLUSIVE` | no claim that UNKNOWN proves safety |
| Authoritative version | only `VERIFIED_FIX` advances `authoritative_version` | rejected/inconclusive revisions remain inspectable but inactive |
| Re-challenge separation | new challenge gets separate bounty, bond, attempts and liability records | V1 balances are not migrated |
| Native GEN delivery | V2 retains V1's clear-before-emission, read-only reconciliation model | failed or ambiguous external transfers cannot safely be recredited automatically without authoritative permanent-failure proof |

Adversarial coverage includes wrong organizer, wrong challenge/attempt, stale parent, duplicate active review, stale review round, source digest substitution, missing source marker, prompt-injection text, malformed findings, incompatible material findings, goal-defeating corrections, replayed adjudication and stalled repair recovery.

The source is not deployed by this branch. A deployment must be separately approved, source-verified and tested against a fresh V2 challenge. No V2 transaction or live payout is represented as evidence here.
