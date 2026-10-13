# LOOPHOLE! final verification closeout

This closeout records the implementation and evidence available at this source
revision. It separates local proof, live Studionet proof and platform limits.
The source-verified release deployment was completed after explicit approval.
The historical RuleVault and GapJudge deployments were not replaced,
and the new monolith started with zero challenges and zero locked GEN.

| Reviewer finding | Source correction | Test evidence | Live evidence | Remaining limitation | Status |
|---|---|---|---|---|---|
| A challenger can supply only self-described hypothetical support. | Added opt-in `PINNED_SOURCE` challenges and source attempts. Rulebook and evidence references must be raw GitHub URLs pinned to a full commit, exact lowercase SHA-256 digests and version markers. Each validator independently fetches the bytes, checks HTTP status, size, UTF-8 decoding, digest, version and required rulebook text, and binds the result into the adjudication prompt and evidence hash. | `tests/test_monolith_protocol.py` covers verified bytes and substituted-byte rejection. `tests/direct/test_loophole_direct.py` covers the same path in actual GenVM Direct Mode. | [The live source-backed lifecycle](LOOPHOLE_SOURCE_BACKED_LIFECYCLE_2026-10-13.md) finalized with VERIFIED evidence and a substantive INVALID outcome. | Public byte integrity is authenticated; repository identity and real-world execution are not. | Implemented and live-tested |
| INVALID agreement previously accepted incompatible supporting findings. | `_agreement_holds` now requires exact agreement on verdict, all three tri-state findings and evidence state. Explanatory reasons remain free to vary. | The simulator rejects incompatible `letter`/`purpose` findings. The mutation test removes the exact-field comparison and demonstrates acceptance of the incompatible result. Direct Mode retains substantive validator execution. | The current deployed live evidence predates this source change and is retained as historical evidence. | A hosted validator disagreement still leaves the review pending or canceled; no fallback label is manufactured. | Implemented and tested; release deployment verified |
| Source unavailability or substitution could create an unsupported payout. | Retrieval failure, non-200 responses, oversized or non-UTF-8 content, missing version markers, hash mismatches and missing frozen policy text produce `INCONCLUSIVE` with `UNVERIFIED` evidence state. The same result is required from the independent validator before bond settlement. | Hash-mismatch simulator and Direct Mode cases prove that no prize is paid and the challenger bond returns. Prompt-injection content remains untrusted data. | The first live attempt with a wrong digest finalized INCONCLUSIVE; the corrected source-backed attempt independently authenticated the bytes before reaching INVALID. | Live web-provider behavior and source availability still depend on the hosted GenVM web module. | Implemented and live-tested |
| Native GEN delivery has an ambiguous recovery boundary. | Kept the conservative pull-credit behavior. Withdrawal clears credit once, records `TRANSFER_EMITTED_UNVERIFIED`, and never retries or recredits from a timeout, wallet report or later balance. The read-only verifier distinguishes submitted, parent-finalized, verified, failed and unresolved states. | Existing verifier tests and the current delivery evidence exercise exact origin, beneficiary, amount, finality, receipt and `value_credited` checks. | [Current funded delivery](LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md) and [current neutral delivery](LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md) include finalized child hashes and authoritative credit evidence. | Studionet does not expose a sufficiently strong authenticated proof of final non-delivery for safe automatic recovery. Ambiguous or failed transfers remain quarantined. | Limitation documented and safety preserved |
| Important lifecycle guards needed executable adversarial coverage. | Preserved FIFO review selection, reveal grace, bounded capacity, stale-round fencing, commitment binding, appeal bounds, exactly-once adjudication, caller credit checks and atomic liability settlement. | `tests/test_monolith_protocol.py`, `tests/test_monolith_mutation_behavior.py` and the full simulator suite cover stale rounds, invalid reveals, premature refunds, incompatible consensus, incorrect appeal settlement, duplicate adjudication and unauthorized zero withdrawals. | [Current VALID lifecycle](LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md), [current INVALID lifecycle](LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md) and [current INCONCLUSIVE lifecycle](LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md) provide real state and balance readbacks. | Time-based recovery, transfer failure recovery and every appeal branch are not all live-network demonstrations. Simulator and Direct Mode evidence is labeled separately. | Implemented with evidence boundaries |
| Wallet and transaction states must reflect real chain outcomes. | The frontend remains injected EIP-1193 only, gates chain `61999`, persists pending hashes, distinguishes accepted from finalized execution and links independent delivery evidence. The new source mode is shown only when the finalized `get_config` advertises it. | Frontend typecheck and production build pass. Existing browser and live-wallet evidence remains linked from the README and lifecycle records. | Production is bound to `0xB87353201CeC791cc16c25e8eE1077076D90548E`; the source-backed UI flow was used for the finalized live lifecycle linked above. | Live wallet confirmation and independent RPC verification are recorded in the source-backed lifecycle. | Implemented and live-tested |
| Dependency reports must distinguish shipped risk from pinned tooling. | Kept the repository-local CLI at `genlayer@0.39.1` and the frontend lockfile installation reproducible. | `npm --prefix frontend audit --audit-level=high` reports `0 vulnerabilities`; `npm audit --omit=dev --audit-level=high` reports no production dependency findings. | No shipped frontend dependency advisory remains in the production tree. | A root development audit reports six transitive advisories through the required GenLayer CLI's Vitest/tinypool/dockerode tree. `npm audit fix --force` proposes breaking replacement `genlayer@0.0.35`; it was not applied. This is recorded as a pinned-toolchain limitation rather than hidden or misreported as clean. | Frontend clean; CLI advisory explicitly retained |

## Evidence index

- Active source: [`contracts/Loophole.py`](../contracts/Loophole.py). The
  sole active Studionet Intelligent Contract is the monolith; the earlier
  RuleVault and GapJudge deployments remain historical and retain their own
  fund records.
- Current deployed address: [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E).
- Current deployed source evidence: [`LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md`](LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md); the previous deployment record remains historical.
- Real VALID, entitlement and verified child transfer: [`LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md`](LOOPHOLE_CURRENT_FUNDED_LIFECYCLE_2026-10-12.md).
- Real INVALID and bounded appeal state: [`LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md`](LOOPHOLE_CURRENT_INVALID_LIFECYCLE_2026-10-12.md).
- Real INCONCLUSIVE, returned bond and verified child transfer: [`LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md`](LOOPHOLE_CURRENT_NEUTRAL_LIFECYCLE_2026-10-12.md).
- Real source-backed authentication and INVALID_PENDING lifecycle: [`LOOPHOLE_SOURCE_BACKED_LIFECYCLE_2026-10-13.md`](LOOPHOLE_SOURCE_BACKED_LIFECYCLE_2026-10-13.md), with [`evidence/loophole-source-backed-lifecycle-2026-10-13.json`](evidence/loophole-source-backed-lifecycle-2026-10-13.json).
- Delivery semantics and RPC evidence: [`DELIVERY_VERIFICATION.md`](DELIVERY_VERIFICATION.md) and [`evidence/live-delivery-verification-2026-10-12.json`](evidence/live-delivery-verification-2026-10-12.json).
- Deployed source SHA-256: `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`; exact parity is recorded in the release deployment evidence.

## Reproduction commands

From the repository root, using the repository virtual environment on Windows
or the equivalent Python environment on Linux:

```powershell
.venv\Scripts\python.exe scripts\preflight.py
.venv\Scripts\python.exe scripts\validate_runner_headers.py
.venv\Scripts\python.exe scripts\verify_prompt_parity.py
.venv\Scripts\python.exe -m compileall -q contracts diagnostics scripts
.venv\Scripts\python.exe -m pytest tests -m "not direct" -q
$env:GENVM_VERSION='v0.3.0-rc7'
.venv\Scripts\genvm-lint.exe check contracts\Loophole.py --json
.venv\Scripts\python.exe -m pytest tests/direct -m direct -q
npm --prefix frontend ci
npm --prefix frontend run typecheck
npm --prefix frontend run build
node scripts/verify_delivery.mjs <withdrawal-parent-hash> <beneficiary> <amount-wei>
```

The Direct Mode resolver verifies the authenticated GenVM release asset and
its SHA-256 digest before reuse. Direct Mode and simulator results must remain
reported separately. No command above deploys a source change or sends GEN.

## Approval boundary

No additional deployment was required for the source-backed lifecycle. A future funded VALID or withdrawal test still requires explicit approval and must use the existing source-verified monolith; this negative case created no payout.
