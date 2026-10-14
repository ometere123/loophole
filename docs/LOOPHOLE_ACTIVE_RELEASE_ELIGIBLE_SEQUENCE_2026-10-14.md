# LOOPHOLE active-release eligible sequence — 2026-10-14

This record is a pre-appeal point-in-time snapshot of the previously prepared, time-eligible sequence on the active monolith at [0xB87353201CeC791cc16c25e8eE1077076D90548E](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E), on Studionet 61999. The production source was unchanged and no deployment was performed. The later finalized appeal is consolidated in [`docs/LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md`](LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md).

The repository-local CLI was 0.39.1. CLI walletA, `0x951e6b75530774ff82321a5ae54e14f778f0c855`, was unlocked and sent the three nonpayable lifecycle calls. CLI walletB, `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0`, was unlocked, was the challenger for attempt 3, and sent the withdrawal. Challenge 1 was already funded; its recorded organizer is `0xfcef676044658b5402f590dabe9e04a0f640522f`. No new attached GEN was used by this sequence.

## Finalization and adjudication

- Finalize the expired INVALID result for attempt 2, walletA, zero value: [0xfca07a7207aec6cf6f7ac25ee97572273b7611c008f7d53c385238ae4fdd1905](https://explorer-studio.genlayer.com/tx/0xfca07a7207aec6cf6f7ac25ee97572273b7611c008f7d53c385238ae4fdd1905)
- Start the queued review for challenge 1, walletA, zero value: [0x6ba23000181abd16bc02e9a9abf2b240ec87b241356836ad865d8590a92d7106](https://explorer-studio.genlayer.com/tx/0x6ba23000181abd16bc02e9a9abf2b240ec87b241356836ad865d8590a92d7106)
- Adjudicate challenge 1 / attempt 3 / round 3, walletA, zero value: [0x91f7c418cac52d4695f7ccf4b16d2d8491f2c73e43792faa7cb727ab179fa996](https://explorer-studio.genlayer.com/tx/0x91f7c418cac52d4695f7ccf4b16d2d8491f2c73e43792faa7cb727ab179fa996)

All three transactions were independently read as `FINALIZED`, had EVM receipt status `0x1`, and had successful GenVM execution. The first two had five `AGREE` votes. The adjudication reached `MAJORITY_AGREE`; the recorded votes were `AGREE, IDLE, AGREE, AGREE, IDLE`, where the two idle validators were cancelled after quorum. The frozen source-backed decision was:

```text
evidence_state=VERIFIED
letter=PROVEN
purpose=PROVEN
feasible=PROVEN
verdict=VALID
```

The post-adjudication readback showed challenge 1 `WON`, winner walletB, winner attempt 3, attempt 3 `DECIDED/VALID`, and a claimable entitlement of `0.02 GEN` (`0.01 GEN` bounty plus `0.01 GEN` bond). The contract's `get_adjudication("1:3:3")` record is `ATOMIC` and contains the same evidence hash and decision fields.

## Withdrawal and recipient credit

WalletB withdrew the exact entitlement with zero attached value:

- Withdrawal parent: [0x0daabaca54cf07cfda6956d371b61cce1f651ff76929f2c60e8553c409b86785](https://explorer-studio.genlayer.com/tx/0x0daabaca54cf07cfda6956d371b61cce1f651ff76929f2c60e8553c409b86785)
- Native GEN child: [0x8ef262753d3bb2b14fc262c45830da0d8029f316b609c9cec6283af729dd1da8](https://explorer-studio.genlayer.com/tx/0x8ef262753d3bb2b14fc262c45830da0d8029f316b609c9cec6283af729dd1da8)

The parent finalized with successful GenVM execution, receipt status `0x1`, and an explicit child relationship. `node scripts/verify_delivery.mjs` independently classified the child as `DELIVERY VERIFIED` on chain `0xf22f` because it was finalized, had receipt status `0x1`, originated at the active monolith, reached walletB, transferred exactly `20000000000000000` wei, and exposed `value_credited: true`. The contract withdrawal record remains truthfully `TRANSFER_EMITTED_UNVERIFIED`.

WalletB's CLI balance readback increased from `34.850999999999999 GEN` to `34.870999999999999 GEN`; the final `eth_getBalance` read was `34870999999999999000` wei. Contract readback showed walletB credit `0`, organizer credit `0.01 GEN`, withdrawal count `2`, total credit `0.02 GEN`, and total locked `0.02 GEN`.

The machine-readable transaction, state, receipt and accounting evidence is in [docs/evidence/loophole-active-release-eligible-sequence-2026-10-14.json](evidence/loophole-active-release-eligible-sequence-2026-10-14.json).

This evidence proves a real source-backed adjudication, atomic entitlement and independently verified native GEN delivery on the active deployment. It does not prove real-world execution of the textual scenario, appeal settlement, stalled-review recovery or safe recovery from a permanently failed external transfer.
