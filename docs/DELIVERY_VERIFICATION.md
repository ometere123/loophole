# External GEN delivery verification

RuleVault withdrawal records remain `TRANSFER_EMITTED_UNVERIFIED` because an Intelligent Contract cannot synchronously prove delivery of a native GEN message to an EOA.

Use the read-only verifier after a withdrawal parent is finalized:

```powershell
node scripts/verify_delivery.mjs <withdrawal-parent-hash> <beneficiary> <amount-wei>
```

The verifier checks Studionet chain `0xF22F`, the canonical RuleVault origin, parent finality and successful leader return evidence, then follows `triggered_transactions`. For every parent and child it also queries `gen_getTransactionStatus` and `eth_getTransactionReceipt` when available. The GenLayer lifecycle result and execution fields remain authoritative for contract success; the EVM receipt is a transport check and a receipt with `status: 0x1` alone never proves a successful GenLayer execution. This is why a failed GapJudge transaction can expose an EVM success envelope while its GenLayer status is `CANCELED`.

The verifier distinguishes `TRANSFER SUBMITTED`, `PARENT FINALIZED`, `DELIVERY VERIFIED`, `FAILED`, and `UNRESOLVED`. It reports `DELIVERY VERIFIED` only when a child is finalized, has successful GenLayer execution, is sent from RuleVault to the exact beneficiary for the exact amount, and carries authoritative `value_credited: true`; a supported EVM receipt must also be present and successful. If an RPC method is unsupported, rate limited, or temporarily unavailable, the result records that category rather than silently treating missing evidence as success. A `CLAIMABLE` balance is an entitlement before withdrawal and is not delivery evidence. Missing, mismatched, conflicting, or incomplete evidence remains `UNRESOLVED`.

The check is read-only. It never retries a transfer, restores credit, or treats a positive contract balance or beneficiary acknowledgement as proof.

The RPC comparison in [`docs/evidence/delivery-verifier-rpc-comparison-2026-10-11.json`](evidence/delivery-verifier-rpc-comparison-2026-10-11.json) records the distinction against live Studionet data: the relay parent and child are `FINALIZED` with successful GenLayer execution and EVM `0x1` receipts, while the failed GapJudge child has an EVM `0x1` receipt but GenLayer `CANCELED`, `NO_MAJORITY`, `recovery_count: 3`, and `max_recovery_cycles_exceeded`.
