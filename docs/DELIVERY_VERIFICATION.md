# External GEN delivery verification

RuleVault withdrawal records remain `TRANSFER_EMITTED_UNVERIFIED` because an Intelligent Contract cannot synchronously prove delivery of a native GEN message to an EOA.

Use the read-only verifier after a withdrawal parent is finalized:

```powershell
node scripts/verify_delivery.mjs <withdrawal-parent-hash> <beneficiary> <amount-wei>
```

The verifier checks Studionet chain `0xF22F`, the canonical RuleVault origin, parent finality and successful leader return evidence, then follows `triggered_transactions`. It distinguishes `TRANSFER SUBMITTED`, `PARENT FINALIZED`, `DELIVERY VERIFIED`, `FAILED`, and `UNRESOLVED`. It reports `DELIVERY VERIFIED` only when a child is finalized, successful by authoritative `value_credited`, sent from RuleVault to the exact beneficiary, and carries the exact expected amount. A `CLAIMABLE` balance is an entitlement before withdrawal and is not delivery evidence. Missing, mismatched, or incomplete evidence remains `UNRESOLVED`.

The check is read-only. It never retries a transfer, restores credit, or treats a positive contract balance or beneficiary acknowledgement as proof.
