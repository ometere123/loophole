# LOOPHOLE monolith deployment — 2026-10-12

The one approved zero-value deployment used the repository-local GenLayer CLI
0.39.1, the active `praest-deployer` wallet and Studionet chain 61999. The
deployment transaction finalized with GenVM `SUCCESS` and `MAJORITY_AGREE`.

- Contract: [`0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf`](https://explorer-studio.genlayer.com/address/0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf)
- Deployment transaction: [`0x4ff23d2092cd920f535590e9aadf9bc5571934ab24d8aac56fae0ef3dc5947b9`](https://explorer-studio.genlayer.com/tx/0x4ff23d2092cd920f535590e9aadf9bc5571934ab24d8aac56fae0ef3dc5947b9)
- Value attached: `0 GEN`
- Final receipt: `FINALIZED`, result `6`, leader execution `SUCCESS`
- Validator round: `AGREE, AGREE, IDLE, AGREE, IDLE`; the idle entries were cancelled after quorum, as shown by the receipt
- `get_config`: `contract=Loophole`, `chain=61999`, `adjudication_mode=DIRECT_ATOMIC`, all counters zero
- Repository and RPC source: exact 28,363-byte match, SHA-256 `eea9c1252a08822694be4cbcf38a946387364e05f53b4063adb8ccd537b17500`

The complete public RPC transaction record, including the base64 contract code,
consensus fields and unsupported-method diagnostics, is in
[`docs/evidence/loophole-deployment-2026-10-12.json`](evidence/loophole-deployment-2026-10-12.json).
The historical RuleVault and GapJudge deployments remain unchanged and are not
used as the source of state for this new contract.

The deployment proves source correspondence and deployment execution only. No
funded challenge, adjudication, entitlement or withdrawal has yet been claimed
for this address.
