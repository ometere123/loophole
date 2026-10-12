# LOOPHOLE! · Break the rules before the rules break you

LOOPHOLE! is a single-contract GenLayer protocol on Studionet 61999. A rulebook organizer escrows a GEN bounty, challengers commit and reveal evidence, and anyone can run a direct validator adjudication against the frozen evidence. A finalized result settles the economic state atomically in the same contract.

The current repository contains the new deployable contract at `contracts/Loophole.py`. The earlier `RuleVault` and `GapJudge` sources are kept under `contracts/historical/` solely to preserve source correspondence and evidence for the existing Studionet deployments. The historical contracts and their funds are not migrated or modified by the monolith release.

## Environment

- Studionet chain `61999` (`0xF22F`)
- RPC `https://studio.genlayer.com/api`
- Repository-local GenLayer CLI `0.39.1`
- Frontend SDK `genlayer-js@1.1.8`
- Injected EIP-1193 wallet only
- No Snaps, WalletConnect, hosted signer or privileged payout backend

## Local verification

```bash
npm ci
npm --prefix frontend ci
python -m pip install -r requirements.txt
python scripts/preflight.py
python -m pytest tests -m "not direct" -q
genvm-lint check contracts/Loophole.py
python scripts/validate_runner_headers.py
python scripts/verify_prompt_parity.py
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

The Direct Mode suite is separate from the simulator suite:

```bash
GENVM_VERSION=v0.3.0-rc7 python -m pytest tests/direct -m direct -q
```

The CI workflow validates the production source, historical source fixtures, diagnostics, mutation behavior, genuine Direct Mode and the frontend lockfile build.

## Protocol flow

1. An organizer publishes an immutable title, goal, rule, limitations, duration, bounty and exact challenger bond through `create_challenge`.
2. A challenger commits a lowercase SHA-256 hash of the challenge ID, wallet address, salt, scenario, exact rule quote and impact. The fields use a length-prefixed UTF-8 encoding, so delimiters and Unicode cannot create ambiguous preimages. The client saves a local backup and offers JSON export; the contract stores only the commitment.
3. The challenger reveals the original fields through `reveal_attempt`. The contract checks the exact commitment and requires the quoted passage to occur in the frozen policy.
4. Anyone calls `start_review`. The contract serializes the FIFO queue, freezes the active attempt and increments the review round.
5. Anyone calls `adjudicate_review`. The method reads the frozen state from the same contract, runs independent GenLayer validator assessment, derives the verdict from three tri-state material findings, records the result and settles the applicable liability atomically.
6. `VALID` credits the challenger with bounty plus bond. The first `INVALID` result enters a bounded appeal window. An appeal requires an equal bond and creates a new review round. `INCONCLUSIVE` returns the affected bond without releasing the bounty.
7. Unrevealed commitments expire after the reveal grace period. Stalled direct reviews can be recovered after five days. Organizer refund remains blocked while any legitimate challenger right is unresolved.
8. `withdraw` clears the recipient's claimable credit before emitting the native GEN transfer. The record remains `TRANSFER_EMITTED_UNVERIFIED`; the frontend and `scripts/verify_delivery.mjs` reconcile the external child independently.

## Consensus rubric

Validators independently assess:

- `letter`: whether every described step satisfies the exact written rule;
- `purpose`: whether the documented outcome materially defeats the explicit goal;
- `feasible`: whether the frozen text supplies an internally possible sequence without invented prerequisites.

Each finding is `PROVEN`, `DISPROVEN` or `UNKNOWN`. The contract derives `VALID` only when all three are `PROVEN`, `INVALID` when any one is `DISPROVEN`, and `INCONCLUSIVE` otherwise. Validators must agree on the three material findings and derived verdict; explanatory wording may differ. This keeps semantic checks substantive while avoiding brittle comparison of prose.

## Historical deployments

The original two-contract deployment remains authoritative for its existing funded challenges and is preserved as historical evidence:

- GapJudge: `0xb14B08cd35Fa64FE795e14931DdA09999627785d`
- RuleVault: `0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26`

The current source-verified monolith is deployed at [`0xec98AFC80bda4b664F20d782aA8a0bd49e436233`](https://explorer-studio.genlayer.com/address/0xec98AFC80bda4b664F20d782aA8a0bd49e436233). Its finalized zero-value deployment transaction is [`0xc5a5dee6cbbb2f081a37adefcb060061abe306044a46c17c2587f18577bda2d1`](https://explorer-studio.genlayer.com/tx/0xc5a5dee6cbbb2f081a37adefcb060061abe306044a46c17c2587f18577bda2d1), with exact source and schema evidence in [`docs/LOOPHOLE_CURRENT_DEPLOYMENT_2026-10-12.md`](docs/LOOPHOLE_CURRENT_DEPLOYMENT_2026-10-12.md). The previous source-verified monolith at [`0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`](https://explorer-studio.genlayer.com/address/0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e), the earlier monolith at [`0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf`](https://explorer-studio.genlayer.com/address/0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf), and their evidence remain historical. No historical escrow is migrated automatically.

The previous monolith's complete funded challenge, adjudication, entitlement and native GEN withdrawal remains recorded in [`docs/LOOPHOLE_CORRECTED_LIVE_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CORRECTED_LIVE_LIFECYCLE_2026-10-12.md), including the independently verified external transfer child. The current deployment's complete two-wallet funded lifecycle is recorded in [`docs/LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md) and its machine-readable evidence in [`docs/evidence/loophole-current-funded-lifecycle-2026-10-12.json`](docs/evidence/loophole-current-funded-lifecycle-2026-10-12.json). The current deployment's independently verified negative adjudication is recorded in [`docs/LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md), with machine-readable evidence in [`docs/evidence/loophole-current-invalid-lifecycle-2026-10-12.json`](docs/evidence/loophole-current-invalid-lifecycle-2026-10-12.json); its bounded appeal window remains explicit. The current deployment's real ambiguous case, `INCONCLUSIVE` settlement and returned-bond delivery are recorded in [`docs/LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md), with machine-readable evidence in [`docs/evidence/loophole-current-neutral-lifecycle-2026-10-12.json`](docs/evidence/loophole-current-neutral-lifecycle-2026-10-12.json).

## Safety bounds and delivery

Challenge durations are limited to 1–30 days, active attempts to 12, lifetime attempt records to 64, and two outstanding attempts per challenger. Native GEN amounts use `u256` atto units. No owner override can create a winner, alter a rulebook, or withdraw another recipient's credit. A failed or unresolved external child transfer never restores credit automatically and never triggers a blind retry.

The frontend reads challenges and verdicts from chain state, gates wallet writes to EIP-1193 chain 61999, distinguishes accepted from finalized execution, restores pending transaction provenance after refresh, and can recover missing withdrawal parent provenance from the read-only explorer history before showing delivery as verified. Missing, ambiguous or unavailable evidence remains unresolved with explorer links.

## Scope, Verification & Known Limitations

LOOPHOLE! rewards independently adjudicated textual or hypothetical loopholes against immutable rulebooks. GenLayer validators assess literal compliance, conflict with the stated purpose and feasibility of the described sequence. A `VALID` result means the frozen text supports those findings; it is not proof that an exploit occurred in the real world.

Appeals reassess the original frozen rulebook and attempt evidence. They do not accept additional supporting evidence or a rewritten attack, so a new theory must be submitted as a separate attempt when the challenge permits it.

GEN delivery has separate evidence states: `CLAIMABLE` is finalized on-chain credit; `TRANSFER SUBMITTED` is a withdrawal parent submitted with delivery still unverified; `PARENT FINALIZED` means the parent executed successfully but does not prove payment; `DELIVERY VERIFIED` requires an independently matched finalized child with the exact contract origin, beneficiary, amount, successful receipt and authoritative recipient-credit evidence; `FAILED` requires authoritative child failure or non-credit; and `UNRESOLVED` means safe delivery proof is unavailable. A successful withdrawal parent alone never proves that GEN reached the recipient.

The verifier is read-only. If an external transfer fails or remains ambiguous, the current protocol cannot safely recredit or retry it automatically. Credit is never restored from a timeout, a later positive balance or beneficiary acknowledgement, and the application makes no guarantee of payout recovery.

The current monolith has authentic live evidence for `VALID` with a verified bounty-plus-bond receipt ([funded lifecycle](docs/LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md)), `INVALID` with no entitlement ([invalid lifecycle](docs/LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md)), and `INCONCLUSIVE` with returned-bond delivery ([neutral lifecycle](docs/LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md)). The `VALID` and `INCONCLUSIVE` records include finalized native GEN child receipts independently matched to their beneficiaries. The invalid case remains in its documented bounded appeal window; live appeal settlement, stalled-review recovery and external-transfer failure recovery are not claimed as demonstrated.

`contracts/Loophole.py` is the sole active Intelligent Contract for LOOPHOLE! on Studionet 61999. The earlier RuleVault and GapJudge deployments remain separate historical deployments with their own source and fund records; they are not part of the active monolith or an automatic migration path.

The current public frontend is [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/), verified against the current monolith above. Its deployment and environment evidence is recorded in [`docs/FRONTEND_DEPLOYMENT_2026-10-12.md`](docs/FRONTEND_DEPLOYMENT_2026-10-12.md).

## Deployment

The guarded deployment helper performs a dry-run by default and refuses any network other than Studionet 61999 or any CLI other than the repository-local 0.39.1:

```bash
python deploy/deploy_studionet.py
python deploy/deploy_studionet.py --execute --confirm-chain 61999
```

The second command requires explicit authorization for the one GEN-spending deployment action. It deploys only `contracts/Loophole.py`, waits for finalized successful execution, verifies `get_config`, writes the local manifest and prints `NEXT_PUBLIC_LOOPHOLE_ADDRESS`.

License: MIT.
