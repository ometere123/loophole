# Economic security and failure cases

| Invariant / scenario | Enforcement | Residual risk |
|---|---|---|
| Can't rewrite funded rule | no edit method, frozen snapshot in challenge map | GenLayer network rollback prior to finalization; UI reads finalized |
| Can't self-redeem as the same wallet | vault checks organizer address | Sybil identity not solved |
| Commitments can't be stolen from mempool | SHA-256 domain separation incl account and challenge | compromised local backup or salted data disclosure |
| Fixed GEN bonds | exact payable amount enforced | native-value transfer implementation must be verified live |
| Can't queue simultaneous reviews | only one active review per challenge | malicious spam can slow throughput |
| Unauthorized callback rejected | direct sender must match bound judge address | malicious deployer can bind wrong initial vault, inspect configuration |
| Replay/stale verdict | active attempt and current round must match | asynchronous children can remain delayed |
| No double prize | winner seals challenge and no later callbacks can credit prize | transaction finality/reorg must be handled |
| Locked bounty recoverable | expiry+48h and no active review; stalled review recovery after 5d | if judge callback execution fails, a human must trigger recovery |
| Expired commitments forfeited | public bond settlement method after close | sponsor/winner cannot seize an already decided bond |
| Revealed but never reviewed bonds refund | public method once challenge won/refunded | challenger must send a transaction |
| Claim accounting first | credit cleared before outbound transfer | child EVM transfer may fail; GenLayer does **not** return failed-message value automatically |

## Major remaining external verification

1. Source must pass `genvm-lint` on exact runtime, including annotated storage and typed address conversions.
2. Deploy both contracts using repo-local 0.39.1 on Studionet 61999 and verify their schemas/source hashes.
3. Bind judge after vault deployment; check `get_configuration()` and `get_config()` show reciprocal addresses.
4. Execute 3-wallet funded lifecycle with a real VALID, INVALID, and INCONCLUSIVE answer; inspect emitted child transactions.
5. Verify exact source and proof timeline for every callback: parent finalized → child created → child finalized → vault updated.
6. Verify EOA value transfer independently from the vault withdrawal record. Never describe `TRANSFER_EMITTED_UNVERIFIED` as paid.
7. Demonstrate timeout recovery, failed callbacks and native-balance/credit reconciliation. Obtain external security review before large GEN values.

This is not formal verification. The 12-attempt capacity is a bounded resource and can be exhausted by Sybil actors; increasing it adds cost, not genuine Sybil protection.
