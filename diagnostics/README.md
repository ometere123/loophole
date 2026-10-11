# Studionet adjudication differential probe

`AdjudicationProbe.py` is a diagnostic contract kept separate from the two LOOPHOLE production contracts. It is designed to isolate three paths with the same pinned GenLayer SDK and network:

1. `direct_judgment(prompt)` executes a small `run_nondet_unsafe` judgment in the user submitted transaction.
2. `trigger_judgment(prompt)` schedules the identical judgment through `emit(on='finalized')`.
3. `trigger_ping()` schedules a deterministic finalized child without LLM execution.

The probe is excluded from the production release. Its one approved zero-value deployment and the sequential `trigger_ping`, `direct_judgment`, and `trigger_judgment` runs are recorded in [`docs/ADJUDICATION_PROBE_2026-10-11.md`](../docs/ADJUDICATION_PROBE_2026-10-11.md). Any additional Studionet write, including a separate cross-contract reproduction, requires explicit approval. Use the smallest available transaction settings and wait for every result before submitting the next operation.
