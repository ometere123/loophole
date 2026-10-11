# Studionet triggered-consensus recovery reproduction

## Environment

- Chain: Studionet `61999` (`0xF22F`)
- RPC: `https://studio.genlayer.com/api`
- RuleVault: `0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26`
- GapJudge: `0xb14B08cd35Fa64FE795e14931DdA09999627785d`
- Client stack: CLI `0.39.1`, `genlayer-test 0.29.2`, `genvm-linter 0.11.0`, `genlayer-py 0.16.3`, frontend `genlayer-js 1.1.8`
- Contract SDK header: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

## Reproduction

Both attempts were funded, committed, revealed, and submitted for review through the canonical deployed contracts. Each `start_review` finalized successfully and emitted a GapJudge child. The two cases differ in their frozen policy and scenario, but both triggered the same failure shape.

| Case | `start_review` parent | GapJudge child | child created/observed | final GenLayer result |
| --- | --- | --- | --- | --- |
| 1 | `0xe9c85b521ed6e26980d4e821babed8a91947bb76d3a1ed87c9942085e93c5306` | `0x720e15de26aa4eb6f34fe67a79e684fd0286b4f09c87df283070bdd33c0a5ed4` | recorded by RPC | `CANCELED / NO_MAJORITY` |
| 2 | `0x8a0a5642cc438611fa6e3cb09892ef6e33c18642be4b98f11281b3305d346839` | `0x215ca59b238d77e53a7bbb6b9aa71b4227e77afa8b8539f973806965acc44ef4` | recorded by RPC | `CANCELED / NO_MAJORITY` |

For both children, `eth_getTransactionByHash` reports leader execution `SUCCESS`, `consensus_data.error = max_recovery_cycles_exceeded`, empty `votes`, no final validator list, `gas_used = 0`, and no triggered callback. `gen_getTransactionStatus` reports `CANCELED`. `eth_getTransactionReceipt` returns the same finalized transport envelope with `status = 0x1`, `effectiveGasPrice = 0x0`, and a GapJudge message log. The full raw results, including method errors, are in [`docs/evidence/studionet-adjudication-rpc-2026-10-10.json`](evidence/studionet-adjudication-rpc-2026-10-10.json).

## Request for maintainer diagnostics

Please correlate the two child hashes with worker logs and return, for each transaction:

1. worker claim and release timestamps, worker identity, and recovery count per reset;
2. consensus phase transitions and validator assignment snapshot;
3. GenVM runner version/digest, leader and validator execution errors, and timeout classification;
4. LLM provider/model availability and request failures, with secrets removed;
5. child-message admission/budget values and parent/child fee allocation;
6. whether the transaction was reset after a stale claim or worker restart;
7. the first causal failure before the final `max_recovery_cycles_exceeded` record.

The public RPC does not expose these fields. The repository does not infer them from empty final votes.

## Isolated control result

After the malformed runner header was corrected, one separately approved zero-value diagnostic deployment was run on the same Studionet stack. The probe address is `0xF1a8f257954204bedc1bce57B8C498c9f9841889`, with corrected-source SHA-256 `5c692d508d0bf412f22162581adc39b93bf449d62e51ce8cb427060001b12d01`. The deployment finalized with successful leader execution. The sequential control transactions all finalized successfully:

- deterministic finalized child: parent `0x65c0a889a888d41d9ff160c20f976991a33ae88657919e19df2539968546c557`, child `0x89ca8c6dfb4fb4d34e89991c0e68b569a53f3525eb17e0d96de55b96391a8976`, `ping_count` `0 → 1`;
- direct nondeterministic judgment: `0x6ba3bacc795122acb6be070cafeb67b0203718d62084f3cb09e0e97289078004`, validator agreement and `{"label":"CONTROL"}`;
- finalized-triggered nondeterministic judgment: parent `0x040d6346a1576d114ab1af662dac390316a70c9b2e14f278e46a0eb4cea8f2fa`, child `0x54fd07c0562d0e85ab8ea7ac91fbdb18bbfb7dfbe2789cf247b1ef887ce5b8b6`, validator agreement and `{"label":"CONTROL"}`.

The complete records are in [`docs/ADJUDICATION_PROBE_2026-10-11.md`](ADJUDICATION_PROBE_2026-10-11.md) and its linked JSON evidence. This rules out a universal Studionet failure for direct nondeterminism, finalized self-messages, and deterministic finalized children. It does not reproduce the RuleVault → GapJudge cross-contract message, so the remaining differential is the cross-contract boundary and/or the production adjudication payload. One additional zero-value cross-contract diagnostic deployment is the minimum next action; it must be separately approved before any new Studionet write.
