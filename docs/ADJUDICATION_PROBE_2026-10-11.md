# Corrected diagnostic probe evidence

This is the isolated self-triggered control for the Studionet adjudication failures. It is separate from the two production contracts and uses no payable value.

## Environment and source

- Chain: Studionet `61999` (`0xF22F`)
- RPC: `https://studio.genlayer.com/api`
- Repository-local CLI: `genlayer 0.39.1`
- Probe address: `0xF1a8f257954204bedc1bce57B8C498c9f9841889`
- Corrected source SHA-256: `5c692d508d0bf412f22162581adc39b93bf449d62e51ce8cb427060001b12d01`
- Source correspondence: exact match in the signed deployment payload, 2,057 bytes at offset 237
- Schema: zero-argument constructor, `trigger_ping`, `child_ping`, `direct_judgment`, `trigger_judgment`, `child_judgment`, and read-only `get_state`

The deployment receipt finalized successfully with `MAJORITY_AGREE`; the leader execution result was `SUCCESS`. The full RPC record is [`evidence/adjudication-probe-deployment-2026-10-11.json`](evidence/adjudication-probe-deployment-2026-10-11.json), and source matching is [`evidence/adjudication-probe-source-2026-10-11.json`](evidence/adjudication-probe-source-2026-10-11.json).

## Sequential control results

The same harmless prompt was used for both judgment calls: `Return the fixed control label for this harmless diagnostic probe.` Each transaction was waited to `FINALIZED`, and execution result was checked independently of lifecycle status.

| Stage | Parent | Child | Result | State evidence |
| --- | --- | --- | --- | --- |
| Deterministic ping | [0x65c0…c557](https://explorer-studio.genlayer.com/tx/0x65c0a889a888d41d9ff160c20f976991a33ae88657919e19df2539968546c557) | [0x89ca…a8976](https://explorer-studio.genlayer.com/tx/0x89ca8c6dfb4fb4d34e89991c0e68b569a53f3525eb17e0d96de55b96391a8976) | Both finalized successfully; child `triggered_on: finalized` | `ping_count: 0 → 1` |
| Direct judgment | [0x6ba3…8004](https://explorer-studio.genlayer.com/tx/0x6ba3bacc795122acb6be070cafeb67b0203718d62084f3cb09e0e97289078004) | — | Finalized successfully; validator agreement; `{"label":"CONTROL"}` | `last_result: {"label":"CONTROL"}` |
| Triggered judgment | [0x040d…f2fa](https://explorer-studio.genlayer.com/tx/0x040d6346a1576d114ab1af662dac390316a70c9b2e14f278e46a0eb4cea8f2fa) | [0x54fd…5b8b6](https://explorer-studio.genlayer.com/tx/0x54fd07c0562d0e85ab8ea7ac91fbdb18bbfb7dfbe2789cf247b1ef887ce5b8b6) | Both finalized successfully; child `triggered_on: finalized`; validator agreement; `{"label":"CONTROL"}` | `last_result: {"label":"CONTROL"}` |

The raw parent and child inspection records are [`adjudication-probe-ping-2026-10-11.json`](evidence/adjudication-probe-ping-2026-10-11.json), [`adjudication-probe-direct-2026-10-11.json`](evidence/adjudication-probe-direct-2026-10-11.json) and [`adjudication-probe-triggered-2026-10-11.json`](evidence/adjudication-probe-triggered-2026-10-11.json). The RPC inspector records unsupported methods separately from rate limits and temporary failures.

## Conclusion and boundary

The current Studionet worker can finalize a direct nondeterministic judgment and the same judgment in a self-triggered finalized child. The prior GapJudge failures therefore are not explained by a universal inability to execute nondeterminism or finalized messages. This probe does not isolate the RuleVault → GapJudge cross-contract boundary, the production policy payload, or authenticated callback handling. No production contract was redeployed and the two funded challenges were not touched. A smallest cross-contract reproduction needs one separately approved diagnostic deployment before it can be run.
