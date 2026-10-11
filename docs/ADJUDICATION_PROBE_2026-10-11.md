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

The current Studionet worker can finalize a direct nondeterministic judgment and the same judgment in a self-triggered finalized child. The prior GapJudge failures therefore are not explained by a universal inability to execute nondeterminism or finalized messages. This probe alone does not isolate the RuleVault → GapJudge cross-contract boundary, the production policy payload, or authenticated callback handling. The separately approved relay reproduction below covers the generic finalized cross-contract message and leaves the production workload as the remaining differential. No production contract was redeployed and the two funded challenges were not touched.

## Cross-contract relay reproduction

The separately approved zero-value relay deployment used the same Studionet
61999 stack and targeted this already deployed probe. The relay source SHA-256
is `9a17de4e4bf58e8140abd64408552e15b952ede8bb2b3469f35d692ca6dab8cd`, and
the deployed source matched it exactly. The deployment [0xfa7659a2b83b835bbd1ba1ccee2db8d376d5852cba913e6f142a99c341819907](https://explorer-studio.genlayer.com/tx/0xfa7659a2b83b835bbd1ba1ccee2db8d376d5852cba913e6f142a99c341819907)
finalized with successful leader execution and `MAJORITY_AGREE`; the relay
address is `0x212b27001161A981D0E9d7c1669E3B9dBfA21881`.

Using the same fixed harmless prompt, the relay parent [0x92abae96d5f48dca6556360c234adf3e99b74a61dd77972597fa37b98e0d7796](https://explorer-studio.genlayer.com/tx/0x92abae96d5f48dca6556360c234adf3e99b74a61dd77972597fa37b98e0d7796)
finalized with successful leader execution and five agreeing validator votes.
Its finalized zero-value message targeted the probe and produced child
[0x15b76a2144d2e30123214d7e5c13bda570d73b2299eac5c536386642e0e393f1](https://explorer-studio.genlayer.com/tx/0x15b76a2144d2e30123214d7e5c13bda570d73b2299eac5c536386642e0e393f1).
The child finalized with `MAJORITY_AGREE`, successful leader execution and
three agreeing/two idle validator votes. Its authenticated ancestry is
`from=0x212b27001161A981D0E9d7c1669E3B9dBfA21881`,
`to=0xF1a8f257954204bedc1bce57B8C498c9f9841889`, and
`triggered_by=0x92abae96d5f48dca6556360c234adf3e99b74a61dd77972597fa37b98e0d7796`.
The relay state changed `request_count: 0 → 1`; the probe retained
`ping_count: 1` and recorded `last_result: {"label":"CONTROL"}`.

The complete raw deployment, parent, child, schema, source correspondence,
state readbacks and unsupported RPC diagnostics are in
[`evidence/cross-contract-relay-2026-10-11.json`](evidence/cross-contract-relay-2026-10-11.json),
generated by [`scripts/inspect_cross_contract_relay.mjs`](../scripts/inspect_cross_contract_relay.mjs).
This rules out a generic failure of finalized cross-contract messages or
nondeterministic child execution on the current Studionet run. It does not
prove the production `GapJudge.adjudicate` workload or its authenticated
callback, which additionally performs substantive repeated LLM assessment,
frozen-evidence validation and a callback to RuleVault. No production source,
deployment or funded challenge was changed.
