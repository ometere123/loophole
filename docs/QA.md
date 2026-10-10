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

No item is marked as achieved without evidence. The included offline 11 state-machine tests passed in the creation environment, but they do not assert production consensus correctness. A full 5/5/5/5 review is independent and cannot be guaranteed by source packaging.
