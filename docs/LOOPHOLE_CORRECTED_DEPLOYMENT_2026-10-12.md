# LOOPHOLE corrected deployment — 2026-10-12

The approved zero-value deployment of the corrected single-contract release used
the repository-local GenLayer CLI `0.39.1`, the active `praest-deployer` wallet,
and Studionet chain `61999`. The production source was not changed after this
deployment.

- Contract: [`0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`](https://explorer-studio.genlayer.com/address/0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e)
- Deployment transaction: [`0xf27efe23174de8d46ace87bade177ebeb653d2a7a13c8f398bcfccfceb4dd1c3`](https://explorer-studio.genlayer.com/tx/0xf27efe23174de8d46ace87bade177ebeb653d2a7a13c8f398bcfccfceb4dd1c3)
- Value attached: `0 GEN`
- Finality: `FINALIZED`
- EVM receipt: `0x1`
- GenVM leader execution: `SUCCESS`
- Consensus result: `MAJORITY_AGREE`
- Validator votes: five `AGREE` votes in one round
- Constructor: parameterless
- Public schema: 19 methods, including direct `adjudicate_review`, reads,
  commit/reveal, recovery, appeal and withdrawal

The repository source is 28,740 bytes with SHA-256
`f173b087336403044db3ce793c2c0df57e5104b5078964b2ce8b8b7e88ccf8c7`. The
independent release gate decoded both `gen_getContractCode` and the submitted
deployment `contract_code` from base64 and found an exact byte match to
`contracts/Loophole.py`. The complete compact record is
[`docs/evidence/loophole-corrected-deployment-2026-10-12.json`](evidence/loophole-corrected-deployment-2026-10-12.json),
and the reusable check is
[`scripts/verify_contract_deployment.mjs`](../scripts/verify_contract_deployment.mjs).

The initial `get_config` readback proved `chain=61999`,
`adjudication_mode=DIRECT_ATOMIC`, `commitment_encoding=length-prefixed-utf8-v1`
and zero challenges, attempts, adjudications, withdrawals, credit and locked
GEN. No historical escrow was migrated.

The earlier monolith deployment at
[`0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf`](https://explorer-studio.genlayer.com/address/0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf)
and the original RuleVault/GapJudge pair remain preserved historical
deployments. Existing funds and challenges on those addresses were not touched.

This record proves deployment finality, execution, schema and source
correspondence. A funded challenge, adjudication, entitlement and withdrawal
against this corrected address remain a separate live verification step.
