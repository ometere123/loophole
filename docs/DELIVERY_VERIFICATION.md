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
