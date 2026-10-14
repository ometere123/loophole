# LOOPHOLE bonded appeal evidence — 2026-10-14

This record began as a read-only preparation for the bonded appeal on the
active Studionet release. After explicit approval, exactly one appeal
transaction was signed with the repository-local CLI keychain and verified
without exposing the private key or issuing a retry.

## Active release

- Network: GenLayer Studionet, chain `61999` (`0xf22f`)
- Contract: [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E)
- Deployment: [`0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960`](https://explorer-studio.genlayer.com/tx/0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960)
- Repository source: `contracts/Loophole.py`
- Source SHA-256: `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`
- Deployment source bytes and repository source bytes both hashed to the value above; the deployment verifier reported exact byte parity, finalized status, EVM receipt `0x1`, and GenVM `SUCCESS`.

## Appeal readiness

The following state was read from `LATEST_FINAL` at `2026-10-14T19:29:19Z`.

- Challenge `3`: `OPEN`; `active_attempt=0`; `active_round=1`; `active_slots=1`; `review_started=0`.
- Attempt `5`: `INVALID_PENDING`; challenger `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0`; `appeal_used=false`.
- Attempt bond: `10000000000000000` wei (`0.01 GEN`).
- Appeal deadline: Unix `1792019100`, `2026-10-14T23:05:00Z`.
- Wallet B latest balance: `34.870999999999999 GEN`; CLI account status: `unlocked`.
- `get_adjudication("3:5:1")`: `INVALID`, `evidence_state=VERIFIED`, `letter=DISPROVEN`, `purpose=DISPROVEN`, `feasible=PROVEN`, `settlement=ATOMIC`.

**Preflight status: READY.** The exact transaction intent was:

```text
from:     0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0  (Wallet B)
to:       0xB87353201CeC791cc16c25e8eE1077076D90548E
chain:    61999
method:   appeal_invalid
args:     [5]
value:    10000000000000000 wei (0.01 GEN)
sent:     once, after explicit approval
```

The CLI preflight rechecked chain `0xf22f`, the Wallet B key address, the
appeal window, the challenger, the exact bond and challenge idleness before
signing. The CLI command’s built-in contract writer hardcodes zero value, so
the transaction was submitted through the repository-local `genlayer-js`
value-capable client using the unlocked `walletB` keychain entry.

## Appeal transaction result

- Transaction: [`appeal_invalid(5)`](https://explorer-studio.genlayer.com/tx/0x18c14608d5eb3633545b0f48d26112245a24bf5c82c69d2e8ddb4e08b43579af)
- Sender: Wallet B, `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0`
- Attached value: `10000000000000000` wei (`0.01 GEN`)
- Status: `FINALIZED`; EVM receipt `0x1`; leader GenVM execution `SUCCESS`
- Consensus: `MAJORITY_AGREE`; all five validator votes were `agree`
- Triggered child transactions: none

The finalized state read at `2026-10-14T19:55:39Z` is:

- Attempt `5`: `APPEAL_REVIEWING`, `appeal_used=true`, `appeal_bond_wei=10000000000000000`.
- Challenge `3`: `OPEN`, `active_attempt=5`, `active_round=2`, `active_slots=1`.
- Wallet B credit: `0`.
- `total_locked_wei`: `30000000000000000`; `total_credit_wei`: `20000000000000000`.
- `get_adjudication("3:5:2")`: empty because the appeal review has not yet been adjudicated.

## Existing live evidence

All rows below target the active monolith and were read as `FINALIZED` with EVM
receipt `0x1` and successful leader GenVM execution. The hosted RPC does not
implement `gen_getTransactionReceipt` (`-32601 Method not found`), so the
independent checks use `gen_getTransactionStatus`, `eth_getTransactionReceipt`,
consensus fields, contract readbacks and the supported child-transfer fields.

| Lifecycle | Transaction | Verified result |
| --- | --- | --- |
| Unappealed INVALID settlement, attempt 2 | [finalize_invalid](https://explorer-studio.genlayer.com/tx/0xfca07a7207aec6cf6f7ac25ee97572273b7611c008f7d53c385238ae4fdd1905) | `MAJORITY_AGREE`, five `agree` votes; state `DECIDED/INVALID`; organizer bond credit recorded. |
| Source-backed VALID, attempt 3 | [adjudication](https://explorer-studio.genlayer.com/tx/0x91f7c418cac52d4695f7ccf4b16d2d8491f2c73e43792faa7cb727ab179fa996) | `MAJORITY_AGREE`, three `agree` and two `idle` votes after quorum; challenge 1 `WON`; `0.02 GEN` entitlement. |
| Source-backed VALID, attempt 4 | [adjudication](https://explorer-studio.genlayer.com/tx/0xead922f8c61a7936209fa85f181ee2a03ab50f14e92937a6fc08be6fc441d95b) | `MAJORITY_AGREE`, three `agree` and two `idle` votes after quorum; challenge 2 `WON`; `0.03 GEN` entitlement. |
| Appeal target, attempt 5 | [initial adjudication](https://explorer-studio.genlayer.com/tx/0x31adc6f710e14b158ebd17e358702d66ffa24177ede9a8386e5df877ff8be5dc) · [appeal](https://explorer-studio.genlayer.com/tx/0x18c14608d5eb3633545b0f48d26112245a24bf5c82c69d2e8ddb4e08b43579af) | Initial result was `INVALID_PENDING`; the appeal finalized with five `agree` votes and moved the attempt to `APPEAL_REVIEWING`, round 2. |

## Independently verified GEN delivery

The withdrawal records remain truthfully `TRANSFER_EMITTED_UNVERIFIED` because
the contract cannot observe external child receipts. The read-only verifier
independently established delivery for both active-release withdrawals:

| Amount | Parent | Child | Beneficiary | Evidence |
| ---: | --- | --- | --- | --- |
| `0.03 GEN` | [parent](https://explorer-studio.genlayer.com/tx/0x005568ee1b22971c54f62a21ef227271c765b8e0883cf87573469a0d86e03849) | [child](https://explorer-studio.genlayer.com/tx/0x0c04cd4f4824311cbac060cc623dc684aa3d31ca569f656525ac7459ff2b33e3) | `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0` | Parent and child finalized; receipts `0x1`; child origin is the active monolith; exact recipient/value match; `value_credited=true`. |
| `0.02 GEN` | [parent](https://explorer-studio.genlayer.com/tx/0x0daabaca54cf07cfda6956d371b61cce1f651ff76929f2c60e8553c409b86785) | [child](https://explorer-studio.genlayer.com/tx/0x8ef262753d3bb2b14fc262c45830da0d8029f316b609c9cec6283af729dd1da8) | `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0` | Parent and child finalized; receipts `0x1`; child origin is the active monolith; exact recipient/value match; `value_credited=true`. |

The latest readback shows Wallet B credit `0`, Wallet A credit `0`, two
withdrawal records, `total_credit_wei=20000000000000000`, and
`total_locked_wei=20000000000000000`. The remaining locked liability is the
challenge 3 bounty (`0.01 GEN`) plus attempt 5’s pending bond (`0.01 GEN`);
the outstanding `0.02 GEN` credit is held by two earlier participants and is
not Wallet B’s withdrawn entitlement.

## Read-only eligibility and remaining appeal review

`node scripts/inspect_recovery_eligibility.mjs` now defaults to the active
monolith and reported no stalled-review recovery candidates. Challenge 3 is
now in an active appeal review, so refund and invalid finalization remain
blocked. No additional write was called after the appeal.

The remaining appeal evidence is intentionally empty until adjudication and
settlement exist:

```text
appeal transaction:       VERIFIED above
appeal finality:          VERIFIED above
appeal consensus/verdict: PENDING adjudicate_review(3, 5, 2)
appeal settlement:        PENDING the finalized appeal adjudication
post-settlement reads:    PENDING
```

## Reproduction checks

```text
node scripts/inspect_recovery_eligibility.mjs
node scripts/verify_delivery.mjs 0x005568ee1b22971c54f62a21ef227271c765b8e0883cf87573469a0d86e03849 0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0 30000000000000000
node scripts/verify_delivery.mjs 0x0daabaca54cf07cfda6956d371b61cce1f651ff76929f2c60e8553c409b86785 0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0 20000000000000000
node --test scripts/delivery_classifier.test.mjs
python -m pytest -q
python scripts/verify_release_integrity.py
node scripts/verify_contract_deployment.mjs 0xB87353201CeC791cc16c25e8eE1077076D90548E 0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960 contracts/Loophole.py
```
