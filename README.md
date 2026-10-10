# LOOPHOLE! · Break the rules before the rules break you

A playful, two-contract GenLayer community-policy loophole bounty protocol on **Studionet 61999**.

The **RuleVault** contract escrows challenge prizes and challenger bonds, holds immutable rulebooks, serializes case review, authenticates callbacks, records adjudicated entitlements and emits GEN withdrawals. **GapJudge** independently judges three substantive factors (literal compliance, purpose conflict, feasibility) with GenLayer validator consensus and returns its result via a *finalized* internal message. Its policy input is frozen in RuleVault; no server, hosted AI endpoint, administrator or frontend local state decides eligibility.

## Quick start

Requirements: Node 22+, Python 3.12+, an injected EIP-1193 wallet, local GenLayer CLI wallet configured/funded on Studionet. The CLI is **repository-local `genlayer@0.39.1`**, never a global or `npx` latest installation. No WalletConnect, Snaps, Docker requirement or signing backend.

```bash
npm install
npm --prefix frontend install
python -m pip install -r requirements.txt
python scripts/preflight.py
python -m pytest -q tests/
genvm-lint check contracts/RuleVault.py
genvm-lint check contracts/GapJudge.py
./node_modules/.bin/genlayer network set studionet
python deploy/deploy_studionet.py                    # verifies network, active wallet; dry run
python deploy/deploy_studionet.py --execute --confirm-chain 61999
cp frontend/.env.example frontend/.env.local         # fill the two addresses printed after deploy
npm --prefix frontend run dev
```

The verified Studionet deployment and public frontend are recorded in `deployments.studionet.json`. Economic lifecycle testing still requires funded organizer and challenger transactions because the CLI write path does not expose payable values.

## End-to-end action sequence

1. Deploy GapJudge and RuleVault through the active CLI wallet; bind judge once to vault using `bind_vault`.
2. Organizer funds `create_challenge` with a GEN value (0.01–1,000,000 GEN), exact purpose/rule/limitations, challenge duration 1–30 days and a GEN bond (0.0001–1000 GEN).
3. Challenger uses browser wallet to `commit_attempt` with an exact bond and lowercase SHA-256 commitment. A secret backup is saved locally; **export it**, because losing the salt makes the bond forfeitable.
4. Before the deadline, challenger reveals the matching `salt`, `scenario`, `rule_quote` and `impact` with `reveal_attempt`.
5. Anyone calls `start_review`. Vault sends finalized message to GapJudge. GapJudge compares a leader's verdict against an **independently derived** validator verdict, requiring agreement on verdict and all three material findings.
6. GapJudge emits a finalized authenticated `record_verdict` callback. The vault credits prize + bond to first adjudicated VALID challenger, places the first INVALID result into a neutral appeal window, and returns INCONCLUSIVE bond to challenger.
7. After expiry +48 hours, if no active review, `refund_unwon` credits organizer's unused bounty. `recover_stalled_review` releases a stalled review after 5 days and fences stale callbacks. `settle_remaining_bond` handles unopened commitments and unreviewed attempts after closure.
8. `withdraw` emits a finalization-gated external GEN transfer. **This is asynchronous, not a synchronous confirmed payout**. Verify the child's actual execution and destination balance; failed child transfers are not automatically refunded on current GenLayer.

## Local state versus chain state

Real reads use `get_config`, `get_challenge`, `get_attempt`, `get_credit`, `get_withdrawal` from RuleVault. Each write obtains an injected EIP-1193 signature and tracks accepted versus finalized receipt **plus execution result**. On-chain async follow-up steps are shown separately; a transaction finalizing doesn't mean a child payout is confirmed. Challenge cards never come from a local mock seed. Local storage contains only *your own commitment recovery material*, not authoritative adjudications.

## Controls and bounds

- Challenge durations 1–30 days; 12 active attempt slots, 64 total attempt records, and 2 outstanding attempts per wallet; organizer barred from direct self-challenges.
- Immutable rule, intent and exceptions; policy body up to 3,000 characters, objective up to 1,200; no external claims/source pages.
- Commit/reveal is bound to *challenge ID, wallet address, salt, scenario, quote and impact*, concatenated with `|`, then SHA-256 hex. No client-side verdict.
- FIFO among revealed attempts, one review active at a time; finalized, authenticated callbacks; idempotent judge cases; round fencing for stale callbacks.
- The first INVALID verdict enters a 24-hour appeal window; anyone may finalize it after that window, while the challenger may appeal with an equal bond. INCONCLUSIVE refunds the applicable bond; absence of a reveal credits the organizer after expiry. A winner receives bounty and own bond. Revealed unreviewed cases get bonds back after win/refund.
- Reveals remain open for 48 hours after challenge end. Active review can take 5+ days to recover, during which refund is blocked.
- Native GEN amount accounting is in `u256` wei. Prize and bonds are liabilities until credited/withdrawn.

## Limits and known operational risks

This package is not an audited system. Model verdict agreement is not a mathematical correctness proof; adversarial policy cases may legitimately be inconclusive or conflict. Studionet GEN is test currency. Withdrawals intentionally report `TRANSFER_EMITTED_UNVERIFIED` because GenLayer external message failure does not credit value back.

## Scripts and audits

- `python scripts/preflight.py` — verifies source structure, GenVM pins, CLI pin, wallet and required write methods.
- `pytest -q tests/` — offline deterministic state-machine tests using a deliberately small GenLayer simulator (not Direct Mode).
- `genvm-lint check contracts/*.py` — actual SDK semantic lint once installed.
- `python deploy/deploy_studionet.py` — guarded, repo-local CLI two-contract installer; requires FINALIZED successful execution and verifies reciprocal binding before writing the local manifest.
- GitHub Actions — source checks, GenVM lint, Python state-machine tests, TypeScript check and frontend build.

Additional design details are in `docs/SECURITY.md`, `docs/CONSENSUS.md`, and `docs/QA.md` (these are product documentation, not a handoff).

## GenLayer references

- https://docs.genlayer.com/developers/intelligent-contracts/features/messages
- https://docs.genlayer.com/developers/intelligent-contracts/features/value-transfers
- https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- https://docs.genlayer.com/developers/intelligent-contracts/features/transaction-context
- https://docs.genlayer.com/api-references/genlayer-cli
- https://www.npmjs.com/package/genlayer-js

License: MIT. No copied Jestor branding, assets, designs or components.
