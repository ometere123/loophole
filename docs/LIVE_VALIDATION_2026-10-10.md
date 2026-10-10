# Studionet 61999 live validation

This record contains only transactions observed on the canonical deployment. It does not treat a finalized transaction as successful execution without checking the execution result, and it does not treat a parent transaction as proof of a child transfer.

## Deployment

- Network: Studionet 61999 (`0xF22F`)
- RuleVault: `0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26`
- GapJudge: `0xb14B08cd35Fa64FE795e14931DdA09999627785d`
- Organizer A: `0xfcef676044658b5402f590dabe9e04a0f640522f`
- Challenger B: `0x81301DD9C3605a7DA743D87b803156d8445620B0`

## Challenge 1: explicit educational limitation

Challenge 1 was funded by [create_challenge](https://explorer-studio.genlayer.com/tx/0x4261d505a6967b2a17ae0e3afc4388aa1d196dea88c0077df32fcabe9bb3a17d). The commitment, reveal, and `start_review` transactions finalized with successful execution. The triggered judge child [0x720e15de26aa4eb6f34fe67a79e684fd0286b4f09c87df283070bdd33c0a5ed4](https://explorer-studio.genlayer.com/tx/0x720e15de26aa4eb6f34fe67a79e684fd0286b4f09c87df283070bdd33c0a5ed4) finalized `CANCELED` with `NO_MAJORITY`; its leader output was a coherent `INVALID` proposal, but no authenticated callback was emitted. RuleVault remained in `REVIEWING` with zero credit.

## Challenge 2: literal rule intentionally omits the content condition

Challenge 2 was funded by [create_challenge](https://explorer-studio.genlayer.com/tx/0x82e84cf93d398ea3c24680bb56785c2bbf3f68b2e1ae8c3794908ca1cabd1251). It used a `0.01 GEN` bounty, a `0.01 GEN` challenger bond, a seven day window, and the exact rule:

> A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.

The commitment transaction was [0xe6ad5b183f77a318ae500e44dd724bf9d8bc146fc235f68d3ac8cf671e0e8d1f](https://explorer-studio.genlayer.com/tx/0xe6ad5b183f77a318ae500e44dd724bf9d8bc146fc235f68d3ac8cf671e0e8d1f) as shown by the explorer account history. The complete reveal transaction was [0x0aab324768dec10413c1fe1cdcada525135d05fc156e090572b18ecd59b0faad](https://explorer-studio.genlayer.com/tx/0x0aab324768dec10413c1fe1cdcada525135d05fc156e090572b18ecd59b0faad), finalized with `SUCCESS`, `MAJORITY_AGREE`, five agreeing votes, and `value_credited: false` as expected for a zero-value reveal.

The `start_review` parent was [0x8a0a5642cc438611fa6e3cb09892ef6e33c18642be4b98f11281b3305d346839](https://explorer-studio.genlayer.com/tx/0x8a0a5642cc438611fa6e3cb09892ef6e33c18642be4b98f11281b3305d346839). It finalized with successful execution and emitted the authenticated child request [0x215ca59b238d77e53a7bbb6b9aa71b4227e77afa8b8539f973806965acc44ef4](https://explorer-studio.genlayer.com/tx/0x215ca59b238d77e53a7bbb6b9aa71b4227e77afa8b8539f973806965acc44ef4) to GapJudge.

The judge child was independently inspected through the Studionet RPC. The leader GenVM execution succeeded and proposed `INVALID`, with the explanation that the attack satisfied the literal hashtag and word count but failed the stated educational goal. The child then finalized `CANCELED` with `NO_MAJORITY`, zero validator votes, and no triggered callback. This is a real platform execution result, not a simulated verdict. RuleVault state after finalization was:

```text
challenge 2: OPEN
attempt 2: REVIEWING
active_round: 1
total_credit_wei: 0
withdrawal_count: 0
```

No entitlement or withdrawal was created, so there is no legitimate withdrawal parent or child transfer to verify for this run. The conservative contract behavior correctly prevented payout when validator consensus was not authenticated.

## Interpretation

Two independent live review attempts reached the same triggered-consensus failure shape: a successful leader proposal followed by a canceled child with `NO_MAJORITY` and no callback. This blocks a claim of a complete funded economic lifecycle on this Studionet run. It also shows that a leader proposal cannot safely be promoted to a verdict by the frontend or by an off-chain observer. The repository keeps the challenge frozen for the configured review timeout and does not retry, restore credit, or fabricate delivery evidence.

## Receipt comparison and trace limitation

The raw `eth_getTransactionByHash` receipts were compared with the successful funding and reveal transactions:

| Transaction | Status / result | Leader execution | Votes | Value | Gas used | Trigger |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `0x4261d505…9bb3a17d` create challenge 1 | `FINALIZED / MAJORITY_AGREE` | `SUCCESS` | 3 agree, 2 idle | `0.01 GEN` | 0 | user transaction |
| `0x0aab3247…b0faad` reveal attempt 2 | `FINALIZED / MAJORITY_AGREE` | `SUCCESS` | 5 agree | 0 | 0 | user transaction |
| `0x720e15de…c0a5ed4` judge child 1 | `CANCELED / NO_MAJORITY` | `SUCCESS` | empty | 0 | 0 | `0xe9c85b52…e93c5306` |
| `0x215ca59b…cc44ef4` judge child 2 | `CANCELED / NO_MAJORITY` | `SUCCESS` | empty | 0 | 0 | `0x8a0a5642…5d346839` |

The child receipts contain no validator receipts, no validator vote hashes, no triggered callback, and `value_credited: false`. The RPC exposes `gaslimit` values of `0` and `1` for the two children and `gas_used: 0`; it exposes no separate fee deduction field for these gasless Studionet calls. Calling `gen_dbg_traceTransaction` for either child returns JSON-RPC `-32601 Method not found: gen_dbg_traceTransaction`. Validator-level execution traces therefore cannot be retrieved from the public Studionet RPC; the committed receipt fields are the authoritative available evidence.

## Semantic review of the second leader proposal

Challenge 2 froze the goal “Reward members who publish an original educational post that explains a topic clearly and helps readers learn,” the literal rule requiring `#OurCampaign` and at least 100 words, and the sole limitation “Posts must be newly written by the member.” The scenario describes a newly written 100-word repeated sentence containing the hashtag. Under the frozen text, the literal finding should be `letter: true`; the scenario is feasible as stated; and the claimed purpose harm is plausible because the literal conditions omit educational content. The leader’s encoded explanation says the attack satisfies the literal rule but returned `letter: false`, `purpose: false`, and `feasible: false`, which is internally inconsistent with the supplied facts. That is a leader proposal only: it was never authenticated by validator consensus and was correctly prevented from changing economic state.

The first challenge’s leader proposal was semantically different and internally coherent: its limitation expressly excluded meaningless repetition, so `INVALID` with a failed literal finding was reasonable. Both children nevertheless failed before any validator vote. The repeated empty-vote/canceled shape, contrasted with successful user transactions, is evidence of a triggered-consensus platform/runtime problem rather than proof that a RuleVault callback or payout guard is defective. No redeployment is justified by these receipts.

## Direct Mode resolver repair

Run `38075901285` failed before contract loading because the unauthenticated GitHub API request for the public GenVM release returned HTTP 403 `rate limit exceeded`. The resolver now accepts the Actions `github.token` through `GENVM_GITHUB_TOKEN`, authenticates both release metadata and asset download, selects the verified `genvm-runners-all.tar.xz` asset for `v0.3.0-rc7`, and requires matching version, asset name, published SHA-256 digest, published size, and recalculated local digest before cache reuse. The temporary download is verified before atomic replacement. Local Direct Mode passed 4/4 with the authenticated resolver, and CI run `38078856169` passed all contracts and frontend jobs.

## Follow-up adjudication isolation from commit 409f691

The complete raw probe output is committed at [`docs/evidence/studionet-adjudication-rpc-2026-10-10.json`](evidence/studionet-adjudication-rpc-2026-10-10.json), generated by [`scripts/inspect_adjudication.mjs`](../scripts/inspect_adjudication.mjs). It queried both failed children and their `start_review` parents through chain `0xf22f`.

The public RPC supports `eth_getTransactionReceipt` and `gen_getTransactionStatus`. The EVM receipt for each failed child reports `status: 0x1`, `gasUsed: 0x7a1200`, `effectiveGasPrice: 0x0`, and a finalized-message log. That is the transport envelope only. The GenLayer transaction record independently reports `CANCELED`, `NO_MAJORITY`, `max_recovery_cycles_exceeded`, leader `SUCCESS`, empty votes, zero validator assignments in the final record, and no callback child. The inspector deliberately records both values and does not interpret the EVM envelope as successful contract execution.

The following public methods were attempted and are unsupported on the hosted endpoint: `gen_getTransactionReceipt`, `gen_getConsensusData`, `gen_getTransactionFee`, `gen_getTransactionFees`, `gen_getTransactionData`, `gen_getTransactionAllData`, `gen_getTransactionExecution`, `gen_getTransactionLogs`, `gen_getTransactionHistory`, `gen_getTransactionLifecycle`, and `gen_dbg_traceTransaction`. Some later probes returned the endpoint's `-32029` rate-limit response; those responses are preserved as unavailable evidence rather than converted into empty traces. No public method exposed recovery-cycle history, validator scheduling, provider errors, or parent-child fee allocation.

The upstream Studio worker source was compared against the pinned application stack. Its current public implementation sets a default maximum of three recovery cycles, clears persisted consensus history when resetting a transaction, increments `recovery_count`, and cancels after the cap with `max_recovery_cycles_exceeded`. It also has separate retry paths for no validators and unclassifiable leader GenVM crashes. This explains why final empty votes cannot prove that no validator work occurred. It does not identify the hosted Studionet worker build, GenVM runner digest, LLM provider responses, or the exact reset cause; the hosted deployment does not expose those fields through its public RPC. The repository therefore does not claim a more specific root cause than “upstream worker/runtime recovery exhaustion during triggered consensus.”

The pinned local versions used for comparison are `genlayer-test 0.29.2`, `genvm-linter 0.11.0`, `genlayer-py 0.16.3`, repository-local CLI `genlayer 0.39.1`, and frontend `genlayer-js 1.1.8`. These versions are evidence of the client/test stack, not proof of the hosted backend version.

An isolated diagnostic contract is prepared under [`diagnostics/AdjudicationProbe.py`](../diagnostics/AdjudicationProbe.py). It compares a direct `run_nondet_unsafe` judgment, the identical judgment scheduled with `emit(on='finalized')`, and a deterministic finalized child ping. It is separate from RuleVault and GapJudge and passes Python compilation plus GenVM lint. It has not been deployed or invoked: the next Studionet write requires explicit approval and must be recorded with its deployment, parent, and child hashes before proceeding.

The challenge 2 leader proposal remains unauthenticated. Its text says the literal rule and word count were satisfied while encoding `letter: false`, `purpose: false`, and `feasible: false`; that is internally inconsistent with the frozen evidence. GapJudge's validator path already re-executes the full substantive assessment and requires exact agreement on verdict and all three material findings, while RuleVault rejects a `VALID` result with a false finding. No production source change or redeployment is justified by this unauthenticated proposal, and the two funded challenges remain frozen under the five-day stalled-review protection.

## Approved diagnostic deployment gate

The approved zero-value deployment attempt for [`diagnostics/AdjudicationProbe.py`](../diagnostics/AdjudicationProbe.py) was [0x59704b14f04d1b18f618e4ab9f76f4e52597eb23fd0963ba66e4250b2212b3bc](https://explorer-studio.genlayer.com/tx/0x59704b14f04d1b18f618e4ab9f76f4e52597eb23fd0963ba66e4250b2212b3bc). It finalized with `MAJORITY_AGREE`, but the leader execution result was `ERROR` with `contract_error / invalid_contract`; the derived address `0xFeA1FD981b420c797C4f87aA54C1995fe87547e3` has no public schema or code. The complete receipt probe is [`adjudication-probe-deployment-rpc-2026-10-10.json`](evidence/adjudication-probe-deployment-rpc-2026-10-10.json).

The probe sequence was stopped before `trigger_ping`, `direct_judgment`, or `trigger_judgment`. No additional transaction was submitted, and no production contract or funded challenge was changed. The local semantic validator additionally reported `E101` because the pinned `py-genlayer` artifact is absent from the local linter cache; AST lint passed three checks. A corrected diagnostic deployment requires a demonstrated source-level explanation for the `invalid_contract` result and fresh approval before another Studionet write.

## Corrected diagnostic source validation

The diagnostic `Depends` declaration now occupies line 1, followed by the imports and then descriptive comments. The before/after source bytes and complete RPC responses are in [`adjudication-probe-schema-2026-10-10.json`](evidence/adjudication-probe-schema-2026-10-10.json).

`gen_getContractSchemaForCode` rejected the original 2,056-byte source with `VM_ERROR: invalid_contract`. The actual GenVM log was `runner comment does not start with version, using default v0.1.0`, proving that the descriptive comment preceding `Depends` changed runner selection. The corrected 2,057-byte source returned a schema with a zero-argument constructor and six public methods: `trigger_ping`, `child_ping`, `direct_judgment`, `trigger_judgment`, `child_judgment`, and read-only `get_state`.

The failed deployment transaction contained the exact original source bytes. [`adjudication-probe-submitted-source-2026-10-10.json`](evidence/adjudication-probe-submitted-source-2026-10-10.json) records an exact byte match at offset 237 and SHA-256 `690c94f299915de02e5b0de604df03bb672d5980063c41aa1f2fd48616da48b3`.

The local semantic validator now succeeds when explicitly pinned to `GENVM_VERSION=v0.3.0-rc7`: `Validation passed; Contract: AdjudicationProbe; Methods: 6 (1 view, 5 write); ctor_params: 0`. The previous `E101` came from automatic selection of a cached manager bundle that did not contain the pinned `py-genlayer` hash. The corrected source passes GenVM lint, SDK validation, compilation, runner-header validation, and the dedicated Direct Mode test. CI now runs all of these diagnostic checks.
