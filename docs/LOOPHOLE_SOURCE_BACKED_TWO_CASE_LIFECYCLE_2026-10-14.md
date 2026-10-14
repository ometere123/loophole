# LOOPHOLE source-backed two-case lifecycle — 2026-10-14

This record is a pre-appeal point-in-time snapshot of two source-backed cases executed on the active Loophole monolith at [0xB87353201CeC791cc16c25e8eE1077076D90548E](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E) on Studionet 61999. The production source was unchanged and no deployment was performed. Its challenge 3 `INVALID_PENDING` state predates the later finalized appeal; the current appeal, settlement and consolidated delivery evidence are in [`docs/LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md`](LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md).

The organizer was Wallet A, 0x951e6b75530774ff82321a5ae54e14f778f0c855. The challenger and withdrawal beneficiary was Wallet B, 0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0. The repository-local CLI was 0.39.1, both accounts were unlocked in the CLI keychain, the chain readback was 0xf22f, and the RPC gas and priority-fee quotes were zero.

The rulebook and attempt evidence used the same immutable external source:

- URL: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/97430aa29ac10a70ee0c18f2a905c4925363b58f/README.md
- HTTP status: 200
- UTF-8 bytes: 8979
- SHA-256: 4c7bb702a0a318fd6bb92438017c0c166242b3a20d3c4502ced71983e1d0b282
- Version marker: OpenZeppelin Contracts

The source was independently fetched before submission and the contract fetched it again during each validator assessment. This authenticates the pinned bytes and their material rule fragments; it does not prove the publisher identity or real-world execution of the described commands.

## Source-backed VALID case

Challenge 2 was funded with 0.02 GEN. Attempt 4 used a 0.01 GEN bond. The committed attack described running forge update after installing the tagged release, causing the working tree to use the master branch. The frozen rulebook stated that forge update uses master, while its limitation stated that master does not carry the release security guarantees.

Every transaction below reached FINALIZED, had an EVM receipt status of 0x1, and had successful GenVM execution where consensus applied:

- Create and fund challenge 2, Wallet A, 0.02 GEN: [0x0854397ed13f1cd6fdabb2f55d5aed3b3a1b86b0caaddb410bfaf2805b0ddc4b](https://explorer-studio.genlayer.com/tx/0x0854397ed13f1cd6fdabb2f55d5aed3b3a1b86b0caaddb410bfaf2805b0ddc4b)
- Commit attempt 4, Wallet B, 0.01 GEN: [0xe477510e46da0f38ebb7a38a4fdaef0a8ba99576b2d38b88e5d7e8a9912dd602](https://explorer-studio.genlayer.com/tx/0xe477510e46da0f38ebb7a38a4fdaef0a8ba99576b2d38b88e5d7e8a9912dd602)
- Reveal attempt 4, Wallet B, zero value: [0x4a738a0bf2b376971f2008737cf6c40df5f5c3b8c94df68dc65a09070d09ab10](https://explorer-studio.genlayer.com/tx/0x4a738a0bf2b376971f2008737cf6c40df5f5c3b8c94df68dc65a09070d09ab10)
- Freeze review, Wallet B, zero value: [0x19ef65087d4a23957c65b8d1019cbbb033cc1d0df53b7830f7328af655c949df](https://explorer-studio.genlayer.com/tx/0x19ef65087d4a23957c65b8d1019cbbb033cc1d0df53b7830f7328af655c949df)
- Adjudicate challenge 2 / attempt 4 / round 1, Wallet B, zero value: [0xead922f8c61a7936209fa85f181ee2a03ab50f14e92937a6fc08be6fc441d95b](https://explorer-studio.genlayer.com/tx/0xead922f8c61a7936209fa85f181ee2a03ab50f14e92937a6fc08be6fc441d95b)

The adjudication finalized with result name MAJORITY_AGREE and successful leader execution. The recorded validator votes were AGREE, AGREE, IDLE, AGREE, IDLE. The decision-critical result was evidence VERIFIED, letter PROVEN, purpose PROVEN, feasible PROVEN, and verdict VALID. The state readback was challenge WON, winner Wallet B, attempt DECIDED, active attempt 0, and active slot count 0. The challenge entitlement was the 0.02 GEN prize plus the 0.01 GEN bond: 0.03 GEN.

## Independently verified GEN delivery

Wallet B submitted withdraw with zero attached value:

- Withdrawal parent: [0x005568ee1b22971c54f62a21ef227271c765b8e0883cf87573469a0d86e03849](https://explorer-studio.genlayer.com/tx/0x005568ee1b22971c54f62a21ef227271c765b8e0883cf87573469a0d86e03849)
- Emitted native GEN child: [0x0c04cd4f4824311cbac060cc623dc684aa3d31ca569f656525ac7459ff2b33e3](https://explorer-studio.genlayer.com/tx/0x0c04cd4f4824311cbac060cc623dc684aa3d31ca569f656525ac7459ff2b33e3)

The parent finalized with result name MAJORITY_AGREE, successful GenVM execution and EVM receipt status 0x1. Its finalized transaction record identified the child relationship. The independent read-only delivery verifier then confirmed:

- chain ID 0xf22f;
- parent destination exactly the active Loophole contract;
- child status FINALIZED and EVM receipt status 0x1;
- child origin exactly the active Loophole contract;
- child recipient exactly Wallet B;
- child value exactly 30000000000000000 wei;
- authoritative value_credited true;
- no status conflict or receipt failure.

The verifier classified the result DELIVERY VERIFIED. The contract withdrawal record remains TRANSFER_EMITTED_UNVERIFIED because the contract cannot observe this external child proof itself. The post-withdraw state readback showed Wallet B credit zero and withdrawal count one.

## RPC inspection

The read-only inspector confirmed `gen_getTransactionStatus` as `FINALIZED` and `eth_getTransactionReceipt` with status `0x1` for every listed transaction. A fresh single-transaction probe returned `-32601 Method not found` for `gen_getTransactionReceipt`, so that method is recorded as unsupported. The bulk diagnostic pass later reached the endpoint's 30-requests-per-minute limit and recorded `-32029` responses as rate-limited. Unsupported, rate-limited and temporary failures are kept distinct; no absent optional response was treated as proof of success.

## Source-backed INVALID case

Challenge 3 was funded with 0.01 GEN. Attempt 5 used a 0.01 GEN bond. Its frozen sequence explicitly avoided forge update and master, so it did not satisfy the quoted subsequent-update condition and did not defeat the stated goal.

- Create and fund challenge 3, Wallet A, 0.01 GEN: [0x8d515fd702bb81a35de501c292f3f00953de68eeb206f10fca8d35ab3288df23](https://explorer-studio.genlayer.com/tx/0x8d515fd702bb81a35de501c292f3f00953de68eeb206f10fca8d35ab3288df23)
- Commit attempt 5, Wallet B, 0.01 GEN: [0xa8d06203d96ab9f9db26ad9b18d79cfcc6d3051753d5a5f270bd42b70dee795e](https://explorer-studio.genlayer.com/tx/0xa8d06203d96ab9f9db26ad9b18d79cfcc6d3051753d5a5f270bd42b70dee795e)
- Reveal attempt 5, Wallet B, zero value: [0x1a0dcb3818e5ebaa424ef81b765dbc60f68185f167af7ab2d3cfd358ca240ac8](https://explorer-studio.genlayer.com/tx/0x1a0dcb3818e5ebaa424ef81b765dbc60f68185f167af7ab2d3cfd358ca240ac8)
- Freeze review, Wallet B, zero value: [0xc7433234086a74c36f5d135801f246ecb8183f712fac8971a07f74c38ae52e13](https://explorer-studio.genlayer.com/tx/0xc7433234086a74c36f5d135801f246ecb8183f712fac8971a07f74c38ae52e13)
- Adjudicate challenge 3 / attempt 5 / round 1, Wallet B, zero value: [0x31adc6f710e14b158ebd17e358702d66ffa24177ede9a8386e5df877ff8be5dc](https://explorer-studio.genlayer.com/tx/0x31adc6f710e14b158ebd17e358702d66ffa24177ede9a8386e5df877ff8be5dc)

The adjudication finalized with result name MAJORITY_AGREE and successful leader execution. The recorded validator votes were AGREE, DISAGREE, AGREE, AGREE, DISAGREE. The authenticated decision was evidence VERIFIED, letter DISPROVEN, purpose DISPROVEN, feasible PROVEN, and verdict INVALID. This is substantive disagreement on decision-critical findings, while the accepted consensus result remained INVALID.

At this pre-appeal snapshot, the final state readback was challenge OPEN, active attempt 0, attempt INVALID_PENDING, appeal_used false, and no winner or entitlement. The appeal deadline is 2026-10-14T23:05:00Z. No appeal had yet been submitted because the approved 0.05 GEN attached-value ceiling was fully consumed by the two challenge prizes and two original bonds. This historical record makes no appeal-result claim; the later finalized appeal is consolidated in [`docs/LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md`](LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md).

## Accounting and scope

The two tests attached exactly 0.05 GEN in total: 0.02 GEN for challenge 2, 0.01 GEN for its bond, 0.01 GEN for challenge 3, and 0.01 GEN for its bond. Zero-value writes and the withdrawal did not add attached value. The final contract readback was challenge_count 3, attempt_count 5, adjudication_count 4, withdrawal_count 1, total_credit_wei 10000000000000000, and total_locked_wei 50000000000000000.

Challenge 1 and its existing attempts were not modified. No deployment, source change, forced callback, appeal bypass, automatic retry or additional payment was performed. The source-backed cases prove authenticated bytes, validator execution and real economic settlement on the active deployment; they do not prove publisher authority, real-world command execution, appeal settlement, timeout recovery or failed-transfer recovery.

Machine-readable evidence is in [docs/evidence/loophole-source-backed-two-case-lifecycle-2026-10-14.json](evidence/loophole-source-backed-two-case-lifecycle-2026-10-14.json).
