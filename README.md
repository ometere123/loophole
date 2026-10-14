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

The optional `PINNED_SOURCE` mode adds an evidence-backed path without changing the hypothetical path. An organizer pins a raw GitHub rulebook URL to a full commit, its exact UTF-8 SHA-256 digest and a version marker; a challenger supplies an equally pinned evidence snapshot. Every validator independently retrieves both sources, checks status, size, digest, version and required rulebook text, and returns `INCONCLUSIVE` without settlement when the bytes are unavailable, substituted or contradictory. This authenticates stable public bytes and binds them to the frozen review; it does not attest to real-world execution or to the identity of a repository owner.

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

The active source-verified monolith is deployed at [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E). Its finalized zero-value deployment transaction is [`0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960`](https://explorer-studio.genlayer.com/tx/0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960), with exact source and schema evidence in [`docs/LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md`](docs/LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md). Its committed source SHA-256 is `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`. The earlier monoliths at [`0xec98AFC80bda4b664F20d782aA8a0bd49e436233`](https://explorer-studio.genlayer.com/address/0xec98AFC80bda4b664F20d782aA8a0bd49e436233), [`0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`](https://explorer-studio.genlayer.com/address/0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e) and [`0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf`](https://explorer-studio.genlayer.com/address/0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf) are historical deployments; their evidence and funds are kept separate. No historical escrow is migrated automatically.

The historical `0xec98…` monolith's funded `VALID`, `INVALID` and `INCONCLUSIVE` records remain available as explicitly labeled evidence in [`docs/LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md), [`docs/LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md) and [`docs/LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md`](docs/LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md). The active deployment's earlier source-backed lifecycle is recorded in [`docs/LOOPHOLE_SOURCE_BACKED_LIFECYCLE_2026-10-13.md`](docs/LOOPHOLE_SOURCE_BACKED_LIFECYCLE_2026-10-13.md), with machine-readable evidence in [`docs/evidence/loophole-source-backed-lifecycle-2026-10-13.json`](docs/evidence/loophole-source-backed-lifecycle-2026-10-13.json): a mismatched digest failed closed as `INCONCLUSIVE`, while corrected evidence authenticated successfully and produced `INVALID_PENDING` with no entitlement. The completed active-release two-case proof is recorded in [`docs/LOOPHOLE_SOURCE_BACKED_TWO_CASE_LIFECYCLE_2026-10-14.md`](docs/LOOPHOLE_SOURCE_BACKED_TWO_CASE_LIFECYCLE_2026-10-14.md), with machine-readable evidence in [`docs/evidence/loophole-source-backed-two-case-lifecycle-2026-10-14.json`](docs/evidence/loophole-source-backed-two-case-lifecycle-2026-10-14.json): challenge 2 reached `VALID`, settled a 0.03 GEN entitlement and independently verified delivery, while challenge 3 reached `INVALID_PENDING` with no entitlement. Live appeal settlement, stalled-review recovery and external-transfer failure recovery remain unclaimed.

The latest active-release eligibility readback is preserved in [`docs/evidence/active-release-eligibility-2026-10-14.json`](docs/evidence/active-release-eligibility-2026-10-14.json). It shows the exact UTC prerequisites for the still-open appeal windows and confirms that no deadline was shortened and no live write was submitted during the readback.

The subsequent eligible sequence on the same active deployment is recorded in [`docs/LOOPHOLE_ACTIVE_RELEASE_ELIGIBLE_SEQUENCE_2026-10-14.md`](docs/LOOPHOLE_ACTIVE_RELEASE_ELIGIBLE_SEQUENCE_2026-10-14.md), with machine-readable evidence in [`docs/evidence/loophole-active-release-eligible-sequence-2026-10-14.json`](docs/evidence/loophole-active-release-eligible-sequence-2026-10-14.json). Existing challenge 1 attempt 2 was finalized as INVALID, attempt 3 was adjudicated as source-backed VALID by real consensus, wallet B received the exact 0.02 GEN entitlement, and the external child transfer was independently verified with `value_credited=true`. The contract withdrawal record remains `TRANSFER_EMITTED_UNVERIFIED`, and no appeal, timeout recovery or failed-transfer recovery is claimed here.

An offline Direct Mode regression also covers source-backed `VALID` settlement. The earlier Wallet B preparation record in [`docs/LOOPHOLE_SOURCE_BACKED_VALID_PROGRESS_2026-10-13.md`](docs/LOOPHOLE_SOURCE_BACKED_VALID_PROGRESS_2026-10-13.md) remains a historical snapshot; the active-release adjudication, entitlement, withdrawal and recipient-credit proof is in the completed two-case record linked above.

## Safety bounds and delivery

The active deployed contract currently accepts challenge durations from 1–30 days, keeps the INVALID appeal window at 24 hours, limits active attempts to 12, lifetime attempt records to 64, and allows two outstanding attempts per challenger. Native GEN amounts use `u256` atto units. No owner override can create a winner, alter a rulebook, or withdraw another recipient's credit. A failed or unresolved external child transfer never restores credit automatically and never triggers a blind retry.

A 5–15 minute challenge option cannot be enabled by the frontend alone: the deployed contract validates the duration and writes the appeal deadline on-chain. Making a short window useful for rapid appeal testing would require a reviewed source change that adds an explicit short-duration policy and a matching short appeal window, followed by a separately approved deployment. Until that occurs, the active release deliberately keeps the 1-day minimum and does not present unsupported short-duration choices as live functionality.

The frontend reads challenges and verdicts from chain state, gates wallet writes to EIP-1193 chain 61999, distinguishes accepted from finalized execution, restores pending transaction provenance after refresh, and can recover missing withdrawal parent provenance from the read-only explorer history before showing delivery as verified. Missing, ambiguous or unavailable evidence remains unresolved with explorer links.

## Scope, Verification & Known Limitations

LOOPHOLE! rewards independently adjudicated textual or hypothetical loopholes against immutable rulebooks. GenLayer validators assess literal compliance, conflict with the stated purpose and feasibility of the described sequence. A `VALID` result means the frozen text supports those findings; it is not proof that an exploit occurred in the real world.

Appeals reassess the original frozen rulebook and attempt evidence. They do not accept additional supporting evidence or a rewritten attack, so a new theory must be submitted as a separate attempt when the challenge permits it.

GEN delivery has separate evidence states: `CLAIMABLE` is finalized on-chain credit; `TRANSFER SUBMITTED` is a withdrawal parent submitted with delivery still unverified; `PARENT FINALIZED` means the parent executed successfully but does not prove payment; `DELIVERY VERIFIED` requires an independently matched finalized child with the exact contract origin, beneficiary, amount, successful receipt and authoritative recipient-credit evidence; `FAILED` requires authoritative child failure or non-credit; and `UNRESOLVED` means safe delivery proof is unavailable. A successful withdrawal parent alone never proves that GEN reached the recipient.

The verifier is read-only. If an external transfer fails or remains ambiguous, the current protocol cannot safely recredit or retry it automatically. Credit is never restored from a timeout, a later positive balance or beneficiary acknowledgement, and the application makes no guarantee of payout recovery.

The previous monolith has authentic live evidence for `VALID`, `INVALID` and `INCONCLUSIVE` outcomes in the explicitly historical records linked above. The active source-verified release now has a completed source-backed `VALID` lifecycle: challenge 2 reached `VALID`, credited the challenger with 0.03 GEN, and produced a finalized native child transfer independently verified for the exact recipient and amount. The same approved test budget also produced an active-release source-backed `INVALID_PENDING` result for challenge 3; no appeal was submitted after the 0.05 GEN attached-value ceiling was consumed. The complete transaction set, state readbacks, vote records and delivery proof are in [`docs/LOOPHOLE_SOURCE_BACKED_TWO_CASE_LIFECYCLE_2026-10-14.md`](docs/LOOPHOLE_SOURCE_BACKED_TWO_CASE_LIFECYCLE_2026-10-14.md) and its machine record. Live appeal settlement, stalled-review recovery and external-transfer failure recovery are not claimed as demonstrated. The source-verified release deployment is recorded in [the release deployment evidence](docs/LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md).

`contracts/Loophole.py` is the sole active Intelligent Contract for LOOPHOLE! on Studionet 61999 at [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E). The earlier RuleVault and GapJudge deployments remain separate historical deployments with their own source and fund records; they are not part of the active monolith or an automatic migration path.

The current public frontend is [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/), verified against the active monolith above. Its current binding evidence is recorded in [`docs/FRONTEND_DEPLOYMENT_2026-10-13.md`](docs/FRONTEND_DEPLOYMENT_2026-10-13.md); the earlier Vercel environment record is historical.

## Deployment

The guarded deployment helper performs a dry-run by default and refuses any network other than Studionet 61999 or any CLI other than the repository-local 0.39.1:

```bash
python deploy/deploy_studionet.py
python deploy/deploy_studionet.py --execute --confirm-chain 61999
```

The second command requires explicit authorization for the one GEN-spending deployment action. It deploys only `contracts/Loophole.py`, waits for finalized successful execution, verifies `get_config`, writes the local manifest and prints `NEXT_PUBLIC_LOOPHOLE_ADDRESS`.

License: MIT.
