# Product acceptance & release matrix

| Area | Release-level evidence needed |
|---|---|
| Repository quality | exact source hash, pinned repo-local 0.39.1, clean CI |
| GenVM semantics | real GenVM lint and Direct Mode, model disagreement tests |
| Contract economic lifecycle | funded organizer → wallet A commit → reveal → serialized judge → finalized callback → EOA withdrawal |
| Payment delivery | external transfer child observed **successfully executed** and recipient balance changed |
| Frontend integration | direct live reads, true writes, reject wallet cancellation, wrong-network guard, account change, refresh persistence |
| UX | desktop/mobile fit, keyboard flows, readable pending/failed/accepted/finalized states, zero mock records |
| Adversarial | organizer self-attack, quote mismatch, collision attempt, forged judge, duplicate callback, stale round, expiry, repeated withdraw |
| Release | publish verified deployment manifest, explorer links and review-grade live walkthrough |

Current release evidence:

- Repository-local CLI `0.39.1`, SDK header pinned to the deployed contracts, and GenVM lint `0.11.0` validation pass with the official `v0.3.0-rc7` runner bundle (`genvm-runners-all.tar.xz`, SHA-256 `e218a1854214681560351051f76fe2b878545cf3409455ef372d57014a88ca67`).
- GenVM Direct Mode executes the actual contracts locally: 6 tests passed, including funded creation, commitment/reveal, wrong-chain rejection, forged reveal rejection, unauthorized callback rejection, the substantive GapJudge assessment and validator-agreement path, and the diagnostic probe judgment. The CI workflow runs the same suite on Linux; run [38116538585](https://github.com/ometere123/loophole/actions/runs/38116538585) passed both `contracts` and `frontend` jobs at commit `8c34301a0cc7ca927257ffea426a8aaf026d40ef`.
- The deployed source was retrieved from both canonical addresses with `genlayer code` and matched the repository fingerprints after normalizing only two endpoint-added trailing blank lines. Reciprocal binding and finalized deployment receipts are recorded in `deployments.studionet.json`.
- The simulator suite and eight executable behavioral mutation tests pass. The six real Direct Mode tests are separate from both simulator and mutation evidence, and none of these local results is substituted for validator consensus evidence.
- The simulator now also covers earliest-revealed queue selection, reveal-grace blocking and expiry, all three terminal INVALID appeal outcomes, and refusal to refund a revealed attempt after the reveal deadline. These checks run in CI with the mutation suite.
- The funded Studionet organizer/challenger lifecycle and independently verified EOA delivery remain unresolved until two funded injected-wallet accounts complete the sequence. No production economic pass is claimed in the manifest.
- The approved zero-value cross-contract relay finalized successfully with an authenticated relay parent → probe child relationship and a substantive `{"label":"CONTROL"}` readback. The raw receipt, validator, schema, source-correspondence and state evidence is in `docs/evidence/cross-contract-relay-2026-10-11.json`; this control does not prove the production GapJudge workload or payout lifecycle.
- A fresh read-only RuleVault snapshot on 2026-10-11 confirms both funded challenges remain in `REVIEWING`, with `40000000000000000` wei locked, zero claimable credit, zero withdrawals, and both five-day recovery deadlines still in the future. The repeatable checker is [`scripts/inspect_recovery_eligibility.mjs`](../scripts/inspect_recovery_eligibility.mjs); its current state and timeout calculation are in [`docs/evidence/live-funded-state-2026-10-11.json`](evidence/live-funded-state-2026-10-11.json), and the check submitted no transaction.
- The fresh frontend production audit (`npm --prefix frontend audit`) has no findings after the lockfile's compatible PostCSS `8.5.29` override. The full repository audit still reports six development-only findings from the pinned `genlayer@0.39.1` toolchain, including two critical Vitest/tinypool findings and moderate `@vitest/mocker`, `dockerode`, and `uuid` paths. npm's automatic fix replaces the required CLI with semver-major `genlayer@0.0.35`, so those findings remain an explicit development-tool limitation. They do not enter the shipped frontend bundle.
