# LOOPHOLE live negative attempt — 2026-10-12

This record preserves the second funded test on the canonical single-contract
deployment at
[`0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`](https://explorer-studio.genlayer.com/address/0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e).
It is evidence of a consensus disagreement and is not represented as a
terminal INVALID ruling.

## Transactions

- Challenge #2 funding: [`0x8206659db5e93af0136912a7e3eab332960c7395e6c94b049b7c962ac8b4c0f8`](https://explorer-studio.genlayer.com/tx/0x8206659db5e93af0136912a7e3eab332960c7395e6c94b049b7c962ac8b4c0f8) — `FINALIZED`, EVM receipt `0x1`, `SUCCESS`, `MAJORITY_AGREE`, `0.01 GEN` credited.
- Commitment: [`0x3614d6ca9126f2a537c72993fc6fbb5a2e6b144c34b6fa6047a50e32ce170e6d`](https://explorer-studio.genlayer.com/tx/0x3614d6ca9126f2a537c72993fc6fbb5a2e6b144c34b6fa6047a50e32ce170e6d) — `FINALIZED`, EVM receipt `0x1`, `SUCCESS`, exact `0.01 GEN` bond credited.
- Reveal: [`0xde3c97b5d8669a08b3688ca90982b8a3d907c60b8e221d9681ac6e85aaa53c53`](https://explorer-studio.genlayer.com/tx/0xde3c97b5d8669a08b3688ca90982b8a3d907c60b8e221d9681ac6e85aaa53c53) — `FINALIZED`, EVM receipt `0x1`, `SUCCESS`; attempt #2 became `REVEALED`.
- Freeze: [`0xb8b97a2cb861b4958a68894a43a4b002bd9c77efcf551310ab276a42f3f6b431`](https://explorer-studio.genlayer.com/tx/0xb8b97a2cb861b4958a68894a43a4b002bd9c77efcf551310ab276a42f3f6b431) — `FINALIZED`, EVM receipt `0x1`, `SUCCESS`; challenge #2 entered review round 1.
- Adjudication: [`0x072460d1b5e494087098b0485f18c7b03fd48d61425a9f952c10c0b18c7c5104`](https://explorer-studio.genlayer.com/tx/0x072460d1b5e494087098b0485f18c7b03fd48d61425a9f952c10c0b18c7c5104) — `FINALIZED`, EVM receipt `0x1`, leader GenVM `SUCCESS`, but consensus result `MAJORITY_DISAGREE`.

## Frozen evidence and readback

The challenge was titled `Exact word-count gate` with the goal of rewarding
educational contributions that genuinely help readers learn. Its rule required
a public post with at least five words and one source link. The limitations
explicitly made a post with fewer than five words ineligible. The revealed
scenario claimed a four-word post and one source link.

The final readback at `https://studio.genlayer.com/api` on chain `0xf22f`
showed:

- challenge #2: `OPEN`, `active_attempt=2`, `active_round=1`, `active_slots=1`;
- attempt #2: `REVIEWING`, `verdict=""`, `letter=false`, `purpose=false`, `feasible=false`;
- `adjudication_count=1`, unchanged from the prior settled VALID lifecycle;
- `total_locked_wei=20000000000000000`, `total_credit_wei=0`;
- no winner, entitlement, withdrawal, callback, or payout was created.

The transaction receipt contained four consensus rotations. The available leader
outputs classified the literal finding as `DISPROVEN` and therefore proposed
`INVALID` every time. Supporting purpose findings varied between `UNKNOWN` and
`DISPROVEN`. The public receipt does not expose each validator's complete LLM
output, but it does expose three successful `DISAGREE` votes, one successful
`AGREE` vote, and one validator cancelled after quorum. All completed validators
reported GenVM `SUCCESS`; the disagreement was semantic/equivalence-level, not a
GenVM crash or timeout.

The public RPC supports `eth_getTransactionReceipt` and
`gen_getTransactionStatus`. The requested `gen_getTransactionReceipt`,
`gen_getConsensusData`, fee, execution, lifecycle, log, history, and debug trace
methods returned JSON-RPC `-32601 Method not found` on this Studionet endpoint.

## Corrective change

The deployed source required the complete `LETTER`, `PURPOSE`, and `FEASIBLE`
tristate tuple to match. That made an economically safe INVALID result stall
when independent validators agreed on the same invalidating finding but differed
on additional downstream support. The pending source correction keeps the full
independent assessment, requires the same settlement verdict, and for INVALID
requires at least one common `DISPROVEN` finding. VALID still requires all three
findings to be `PROVEN`; INCONCLUSIVE still rejects any `DISPROVEN` finding.

This source correction has passed local behavioral tests, Direct Mode, GenVM
lint and semantic validation. It is not deployed yet. The canonical deployment
and the funded challenge remain unchanged, and no adjudication retry was issued.

