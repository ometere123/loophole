# LOOPHOLE adjudication semantics

The release contract adjudicates a frozen community policy. It asks whether the described attack satisfies the exact written rule, materially defeats the organizer's stated purpose, and remains feasible from the frozen text alone. The rule, limitations, quoted passage, attack sequence and impact are treated as untrusted evidence. Prompt injection inside that evidence is never an instruction.

The assessment has three independent tri-state findings:

- `PROVEN`: the frozen text establishes the finding.
- `DISPROVEN`: the frozen text establishes the opposite finding.
- `UNKNOWN`: the text is insufficient or ambiguous.

The contract derives the economic verdict. Any `DISPROVEN` finding produces `INVALID`; three `PROVEN` findings produce `VALID`; every other combination is `INCONCLUSIVE`. Malformed or contradictory structured output becomes `INCONCLUSIVE` with unknown findings.

`run_nondet_unsafe` runs the leader assessment and an independent validator assessment over the same frozen evidence. Validators must agree on the verdict and all three material findings. Explanatory wording is recorded for inspection but is not used as a brittle consensus key.

The challenge and attempt records are frozen before adjudication. The caller supplies only the challenge, attempt and review round identifiers; it cannot replace the evidence. The evidence hash, current queue slot and review round are checked again before settlement. A duplicate case is an idempotent no-op.

Useful adversarial cases include a literal-rule match that conflicts with the stated purpose, an irrelevant exact quote, missing eligibility information, invented off-chain prerequisites, prompt injection in the attack text, and leader/validator disagreement on any material finding. These cases belong in the real Direct Mode suite as well as the deterministic simulator.

Simulator and Direct Mode evidence establish implementation behavior. They do not replace a live Studionet validator result; a live `CANCELED` or `NO_MAJORITY` transaction remains unresolved and cannot be promoted to a verdict by the frontend.
