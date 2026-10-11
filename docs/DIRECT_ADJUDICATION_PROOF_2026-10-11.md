# Direct adjudication differential: offline proof

This record covers the first step of the proposed architecture correction. It
does not claim a live Studionet result and it does not authorize deployment or
paid testing.

## Workload

The test uses the exact frozen challenge #2 policy and attempt data recorded in
the failed child transaction `0x215ca59b238d77e53a7bbb6b9aa71b4227e77afa8b8539f973806965acc44ef4`:

- goal: reward an original educational post that explains a topic clearly;
- rule: a member earns points for `#OurCampaign` and at least 100 words;
- limitation: posts must be newly written;
- scenario: a newly written 100-word repeated sentence includes the hashtag but
  provides no educational value;
- impact: the measurable conditions can be met while the stated purpose is
  defeated.

The test recomputes the same sorted compact JSON SHA-256 evidence binding used
by `contracts/GapJudge.py`. It executes the unchanged production assessment
prompt and output normalization, including the three material findings:
`letter`, `purpose`, and `feasible`.

## Results

With the repository-local stack (`genlayer-test==0.29.2`,
`genlayer-py==0.16.3`, `genvm-linter==0.11.0`, CLI `0.39.1`, and GenVM
`v0.3.0-rc7`), the following tests passed in Direct Mode:

```text
python -m pytest -q tests/direct -m direct
9 passed
```

The new tests prove three separate properties:

1. A contradictory `VALID` response with `letter=false` is normalized to
   `INCONCLUSIVE` and cannot become a payable positive ruling.
2. A validator that independently changes the material `purpose` finding does
   not agree with the leader result.
3. The isolated direct workload probe executes the same full-sized assessment
   and captured validator path.

The probe source also passed the actual semantic linter and SDK validation:

```text
GENVM_VERSION=v0.3.0-rc7 genvm-lint check diagnostics/DirectGapJudgeWorkloadProbe.py
Lint passed (3 checks)
Validation passed
Contract: DirectGapJudgeWorkloadProbe
Methods: 4 (2 view, 2 write)
```

## What this establishes

The failed production children are not explained by an inability of the local
GenVM stack to parse or execute the production-sized assessment. The result is
also not accepted merely because JSON fields have the expected shape: the
validator path reruns the substantive assessment and rejects a changed
material finding.

The isolated probe's live entry point, `adjudicate_frozen_review`, reads
`get_challenge` and `get_attempt` from a configured RuleVault, verifies the
active attempt and review round, reconstructs the frozen evidence object, and
recomputes its hash before invoking consensus. It records the result in the
probe only. It has no callback or payout mechanism and must not be treated as a
production deployment.

## Reference design observations

The inspected reference implementations use the same useful separation of
concerns without being copied into LOOPHOLE:

- Cantrap keeps custody in a separate vault while its arena performs direct
  nondeterministic attack testing and validates material result fields.
- Crux and Reprove replay substantive fields independently before accepting a
  result and send only finalized callbacks to the consumer.
- StewardRail exposes a direct wallet-submitted `adjudicate` path after the
  deterministic evidence gate, then emits a finalized settlement message.
- Vowmark records review attempts and settlement state separately, with
  cooldown/capacity controls and retry reconciliation.

These observations support testing a direct GapJudge transaction, but they do
not by themselves prove that the Studionet worker will finalize the full
LOOPHOLE workload. That requires one separately approved, zero-value live
probe call against the current hosted runtime.
