# LOOPHOLE corrected deployment live lifecycle — 2026-10-12

The canonical corrected single-contract deployment completed a funded lifecycle
on Studionet 61999. The complete sanitized evidence record is
[`docs/evidence/loophole-corrected-live-lifecycle-2026-10-12.json`](evidence/loophole-corrected-live-lifecycle-2026-10-12.json).

- Contract: [`0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`](https://explorer-studio.genlayer.com/address/0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e)
- Source SHA-256: `f173b087336403044db3ce793c2c0df57e5104b5078964b2ce8b8b7e88ccf8c7`
- Challenge funding: [`0xb22ffb39a5d18ba82aa646f428e9932a8a3b4dc3f469c184e327188f7d7972ae`](https://explorer-studio.genlayer.com/tx/0xb22ffb39a5d18ba82aa646f428e9932a8a3b4dc3f469c184e327188f7d7972ae) — finalized, successful, 0.02 GEN credited
- Commitment: [`0x2d92802b2a5772e2732621271f3e722ca170a929562b2f074893187f1273f057`](https://explorer-studio.genlayer.com/tx/0x2d92802b2a5772e2732621271f3e722ca170a929562b2f074893187f1273f057) — finalized, successful, 0.01 GEN credited
- Reveal: [`0x9c20d74900a7ffe615a4e2531e94ffe7caaea973ecf7cfd9628ec052b8f1428e`](https://explorer-studio.genlayer.com/tx/0x9c20d74900a7ffe615a4e2531e94ffe7caaea973ecf7cfd9628ec052b8f1428e) — finalized and the attempt became `REVEALED`
- Freeze/review: [`0x439f492d16b0fe5e07d07b2e81b0ea46f4f5ffc4f678607941751259bf99a15d`](https://explorer-studio.genlayer.com/tx/0x439f492d16b0fe5e07d07b2e81b0ea46f4f5ffc4f678607941751259bf99a15d) — finalized and the attempt became `REVIEWING`
- Adjudication: [`0x6a92213a49bbc55e313e81a9aedf10068d65d91380cd8c9aa476def919918c89`](https://explorer-studio.genlayer.com/tx/0x6a92213a49bbc55e313e81a9aedf10068d65d91380cd8c9aa476def919918c89) — finalized, GenVM `SUCCESS`, `MAJORITY_AGREE`, 3 validator `AGREE` and 2 `DISAGREE`; the recorded result was `VALID` with `LETTER`, `PURPOSE` and `FEASIBLE` all `PROVEN`

The finalized state was `WON`, with the challenger as winner and a 0.03 GEN
entitlement. The withdrawal parent
[`0xdea2deed18247db21a2cd1fb2f150f2d1cd22b8775b5c378d378a612f06b8aa2`](https://explorer-studio.genlayer.com/tx/0xdea2deed18247db21a2cd1fb2f150f2d1cd22b8775b5c378d378a612f06b8aa2)
finalized with successful execution and exposed child
[`0x8fb540e4f09ac6e3ba5a33df87a62366238a7b0f70aef778ae2ad22f870806b6`](https://explorer-studio.genlayer.com/tx/0x8fb540e4f09ac6e3ba5a33df87a62366238a7b0f70aef778ae2ad22f870806b6).
The child finalized with EVM receipt `0x1`, originated at the canonical
contract, reached the exact challenger address for exactly 0.03 GEN and
reported authoritative `value_credited=true`. The readback after withdrawal
was zero credit, zero locked funds and one withdrawal record.

The on-chain withdrawal record remains `TRANSFER_EMITTED_UNVERIFIED` because
the contract cannot synchronously observe native GEN delivery. The independent
read-only verifier reported `DELIVERY VERIFIED` from the finalized parent-child
relationship, exact address/value match, successful transport receipt and
authoritative credit evidence.
