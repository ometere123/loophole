# LOOPHOLE release deployment — 2026-10-13

This is the source-verified deployment of the authenticated source-backed
release candidate on Studionet 61999. The historical RuleVault and GapJudge
deployments were not touched, and no challenge or escrow was migrated.

- Contract: [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E)
- Deployment transaction: [`0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960`](https://explorer-studio.genlayer.com/tx/0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960)
- Chain: Studionet `61999` (`0xf22f`)
- CLI: repository-local GenLayer `0.39.1`
- Deployer: active configured wallet `0x21892BbA93381D94037Fb4aaB01CAFbdf4453B56`
- Attached value: `0 GEN`
- Finality: `FINALIZED`
- EVM receipt: `0x1`
- GenVM execution: `SUCCESS`
- Consensus: `MAJORITY_AGREE`
- Validator votes: three `agree` votes; two validators became `idle` after quorum

The submitted `contract_code`, `gen_getContractCode` and repository source are
each 38,780 bytes with SHA-256:

`423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`

The verified public schema has 22 methods, including
`create_source_challenge`, `commit_source_attempt` and
`reveal_source_attempt`, and the parameterless constructor. The finalized
`get_config` readback reports `chain=61999`,
`adjudication_mode=DIRECT_ATOMIC`,
`validator_agreement=EXACT_TRISTATE_FINDINGS`, and
`source_modes=HYPOTHETICAL,PINNED_SOURCE` with zero challenges, attempts,
adjudications, withdrawals, credit and locked GEN.

The first deployment helper poll received an HTML gateway response after the
transaction was submitted. No retry or second deployment was made. A later
repository-local CLI receipt read and
[`verify_contract_deployment.mjs`](../scripts/verify_contract_deployment.mjs)
confirmed finality, GenVM success, exact source parity and the full schema.
