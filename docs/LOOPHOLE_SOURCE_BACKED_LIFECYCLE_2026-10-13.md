# LOOPHOLE source-backed lifecycle — 2026-10-13

This is the first source-backed lifecycle on the source-verified monolith at [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E) on Studionet 61999, preserved as a historical point-in-time record. The organizer was `0xfcef676044658B5402f590daBe9E04A0F640522f`; the challenger was `0x81301DD9C3605a7DA743D87b803156d8445620B0`. Its `INVALID_PENDING` state predates the later appeal sequence; see [`docs/LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md`](LOOPHOLE_APPEAL_PREPARATION_2026-10-14.md) for current consolidated evidence.

## Transactions

- Create and fund challenge 1: [`0x6ee013890085bb4b2bd86bbaeeec495e07d6472ab532416ba43e3e539e5e6e5f`](https://explorer-studio.genlayer.com/tx/0x6ee013890085bb4b2bd86bbaeeec495e07d6472ab532416ba43e3e539e5e6e5f)
- First commitment with an incorrect evidence digest: [`0xc5ab9b108e496c0dad6adb2786b7128e507c0c8c305695321eb6a4c5643ecc38`](https://explorer-studio.genlayer.com/tx/0xc5ab9b108e496c0dad6adb2786b7128e507c0c8c305695321eb6a4c5643ecc38)
- First reveal: [`0x1b0487045d2efd930a0d4816b07b91182a5e6fd1e43dcc250f2ea422e4348fdb`](https://explorer-studio.genlayer.com/tx/0x1b0487045d2efd930a0d4816b07b91182a5e6fd1e43dcc250f2ea422e4348fdb)
- First adjudication, fail-closed `INCONCLUSIVE`: [`0x4b0cafe6bf3fa2877b6154086d89046b4551e8200563e101f0d1b2f9025a262b`](https://explorer-studio.genlayer.com/tx/0x4b0cafe6bf3fa2877b6154086d89046b4551e8200563e101f0d1b2f9025a262b)
- Corrected commitment: [`0x8994cb8b3db648e05499ee4b6fa195ee66fcba2bc8d6b9a7d229eb50eb82f172`](https://explorer-studio.genlayer.com/tx/0x8994cb8b3db648e05499ee4b6fa195ee66fcba2bc8d6b9a7d229eb50eb82f172)
- Corrected reveal: [`0x519354b216305b7a5058c5020098299e147936224d28c57e9b3854330c25cade`](https://explorer-studio.genlayer.com/tx/0x519354b216305b7a5058c5020098299e147936224d28c57e9b3854330c25cade)
- Freeze review: [`0x7ecb425167afd6db0690dd7524fbea7da895d8ba46994cd79121b8f552d36ab6`](https://explorer-studio.genlayer.com/tx/0x7ecb425167afd6db0690dd7524fbea7da895d8ba46994cd79121b8f552d36ab6)
- Direct adjudication: [`0x95791361e5593505c7aedcc58f6404055a58b75c65a64df967412977674513d0`](https://explorer-studio.genlayer.com/tx/0x95791361e5593505c7aedcc58f6404055a58b75c65a64df967412977674513d0)

Every listed transaction finalized with successful GenVM execution. The final adjudication reached `MAJORITY_AGREE`; its validator vote names were `AGREE`, `DISAGREE`, `AGREE`, `IDLE`, `AGREE`. The leader and three validators agreed on the complete decision-critical output, one validator disagreed, and one validator was idle after quorum. The leader output was:

```json
{"evidence_state":"VERIFIED","feasible":"PROVEN","letter":"PROVEN","purpose":"DISPROVEN","reason":"Attack fulfills rule+limitations with new post+explanation; does not defeat goal of rewarding genuine new contributions.","verdict":"INVALID"}
```

The claimant evidence was pinned to `https://raw.githubusercontent.com/ometere123/loophole/37822b9333e064e632896a8318f2fee5bb4dd1cd/docs/evidence/source-backed-evidence-2026-10-13.md` with UTF-8 SHA-256 `31afc81b0bb761015d43e3215540bcbf8ef2e334d31c5066f0f2367818a053f5`. The final `get_attempt(2)` readback reported `evidence_state=VERIFIED`, `feasible_state=PROVEN`, `letter_state=PROVEN`, `purpose_state=DISPROVEN`, and `verdict=INVALID`. The authenticated reason explains that the described action satisfies the literal rule and its limitation, so it does not defeat the educational purpose.

## Settlement and accounting

- `get_adjudication("1:2:2")`: verified evidence, proven feasibility, proven literal compliance, disproven purpose, `INVALID` verdict, atomic settlement.
- `get_challenge(1)`: `OPEN`, `active_attempt=0`, `active_round=2`, no winner.
- `get_attempt(2)`: `INVALID_PENDING`, `appeal_used=false`, appeal deadline `2026-10-14T18:38:05Z`.
- `get_config`: `total_credit_wei=10000000000000000`, `total_locked_wei=20000000000000000`, `withdrawal_count=0`, `adjudication_count=2`.

The first incorrect-digest attempt returned its bond through the earlier `INCONCLUSIVE` settlement. The corrected attempt has no winner or claimable payout: its bond and the bounty remain locked while the bounded appeal window is open. No withdrawal was submitted, and no payment is claimed from this negative case.

This live result demonstrates that authenticated source evidence changes the adjudication input and can produce a substantive, economically conservative `INVALID` outcome. It does not demonstrate appeal settlement or a payout for this case. The separate live `VALID` and `INCONCLUSIVE` records contain the previously verified native GEN delivery evidence.

The machine-readable record is [`docs/evidence/loophole-source-backed-lifecycle-2026-10-13.json`](evidence/loophole-source-backed-lifecycle-2026-10-13.json).

