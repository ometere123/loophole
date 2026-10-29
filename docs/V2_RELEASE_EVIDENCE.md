# V2 release evidence

This file records reproducible offline and Direct Mode evidence for the V2 source. It deliberately does not invent Studionet deployment or economic evidence.

## Source and toolchain

- V1 active contract: `0xB87353201CeC791cc16c25e8eE1077076D90548E`.
- V1 source SHA-256: `423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222`.
- V2 source: `contracts/LoopholeV2.py`.
- Current V2 source SHA-256: `c3ac301772a4f05dc9eb20d013bb1d4968cff6981547060219fc4947a2ba5b37` (reproduce with `python scripts/verify_v2_source.py`).
- Chain guard: 61999 (`0xF22F`); RPC: `https://studio.genlayer.com/api`.
- CLI: repository-local GenLayer `0.39.1`; frontend SDK: `genlayer-js@1.1.8`.
- Direct Mode runner: `v0.3.0-rc7`, with the repository's authenticated, SHA-256-checked resolver.

## Reproduction

```bash
python -m compileall -q contracts diagnostics scripts
python scripts/preflight.py
python scripts/verify_v2_source.py
GENVM_VERSION=v0.3.0-rc7 genvm-lint check contracts/LoopholeV2.py --json
GENVM_VERSION=v0.3.0-rc7 python -m pytest tests/direct -m direct -q
python -m pytest tests -m "not direct" -q
python -m pytest tests/test_v2_mutation_behavior.py -q
npm run test:sdk
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run test:e2e
```

The Direct Mode V2 cases exercise successful repair, rejected repair, unknown/malformed assessment, positive pinned-source authentication, source-byte mismatch, authorization, stale parent/review, idempotent replay, bounded re-challenge accounting and stalled repair recovery. The behavioral mutation suite executes mutated contract copies and demonstrates that removing organizer authorization or material-finding equivalence changes the observed result. Simulator tests remain separate from Direct Mode tests.

The fresh dependency audit is clean for both the repository production tree (`npm audit --omit=dev`) and the frontend (`npm --prefix frontend audit --audit-level=high`). The frontend remains on Next.js 15 and uses the compatible patched `15.5.28` release; no major framework migration was introduced.

## Live boundary

V2 has no deployment manifest or live transaction hashes because deployment and funded testing require explicit approval. The V1 active deployment, its source parity, finalized appeal, live verdicts and verified native GEN delivery remain documented in the root README and existing `docs/evidence/` records. They are not recycled as V2 proof.
