# Studionet adjudication differential probe

`AdjudicationProbe.py` is a diagnostic contract kept separate from the two LOOPHOLE production contracts. It is designed to isolate three paths with the same pinned GenLayer SDK and network:

1. `direct_judgment(prompt)` executes a small `run_nondet_unsafe` judgment in the user submitted transaction.
2. `trigger_judgment(prompt)` schedules the identical judgment through `emit(on='finalized')`.
3. `trigger_ping()` schedules a deterministic finalized child without LLM execution.

`CrossContractRelay.py` is a separate diagnostic sender. Its
`trigger_probe(prompt)` emits the same `direct_judgment` call to the already
deployed corrected probe at another contract address. Its approved zero-value
deployment and nonpayable trigger call finalized on 2026-10-11; independent
inspection of the relay parent, external probe child, source and state is in
[`docs/evidence/cross-contract-relay-2026-10-11.json`](../docs/evidence/cross-contract-relay-2026-10-11.json).
It does not alter RuleVault, GapJudge, or either funded challenge.

`DirectGapJudgeWorkloadProbe.py` is the next isolated differential. It reads a
frozen review from a configured RuleVault and runs the production-sized
GapJudge assessment from a wallet-submitted transaction. Its
`adjudicate_fixture` entry point exists only for local Direct Mode because the
Direct Mode runner has no cross-contract view backend. The probe has no payout
path and never writes to the production vault. Its deployment and live
adjudication require explicit approval after the local tests pass.

These diagnostics are excluded from the production release. The probe and
relay records, including the sequential probe controls and authenticated relay
ancestry, are recorded in [`docs/ADJUDICATION_PROBE_2026-10-11.md`](../docs/ADJUDICATION_PROBE_2026-10-11.md).
The relay proves the generic finalized cross-contract boundary, while the
production GapJudge workload and authenticated RuleVault callback remain
separate questions.
