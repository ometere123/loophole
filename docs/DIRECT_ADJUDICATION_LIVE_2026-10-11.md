> **Historical superseded record.** This document records the earlier isolated
> direct-workload experiment and its diagnostic purpose. It is not the current
> production deployment or live economic result. The corrected single-contract
> release and its successful funded lifecycle are documented in
> [`LOOPHOLE corrected deployment live lifecycle — 2026-10-12`](LOOPHOLE_CORRECTED_LIVE_LIFECYCLE_2026-10-12.md).

# Live direct workload probe: terminal result

This is the single approved live diagnostic experiment. It used no payable
value, did not call RuleVault or GapJudge writes, did not issue a callback, and
did not touch either funded challenge.

The corrected probe was deployed at
`0xA47Ad90A32C15f78Fab58e4bDD9C229b665518c0` with the canonical RuleVault
`0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26`.

- deployment: [0x50d3dd5db8da2865cfdbe31c355691522a40526ae6d97b6050b0685e7d39357f](https://explorer-studio.genlayer.com/tx/0x50d3dd5db8da2865cfdbe31c355691522a40526ae6d97b6050b0685e7d39357f)
- adjudication: [0x7e43707eabdd13edf592f449bbb023003fffd95b9d106c0188bdb2533eac5505](https://explorer-studio.genlayer.com/tx/0x7e43707eabdd13edf592f449bbb023003fffd95b9d106c0188bdb2533eac5505)
- network: Studionet 61999 (`0xf22f`)
- deployed source SHA-256: `5fe71486454a38d9e74e29e6104624311b0f4826bc95f337fb344a236aa23fb4`
- repository source SHA-256: `5fe71486454a38d9e74e29e6104624311b0f4826bc95f337fb344a236aa23fb4`
- schema: constructor `vault_address`; write `adjudicate_frozen_review`; views `get_case` and `get_configuration`
- configuration readback: the canonical RuleVault and `total_cases=0`

The adjudication call was exactly `adjudicate_frozen_review(2, 2, 1)` and
finalized with `value=0`, leader GenVM `SUCCESS`, four completed consensus
rounds, and terminal result `MAJORITY_DISAGREE`. The final round contained two
agree votes and three disagree votes. The final leader proposal was
`INVALID` with `letter=true`, `purpose=false`, and `feasible=true`; it was not
accepted as a contract verdict because validators did not reach equivalence.

The validators did execute the cross-contract reads and substantive prompt:
the successful validator records have `execution_result=SUCCESS`, nonzero
processing times, and RuleVault storage reads in their execution statistics.
There was no `max_recovery_cycles_exceeded` error in this probe. The diagnostic
case readback is empty and `total_cases` remains zero, which is the expected
rollback after consensus disagreement. No triggered child exists because this
diagnostic path is a direct wallet call and has no callback.

The complete RPC transaction, receipt, consensus history, validator execution
records, state readbacks, and unsupported-method classifications are preserved
in:

- [`docs/evidence/direct-workload-probe-deployment-2026-10-11.json`](evidence/direct-workload-probe-deployment-2026-10-11.json)
- [`docs/evidence/direct-workload-probe-adjudication-2026-10-11.json`](evidence/direct-workload-probe-adjudication-2026-10-11.json)

The result rules out a failure of the finalized cross-contract view boundary
for this workload. It also shows that direct submission is not yet a working
production workaround: the full LOOPHOLE workload is executable, but the
hosted validator set does not agree on the economically material assessment.
The earlier child transactions exhausted worker recovery; this direct probe
exhausted consensus through repeated model disagreement instead. No production
architecture change or redeployment is justified by this experiment alone.

The precise next dependency is a GenLayer maintainer investigation of the
hosted consensus/equivalence behavior for this prompt and validator mix,
including why materially different `VALID`, `INVALID`, and `INCONCLUSIVE`
outputs are produced from the same frozen evidence. A production direct path
must remain blocked until an independently justified prompt/workload or
runtime correction produces a finalized majority result without weakening the
three substantive validator checks.
