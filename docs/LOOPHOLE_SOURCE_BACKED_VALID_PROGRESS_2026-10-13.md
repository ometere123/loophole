# LOOPHOLE source-backed VALID candidate — live progress — 2026-10-13

This record documents the approved current-release source-backed test up to the
last finalized transaction. It does not claim a `VALID` verdict, entitlement,
withdrawal, child transfer or recipient credit. The machine-readable evidence
is [`evidence/loophole-source-backed-valid-progress-2026-10-13.json`](evidence/loophole-source-backed-valid-progress-2026-10-13.json).

## Release and signing context

- Contract: [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E)
- Network: Studionet `61999` (`0xf22f`), RPC `https://studio.genlayer.com/api`
- Deployed source SHA-256: `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`
- Repository-local CLI: `genlayer@0.39.1`
- Frontend SDK used by the application: `genlayer-js@1.1.8`
- Signer: Wallet B, `0xb845a69860ba4cdf19cfdc5afbaf2e20b6be86b0`
- Signing path: the repository-local `genlayer-js` write API used the unlocked
  `walletB` CLI keychain account in memory. The private key was never printed,
  persisted or committed. The CLI `write` wrapper itself hard-codes zero value,
  so it could not carry the required bond; no alternate signer was used.
- Observation after reveal: `2026-10-13T21:32:35.392Z`

The frozen rulebook is the active challenge source:

```text
https://raw.githubusercontent.com/ometere123/loophole/37822b9333e064e632896a8318f2fee5bb4dd1cd/docs/evidence/source-backed-rulebook-2026-10-13.md
sha256: 5df4be40f2b68695c555c1e99c03c7cc0784b810b9d9ccf1cf218fadb3b7459a
version: loophole-source-backed-demo-v1
```

The candidate evidence snapshot is pinned to immutable bytes:

```text
https://raw.githubusercontent.com/ometere123/loophole/f73c308f34e1e50c427148ff708da67f6a647bb1/docs/evidence/source-backed-valid-evidence-2026-10-13.md
sha256: 8a854ec05202de38007b0604ced411bc7de8a501260a8d92140964c72d9d74ef
version: loophole-source-backed-valid-evidence-v1
```

The committed candidate is intended to test a case where the literal rule is
satisfied but the described reversal defeats the stated educational purpose.
The hosted validators remain authoritative; the intended finding is not a
substitute for their actual result.

## Finalized transactions completed

| Order | Method | Value | Transaction | Finalized evidence | State readback |
|---|---|---:|---|---|---|
| 1 | `commit_source_attempt(1, ...)` | `0.01 GEN` | [`0x9e513b578b7432d8b41708054c130f4fc20df6447efc35222e4d668270a9753a`](https://explorer-studio.genlayer.com/tx/0x9e513b578b7432d8b41708054c130f4fc20df6447efc35222e4d668270a9753a) | `FINALIZED`; `eth_getTransactionReceipt.status=0x1`; leader `SUCCESS`; `MAJORITY_AGREE`; five RPC vote entries, all `agree` | Attempt `#3` created as `COMMITTED` with the exact commitment, evidence URL, digest and version |
| 2 | `reveal_source_attempt(3, ...)` | `0 GEN` | [`0xc14521665aed28cb7703d09e99394add6b0dfc0c6d0261f65e03fc594f6fe387`](https://explorer-studio.genlayer.com/tx/0xc14521665aed28cb7703d09e99394add6b0dfc0c6d0261f65e03fc594f6fe387) | `FINALIZED`; `eth_getTransactionReceipt.status=0x1`; leader `SUCCESS`; `MAJORITY_AGREE`; five RPC vote entries, all `agree` | Attempt `#3` is `REVEALED` with the expected evidence hash and frozen fields |

For both transactions, `gen_getTransactionStatus` returned `FINALIZED` and the
transaction response reported `result_name=MAJORITY_AGREE`. The supported
transport receipt was `eth_getTransactionReceipt` with `status=0x1`. The RPC
does not implement `gen_getTransactionReceipt`; the exact response was:

```text
gen_getTransactionReceipt: -32601 Method not found: gen_getTransactionReceipt
```

This unsupported method is recorded as an RPC capability limitation, not as a
failed transaction. No child transactions were present for either write.

## Finalized state after reveal

The finalized contract readback shows:

- Challenge `1`: `OPEN`, `active_attempt=0`, `active_round=2`, `active_slots=2`.
- Attempt `#3`: challenger Wallet B; status `REVEALED`; commitment
  `fadfdadde62e0c6195abe9f877fdc9ae48bc897c8f910dc2245fe19d537b2ece`;
  evidence hash
  `20502c9b61a7d89c465cf957837dd7be59a7b9467494f2c11892900fefb750`;
  `evidence_state` is not assigned until adjudication; no verdict or credit
  exists.
- Attempt `#2`: `INVALID_PENDING`, `appeal_used=false`, and still entitled to
  its appeal window until `2026-10-14T18:38:05Z` (`19:38:05` WAT).
- Configuration: `attempt_count=3`, `adjudication_count=2`,
  `withdrawal_count=0`, `total_credit_wei=10000000000000000`, and
  `total_locked_wei=30000000000000000`.
- Wallet B credit remains `0`. The existing `0.01 GEN` credit belongs to the
  earlier challenger and is not part of this candidate's entitlement.

The new attempt was committed and revealed before the challenge submission
deadline (`2026-10-14T18:11:13Z`). The FIFO review cannot proceed until the
earlier attempt's appeal right is resolved; bypassing it would violate the
contract's queue and appeal protections.

## Remaining approved sequence

After the appeal deadline, each step requires a fresh finalized readback and
must stop on a state mismatch, failed execution, canceled consensus or
unresolved result:

1. `finalize_invalid(2)` — close the expired appeal window.
2. `start_review(1)` — freeze attempt `#3` as the next eligible review.
3. `adjudicate_review(1, 3, 3)` — perform genuine source-backed consensus.
4. Read the verdict and credit. Only an actual `VALID` result with exactly
   `20000000000000000` wei credited to Wallet B permits `withdraw()`.
5. If withdrawal is permitted, independently verify its finalized external
   child with `scripts/verify_delivery.mjs`, including exact origin,
   beneficiary, value and authoritative `value_credited=true` evidence.

No adjudication, callback, entitlement, withdrawal, child transfer or
recipient-credit claim is included in this record.
