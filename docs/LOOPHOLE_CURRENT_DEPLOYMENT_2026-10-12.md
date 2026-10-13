# LOOPHOLE previous deployment — 2026-10-12

This record is retained as historical evidence for the 2026-10-12 monolith.
It was superseded by the source-verified release deployment recorded in
[`LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md`](LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md).

The approved one-time zero-value deployment of the corrected single-contract
release finalized on Studionet 61999 using repository-local GenLayer CLI
`0.39.1` and the active `party_b` wallet. No production contract other than
this new monolith was deployed, and no funded challenge was modified.

- Contract: [`0xec98AFC80bda4b664F20d782aA8a0bd49e436233`](https://explorer-studio.genlayer.com/address/0xec98AFC80bda4b664F20d782aA8a0bd49e436233)
- Deployment transaction: [`0xc5a5dee6cbbb2f081a37adefcb060061abe306044a46c17c2587f18577bda2d1`](https://explorer-studio.genlayer.com/tx/0xc5a5dee6cbbb2f081a37adefcb060061abe306044a46c17c2587f18577bda2d1)
- Chain ID: `61999` (`0xf22f`)
- Value attached: `0 GEN`
- Finality: `FINALIZED`
- EVM receipt: `0x1`
- GenVM leader execution: `SUCCESS`
- Consensus result: `MAJORITY_AGREE`
- Validator votes: three `AGREE` votes and two idle after quorum in one round
- Constructor: parameterless
- Public schema: 19 methods, including direct `adjudicate_review`, reads,
  commit/reveal, recovery, appeal and withdrawal

The repository source and the deployed `gen_getContractCode` are both 30,059
bytes with SHA-256
`940446781007701148449db3316f8b0c0e6b04ee84a8de405f78d5789bc1dae1`.
The submitted deployment `contract_code` has the same byte count and digest.
The reusable exact-source and schema check is
[`scripts/verify_contract_deployment.mjs`](../scripts/verify_contract_deployment.mjs),
and the compact evidence record is
[`docs/evidence/loophole-current-deployment-2026-10-12.json`](evidence/loophole-current-deployment-2026-10-12.json).

The initial `get_config` readback proved `chain=61999`,
`adjudication_mode=DIRECT_ATOMIC`, `commitment_encoding=length-prefixed-utf8-v1`
and zero challenges, attempts, adjudications, withdrawals, credit and locked
GEN. No historical escrow was migrated.

The earlier monolith deployment at
[`0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`](https://explorer-studio.genlayer.com/address/0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e),
the previous monolith, and the original RuleVault/GapJudge pair remain
preserved historical deployments. Existing funds and challenges on those
addresses were not touched. The earlier deployment evidence remains in
[`docs/LOOPHOLE_CORRECTED_DEPLOYMENT_2026-10-12.md`](LOOPHOLE_CORRECTED_DEPLOYMENT_2026-10-12.md)
and its evidence JSON.

This deployment is ready for a new funded lifecycle only after the frontend
binding is updated and independently verified against this address.
