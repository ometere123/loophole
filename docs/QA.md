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
- GenVM Direct Mode executes the actual contracts locally: 4 tests passed, including funded creation, commitment/reveal, wrong-chain rejection, forged reveal rejection, and unauthorized callback rejection. The CI workflow runs the same suite on Linux.
- The deployed source was retrieved from both canonical addresses with `genlayer code` and matched the repository fingerprints after normalizing only two endpoint-added trailing blank lines. Reciprocal binding and finalized deployment receipts are recorded in `deployments.studionet.json`.
- The 11 simulator tests and the four mutation alarms pass. Simulator and mutation results are separate from validator consensus evidence.
- The funded Studionet organizer/challenger lifecycle and independently verified EOA delivery remain unresolved until two funded injected-wallet accounts complete the sequence. No production economic pass is claimed in the manifest.
- `npm audit` has no production findings in the repository root. The frontend has one high and one moderate transitive PostCSS finding through Next.js; npm's non-breaking remediation leaves those findings, while the automatic fix requires a Next.js 16 upgrade. This is recorded as an accepted release limitation pending a deliberate framework upgrade.
