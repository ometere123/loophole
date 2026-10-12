# Product acceptance and release matrix

| Area | Release evidence |
|---|---|
| Repository quality | exact source fingerprints, pinned repository-local CLI `0.39.1`, clean CI |
| GenVM semantics | real GenVM lint/schema validation and Direct Mode against the deployable source |
| Contract lifecycle | funded organizer, commit/reveal, FIFO review, direct adjudication, terminal settlement and pull withdrawal |
| Payment delivery | external transfer child matched to the withdrawal, finalized successfully, with authoritative recipient-credit evidence |
| Frontend | injected EIP-1193 wallet, wrong-network gate, true writes, backup/recovery, refresh persistence and explorer links |
| Adversarial coverage | forged state, stale round, duplicate adjudication, invalid reveal, premature refund, duplicate entitlement, appeal settlement and unauthorized withdrawal |
| Release | source-verified deployment manifest, synchronized branches and inspectable live evidence |

The automated contract gates are deliberately separate:

- The simulator covers state transitions, queue and accounting invariants.
- Executable mutation tests remove individual protections and demonstrate that the corresponding behavioral test then fails or exposes the unsafe result.
- Direct Mode runs the actual pinned GenVM SDK and runner with validator rechecks, including the production tri-state assessment workload.
- Frontend type checking and production build run against the committed lockfile.

None of those local checks is substituted for a live Studionet validator result. The historical two-contract transactions and diagnostic controls under `docs/evidence/` remain evidence of their actual outcomes and are not evidence that the new deployment has completed a funded economic lifecycle.
