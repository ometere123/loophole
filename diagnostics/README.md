# Studionet adjudication differential probe

`AdjudicationProbe.py` is a diagnostic contract kept separate from the two LOOPHOLE production contracts. It is designed to isolate three paths with the same pinned GenLayer SDK and network:

1. `direct_judgment(prompt)` executes a small `run_nondet_unsafe` judgment in the user submitted transaction.
2. `trigger_judgment(prompt)` schedules the identical judgment through `emit(on='finalized')`.
3. `trigger_ping()` schedules a deterministic finalized child without LLM execution.

The probe must not be deployed or invoked as part of the production release. Before any additional Studionet write, obtain explicit approval and record the deployment, parent and child hashes. Use the smallest available transaction settings and wait for every result before submitting the next operation.
