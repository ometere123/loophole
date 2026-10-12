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
2. A challenger commits a lowercase SHA-256 hash of the challenge ID, wallet address, salt, scenario, exact rule quote and impact. The client saves a local backup and offers JSON export; the contract stores only the commitment.
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

The monolith deployment is recorded only after an explicitly approved, finalized zero-value deployment and exact source verification. No historical escrow is migrated automatically.

## Safety bounds and delivery

Challenge durations are limited to 1–30 days, active attempts to 12, lifetime attempt records to 64, and two outstanding attempts per challenger. Native GEN amounts use `u256` atto units. No owner override can create a winner, alter a rulebook, or withdraw another recipient's credit. A failed or unresolved external child transfer never restores credit automatically and never triggers a blind retry.

The frontend reads challenges and verdicts from chain state, gates wallet writes to EIP-1193 chain 61999, distinguishes accepted from finalized execution, restores pending transaction provenance after refresh, and shows unresolved delivery with explorer links.

## Deployment

The guarded deployment helper performs a dry-run by default and refuses any network other than Studionet 61999 or any CLI other than the repository-local 0.39.1:

```bash
python deploy/deploy_studionet.py
python deploy/deploy_studionet.py --execute --confirm-chain 61999
```

The second command requires explicit authorization for the one GEN-spending deployment action. It deploys only `contracts/Loophole.py`, waits for finalized successful execution, verifies `get_config`, writes the local manifest and prints `NEXT_PUBLIC_LOOPHOLE_ADDRESS`.

License: MIT.
