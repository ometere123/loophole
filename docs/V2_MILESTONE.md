# LOOPHOLE V2 — Policy Repair & Revalidation

Status: **implemented as a source-verified release candidate; not deployed**.

V2 preserves the deployed V1 contract and its economic history. `contracts/Loophole.py` remains the active Studionet 61999 contract at `0xB87353201CeC791cc16c25e8eE1077076D90548E`, with source SHA-256 `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`. V2 is a separate self-contained source at `contracts/LoopholeV2.py`; it has no migration path, no access to V1 custody and no configured production address until an explicit deployment approval is given.

## What V2 adds

After a finalized `VALID` attempt, the original organizer can append a bounded policy revision. Each revision records its parent version, original challenge and winning attempt, frozen evidence commitment, policy goal, rule text, limitations, source metadata and content commitment. Historical versions are never overwritten. At most eight versions are allowed for one challenge, and only one repair proposal can be active at a time.

The repair lifecycle is:

`PROPOSED → REVIEWING → VERIFIED_FIX | NOT_VERIFIED | INCONCLUSIVE`

`start_repair_review` freezes the complete original and proposed evidence and a review-round snapshot hash. `adjudicate_repair` independently assesses the frozen snapshot with GenLayer consensus. Only `VERIFIED_FIX` changes the authoritative policy version. A timeout becomes `INCONCLUSIVE` and leaves the previous authoritative version in force.

`create_rechallenge` copies only a verified policy version into a new, separately funded challenge. The new challenge has its own bounty, bond, attempts and settlement accounting. Original winner credit and all prior verdicts remain untouched.

## Repair assessment

Validators independently produce three tri-state findings:

1. `closure`: the correction blocks the exact previously validated loophole;
2. `goal`: the correction preserves the original policy goal;
3. `coherence`: the corrected policy is internally consistent and feasible from authenticated evidence.

The contract derives the outcome mechanically: three `PROVEN` findings produce `VERIFIED_FIX`; any `DISPROVEN` finding produces `NOT_VERIFIED`; all other cases produce `INCONCLUSIVE`. Leader and validator results must agree on the derived outcome, all three material findings and the source-evidence state. Explanatory prose is stored for inspection but is not an equivalence key. Malformed, contradictory, unavailable or unauthenticated evidence fails closed.

## Public inspection and SDK

The optional `/v2` frontend route provides a shareable challenge-ID audit view, policy lineage, repair rounds, findings, source preflight and machine-readable JSON export. It stays visibly unavailable while `NEXT_PUBLIC_LOOPHOLE_V2_ADDRESS` is empty. Writes use the same injected EIP-1193 wallet path as V1 and are hard-gated to Studionet 61999.

The repository-local SDK is in `sdk/`. It provides V2 read/call construction, finalized-execution polling, explorer links and exact pinned GitHub-byte retrieval. The reproducible public-source example is `examples/v2-github-policy.mjs`.

## Verification boundary

The following are implemented and locally verified:

- Python compilation, runner-header validation and V2 source-integrity checks;
- GenVM lint/schema validation against the pinned `v0.3.0-rc7` Direct Mode stack;
- V2 Direct Mode tests for valid, rejected, inconclusive, malformed, source-mismatch, replay, authorization, bounded-history, re-challenge and stalled-repair behavior;
- the existing V1 simulator, mutation and Direct Mode regression suites;
- SDK tests, frontend typecheck, production build, and desktop/mobile Playwright wallet-state checks.

No V2 deployment, funded challenge, repair consensus or V2 native GEN delivery is claimed in this document. Those require a source-hash review and explicit approval for the exact irreversible transactions. The current V1 live evidence remains the only live economic evidence and is linked from the root README.
