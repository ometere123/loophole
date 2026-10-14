# External GEN delivery verification

Loophole withdrawal records remain `TRANSFER_EMITTED_UNVERIFIED` because an Intelligent Contract cannot synchronously prove delivery of a native GEN message to an EOA.

The current default origin is the active source-verified Studionet monolith
`0xB87353201CeC791cc16c25e8eE1077076D90548E`. Historical deployment addresses
are never used as implicit defaults by the verifier.

Use the read-only verifier after a withdrawal parent is finalized:

```powershell
node scripts/verify_delivery.mjs <withdrawal-parent-hash> <beneficiary> <amount-wei>
```

The verifier checks Studionet chain `0xF22F`, the canonical Loophole origin, parent finality and successful leader return evidence, then follows `triggered_transactions`. For every parent and child it also queries `gen_getTransactionStatus` and `eth_getTransactionReceipt` when available. Consensus-bearing children require successful GenVM execution; native GEN transfer children do not run GenVM, so their execution evidence is finalized transport success plus authoritative `value_credited: true`. This is why a failed GapJudge transaction can expose an EVM success envelope while its GenLayer status is `CANCELED`.

The verifier distinguishes `TRANSFER SUBMITTED`, `PARENT FINALIZED`, `DELIVERY VERIFIED`, `FAILED`, and `UNRESOLVED`. It reports `DELIVERY VERIFIED` only when a child is finalized, is sent from the canonical Loophole contract to the exact beneficiary for the exact amount, and carries authoritative `value_credited: true`. A consensus-bearing child must also have successful GenVM execution; a native transfer child must have successful transport receipt evidence when available. If an RPC method is unsupported, rate limited, or temporarily unavailable, the result records that category rather than silently treating missing evidence as success. A `CLAIMABLE` balance is an entitlement before withdrawal and is not delivery evidence. Missing, mismatched, conflicting, or incomplete evidence remains `UNRESOLVED`.

The check is read-only. It never retries a transfer, restores credit, or treats a positive contract balance or beneficiary acknowledgement as proof.

## Protocol recovery boundary

The official GenLayer transfer documentation states that an emitted value is
deducted from the sending Intelligent Contract immediately, held with the
message, and credited only when the child transaction is activated. It also
states explicitly that a failed child transaction does not automatically
return the value to the sender. External EOA delivery is handled through the
protocol's ghost contract and is asynchronous; the sender contract cannot
synchronously observe the recipient's final credit. See the official
[value-transfer documentation](https://docs.genlayer.com/developers/intelligent-contracts/features/value-transfers)
and [message lifecycle documentation](https://docs.genlayer.com/developers/intelligent-contracts/features/messages).

That protocol behavior is why this release does not add an administrator
refund, timeout re-credit, user-submitted receipt, or blind retry. A safe
re-credit would require an authenticated proof that the particular child can
never later credit the bound recipient, together with protection against a
late original delivery. The deployed contract and the currently exposed
Studionet RPC do not provide that proof. Ambiguous or failed delivery is
therefore quarantined as `UNRESOLVED`/`FAILED` by the read-only verifier while
the contract's `TRANSFER_EMITTED_UNVERIFIED` record remains truthful.

The verifier also records RPC capability rather than treating missing data as
success. The current hosted Studionet endpoint accepts the legacy string form
for `gen_getTransactionStatus`, but rejects the documented `{txId: ...}`
object form with a server-side parameter error. `gen_getTransactionReceipt`
and `gen_getTransactionLifecycle` are currently reported as unsupported by
that endpoint. The inspector tries the documented forms first, records the
exact response category, and uses the legacy status form only as an explicit
compatibility fallback. The public receipt API shape is documented at
[gen_getTransactionReceipt](https://docs.genlayer.com/api-references/genlayer-node/gen/gen_getTransactionReceipt),
and lifecycle projection at
[gen_getTransactionLifecycle](https://docs.genlayer.com/api-references/genlayer-node/gen/gen_getTransactionLifecycle).
GenLayer's application guidance also says to require both a terminal status and
successful execution, resume tracking an existing transaction after a timeout,
and avoid resubmitting a state-changing write after an ID has been issued; see
[fee outcomes and debugging](https://docs.genlayer.com/developers/decentralized-applications/fee-outcomes-and-debugging)
and [writing data](https://docs.genlayer.com/developers/decentralized-applications/writing-data).
The platform's [error and revert reference](https://docs.genlayer.com/developers/error-reference)
lists generic `FailedTransfer` and `FailedTransferCall` errors, but those are
protocol revert categories; they are not an authenticated, withdrawal-bound
proof that a native EOA child can never deliver later, so they cannot safely
justify re-crediting this contract's liability.

The pure state classifier has deterministic coverage for successful delivery,
parent-finalized-without-child, pending children, authoritative child failure,
missing `value_credited`, RPC rate limits and status conflicts:

```powershell
node --test scripts/delivery_classifier.test.mjs
```

These tests validate reconciliation decisions and failure containment. They do
not claim that Studionet produced a live failed native transfer; no such
authoritative failure has been observed.

The RPC comparison in [`docs/evidence/delivery-verifier-rpc-comparison-2026-10-11.json`](evidence/delivery-verifier-rpc-comparison-2026-10-11.json) records the distinction against live Studionet data: the relay parent and child are `FINALIZED` with successful GenLayer execution and EVM `0x1` receipts, while the failed GapJudge child has an EVM `0x1` receipt but GenLayer `CANCELED`, `NO_MAJORITY`, `recovery_count: 3`, and `max_recovery_cycles_exceeded`.

A fresh read-only probe on 2026-10-14 recorded the same two failed GapJudge children, [`0x720e15…a5ed4`](evidence/rpc-delivery-capability-2026-10-14.json) and [`0x215ca5…44ef4`](evidence/rpc-delivery-capability-2026-10-14.json): both are on chain `0xF22F`, `CANCELED`/`NO_MAJORITY`, `recovery_count: 3`, `max_recovery_cycles_exceeded`, with empty public vote and validator arrays. The same probe followed the successful withdrawal parent `0x005568…03849` to native child `0x0c04cd…b33e3`; both are `FINALIZED`, and the child carries `value_credited: true` for the already documented delivery. The hosted RPC returned `Method not found` for receipt, fee and lifecycle methods on the failed children; one later request was explicitly categorized as rate-limited, not silently treated as unsupported. These results document the observation boundary; they do not turn a canceled consensus child into evidence of a failed native GEN transfer.
