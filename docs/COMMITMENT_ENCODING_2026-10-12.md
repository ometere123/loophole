# Commitment encoding hardening — 2026-10-12

The deployable `Loophole.py` source now binds the six commit/reveal fields with
length-prefixed UTF-8 segments before hashing them with SHA-256. This removes
the ambiguity of delimiter concatenation while preserving deterministic
client/contract encoding for Unicode input.

The frontend reads `commitment_encoding` from `get_config`. The existing live
monolith without that field continues to use its legacy pipe encoding, while a
deployment containing this correction advertises
`length-prefixed-utf8-v1`. This keeps historical commitments revealable and
prevents a client/contract encoding mismatch during the transition.

Verification completed before deployment:

- GenVM lint and semantic validation passed for the corrected contract with
  `genvm-linter 0.11.0` and runner `v0.3.0-rc7`.
- Python compilation and source preflight passed.
- The simulator and executable mutation suite passed: `54 passed`.
- Genuine GenVM Direct Mode passed: `12 passed`.
- Frontend typecheck and production build passed.
- The regression accepts pipe and Unicode characters in revealed fields and
  proves that an otherwise delimiter-shaped tuple hashes differently.

The existing monolith at
`0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf` remains unchanged at this stage.
Its deployed source fingerprint is recorded in the existing deployment
evidence. The corrected source requires one separately approved zero-value
deployment before the frontend is switched to its new address.
