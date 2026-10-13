# LOOPHOLE source-backed VALID and delivery preparation — 2026-10-13

This document prepares one bounded live test on the existing source-verified
monolith. It contains no transaction receipts and records no new blockchain
write. The sequence is awaiting explicit approval for the attached 0.01 GEN
challenger bond and the resulting withdrawal.

## Preconditions observed read-only

- Contract: [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E)
- Chain: Studionet `61999` (`0xf22f`)
- Source SHA-256: `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`
- Challenge: `1`, source mode `PINNED_SOURCE`, status `OPEN`
- Attempt `2`: `INVALID_PENDING`, appeal unused, appeal deadline `2026-10-14T18:38:05Z`
- Challenge submission deadline: `2026-10-14T18:11:13Z`; the new commitment and reveal must be completed before this time
- Attempt `1` has a separate `0.01 GEN` claimable credit for the earlier challenger and is not used as the payout beneficiary
- Candidate challenger/beneficiary: `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0`; finalized `get_credit` readback was `0`
- No current-release withdrawal exists; `withdrawal_count=0`

The older invalid ruling must remain appealable until its deadline. The new
attempt may be committed and revealed before that deadline, but it cannot be
reviewed until the earlier appeal right is resolved.

## Authenticated source inputs

The frozen rulebook is the existing active challenge source:

```text
https://raw.githubusercontent.com/ometere123/loophole/37822b9333e064e632896a8318f2fee5bb4dd1cd/docs/evidence/source-backed-rulebook-2026-10-13.md
sha256: 5df4be40f2b68695c555c1e99c03c7cc0784b810b9d9ccf1cf218fadb3b7459a
version: loophole-source-backed-demo-v1
```

The candidate evidence snapshot is pinned to the commit that introduced it:

```text
https://raw.githubusercontent.com/ometere123/loophole/f73c308f34e1e50c427148ff708da67f6a647bb1/docs/evidence/source-backed-valid-evidence-2026-10-13.md
sha256: 8a854ec05202de38007b0604ced411bc7de8a501260a8d92140964c72d9d74ef
version: loophole-source-backed-valid-evidence-v1
```

The evidence describes a post that satisfies the literal rule and the
new-explanation limitation while deliberately reversing the source conclusion.
That is intended to make all three material findings independently assessable:
literal compliance `PROVEN`, purpose conflict `PROVEN`, and feasibility
`PROVEN`. The hosted validators remain authoritative; this preparation does
not predict or manufacture their result.

## Exact proposed writes

The transaction arguments below use the active challenge's
`length-prefixed-utf8-v1` commitment encoding and the candidate wallet above.
The new attempt is expected to be attempt `3` if the read-only preflight still
reports `attempt_count=2`.

| Order | Method and arguments | Sender | Attached value | Expected effect |
|---|---|---|---:|---|
| 1 | `commit_source_attempt(1, fadfdadde62e0c6195abe9f877fdc9ae48bc897c8f910dc2245fe19d537b2ece, <candidate evidence URL>, 8a854ec05202de38007b0604ced411bc7de8a501260a8d92140964c72d9d74ef, loophole-source-backed-valid-evidence-v1)` | candidate challenger | `0.01 GEN` | Creates attempt `3` in `COMMITTED`; maximum new escrow at risk is `0.01 GEN`. Must finalize before the submission deadline. |
| 2 | `reveal_source_attempt(3, source-valid-salt-20261013, <scenario below>, <rule quote below>, <impact below>)` | candidate challenger | `0 GEN` | Reveals the exact committed source-backed case. |
| 3 | `finalize_invalid(2)` | permissionless | `0 GEN` | After `2026-10-14T18:38:05Z`, closes the old appeal window and settles attempt `2` without changing the new attempt. |
| 4 | `start_review(1)` | permissionless | `0 GEN` | Freezes attempt `3` as the next FIFO review and advances the round. |
| 5 | `adjudicate_review(1, 3, 3)` | permissionless | `0 GEN` | Runs fresh GenLayer consensus against the frozen rulebook, attempt and authenticated bytes. Stop on any non-terminal or non-successful execution. |
| 6 | `withdraw()` | candidate challenger | `0 GEN` | Only if attempt `3` is finalized `VALID` and the candidate's credit is exactly `0.02 GEN`; creates the asynchronous native GEN transfer parent. |

Exact reveal fields for order 2:

```text
scenario:
Publish a public post with six words and one source link, then add a new explanation that deliberately reverses the linked source's conclusion while presenting the reversal as education; do not copy an earlier post.

rule_quote:
Award 10 points to any public post with at least five words and one source link.

impact:
The post meets the five-word and source-link conditions and adds a new explanation, but the intentionally reversed explanation defeats the goal of a genuine educational contribution.
```

The commitment is the SHA-256 of the length-prefixed UTF-8 concatenation of
`1`, the lower-case candidate address, the salt, scenario, quote and impact.

## Cost, stopping rules and evidence

The only new attached GEN is the `0.01 GEN` challenger bond. The withdrawal
does not add value; it claims the expected `0.02 GEN` bounty-plus-bond credit if
and only if the adjudication is `VALID`. Network or consensus fees, if the
wallet presents any separately, must be shown by the wallet and approved at
signing time. No CLI key or privileged signer is used.

Before each write, the chain, active contract, attempt counts, deadline and
sender are re-read. A wallet rejection, stale state, failed execution,
canceled consensus, unexpected verdict, conflicting receipt or missing finality
stops the sequence; there is no blind retry. A `VALID` result is not assumed.

After a successful withdrawal, `scripts/verify_delivery.mjs` must independently
match the finalized parent to the active contract, identify its exact child,
match beneficiary `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0` and amount
`20000000000000000`, and require finalized successful child transport plus
authoritative `value_credited=true`. The contract record remains
`TRANSFER_EMITTED_UNVERIFIED`.

This is a preparation record only. It does not authorize the writes above.
