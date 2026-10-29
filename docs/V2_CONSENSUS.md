# V2 consensus specification

V2 uses the same GenLayer `run_nondet_unsafe` pattern as the verified V1 assessment, but with a repair-specific frozen snapshot. The leader and each validator receive the original policy, original goal, original winning evidence, proposed revision and authenticated source context. Data is explicitly delimited as untrusted evidence; instructions inside policy text, evidence text or fetched source are not authority.

## Frozen inputs

`start_repair_review` stores the proposal round and a SHA-256 snapshot over:

- original policy version and content commitment;
- original successful attempt ID, verdict and evidence commitment;
- proposed version and content commitment;
- rule, limitations, goal and source references.

`adjudicate_repair` reconstructs this snapshot from contract storage and rejects a changed hash, stale proposal, wrong challenge or wrong round before running nondeterminism.

## Decision-bearing output

The only decision-bearing fields are:

```json
{
  "closure": "PROVEN|DISPROVEN|UNKNOWN",
  "goal": "PROVEN|DISPROVEN|UNKNOWN",
  "coherence": "PROVEN|DISPROVEN|UNKNOWN",
  "reason": "specific concise explanation"
}
```

The parser rejects missing or invalid states and short/oversized explanations. The derived result is deterministic:

- all `PROVEN` → `VERIFIED_FIX`;
- any `DISPROVEN` → `NOT_VERIFIED`;
- otherwise → `INCONCLUSIVE`.

Validator equivalence compares `verdict`, `closure`, `goal`, `coherence` and `evidence_state`. This prevents a leader from obtaining agreement on a label while validators disagree about the material reason. Differences in explanatory wording are intentionally tolerated.

## Source-backed repair

For a `PINNED_SOURCE` challenge, every validator retrieves the original rulebook, winning evidence and proposed rulebook from raw GitHub URLs containing full 40-hex commit IDs. It checks HTTP success, byte size, UTF-8 decoding, SHA-256, version markers and the required frozen fields. Any failure is `UNVERIFIED`, all findings become `UNKNOWN`, and the result is `INCONCLUSIVE`. A hash authenticates bytes, not the identity or authority of the publishing organization; V2 does not claim that it solves that external identity problem.

For `HYPOTHETICAL` challenges, no external source is implied. The outcome is a bounded assessment of the frozen text and is not proof of real-world enforcement or exploitation.

Reference APIs: [GenLayer equivalence principles](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [non-deterministic execution](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism), and [transaction finality](https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/finality).
