# Economic security and failure handling

The deployable release is one Intelligent Contract, `Loophole.py`. It stores the immutable policy, GEN escrow, commit/reveal records, review queue, adjudication result and withdrawal accounting together. The previous RuleVault/GapJudge pair and its Studionet funds remain historical deployments; they are not migrated by this release.

| Invariant | Enforcement | Remaining boundary |
|---|---|---|
| Funded text cannot be rewritten | no edit method; review uses a frozen snapshot and evidence hash | finality and network rollback are external concerns |
| Organizer cannot submit an attempt | organizer address is rejected | Sybil identities are not solved |
| A reveal must match its commitment | SHA-256 binds challenge, sender, salt and all revealed fields through a length-prefixed UTF-8 encoding | a leaked local backup can reveal the secret |
| Reviews are bounded and ordered | one active review, FIFO eligible selection, reveal grace and 12 active/64 lifetime bounds | Sybil wallets can consume bounded capacity |
| Stale or replayed adjudication cannot settle | current active attempt, round and evidence hash are required; case keys are idempotent | delayed network processing remains visible as pending |
| No duplicate prize or bond credit | terminal challenge state, one decision record and exact credit accounting | live external execution still needs verification |
| Appeals have one bounded opportunity | only an affected challenger may appeal one `INVALID` result within the window | timeout recovery remains permissionless after five days |
| No unauthorized withdrawal | withdrawal requires positive caller credit, clears it before emitting, and records provenance | native GEN delivery is asynchronous |

The contract never restores credit because a transfer appears delayed and never retries automatically. Withdrawal records retain `TRANSFER_EMITTED_UNVERIFIED`. The read-only verifier and frontend distinguish `CLAIMABLE`, `TRANSFER SUBMITTED`, `PARENT FINALIZED`, `DELIVERY VERIFIED`, `FAILED` and `UNRESOLVED`. Delivery is verified only with an exact beneficiary and amount, finalized successful child execution, and authoritative `value_credited` evidence where the RPC exposes it.

The five-day stalled-review recovery path preserves the active attempt's bond and returns the review to an inconclusive terminal state. It is not available before the timeout and does not manufacture a verdict or prize.

The complete funded lifecycle and recipient-credit proof remain a live-network acceptance condition. Existing historical failed adjudications remain recorded in `docs/evidence/`; they are not converted into production success claims.
