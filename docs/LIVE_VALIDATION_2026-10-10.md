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
