# LOOPHOLE historical invalid lifecycle — 2026-10-12

The superseded source-verified single-contract deployment at [`0xec98AFC80bda4b664F20d782aA8a0bd49e436233`](https://explorer-studio.genlayer.com/address/0xec98AFC80bda4b664F20d782aA8a0bd49e436233) completed a real two-wallet negative lifecycle on Studionet 61999. This record is historical evidence and is not proof for the active `0xB873…` release. Wallet `0xfcef…522f` organized challenge 2 and Wallet `0x8130…20B0` submitted the challenger attempt.

- Create and fund challenge 2: [`0xcb8211cb64193d6e17e9c588a5e624077a89386f8822bff34155dfa82e36692a`](https://explorer-studio.genlayer.com/tx/0xcb8211cb64193d6e17e9c588a5e624077a89386f8822bff34155dfa82e36692a)
- Commit attempt 2: [`0xab473c548350a6dec8b20cc5e4b859a601eddefe52ede6aac090c9846cb0734a`](https://explorer-studio.genlayer.com/tx/0xab473c548350a6dec8b20cc5e4b859a601eddefe52ede6aac090c9846cb0734a)
- Reveal attempt 2: [`0x36d2d863af5c6d0b3ab3a6f00275cb1e5c4fbcb4eeed74e78630e4f82af4f45f`](https://explorer-studio.genlayer.com/tx/0x36d2d863af5c6d0b3ab3a6f00275cb1e5c4fbcb4eeed74e78630e4f82af4f45f)
- Freeze review: [`0x3fead4a4df595bf20a1e5b549b5fa4f574a758dadc052e6c9e35a60da55c388b`](https://explorer-studio.genlayer.com/tx/0x3fead4a4df595bf20a1e5b549b5fa4f574a758dadc052e6c9e35a60da55c388b)
- Direct adjudication: [`0xf893b9c46fc29ee29eabf41f13ab2c2e55cfca7591bc5501245bf4310f4874c8`](https://explorer-studio.genlayer.com/tx/0xf893b9c46fc29ee29eabf41f13ab2c2e55cfca7591bc5501245bf4310f4874c8)

Every transaction finalized with EVM receipt `0x1` and GenVM `SUCCESS`. The adjudication reached `MAJORITY_AGREE` with three `AGREE` votes and two idle validators canceled after quorum. The stored material findings were `feasible=PROVEN`, `letter=DISPROVEN`, and `purpose=UNKNOWN`, producing `verdict=INVALID`. The evidence was a deliberately ineligible four-word post against a rule requiring at least five words; the rule quote and the revealed scenario were read back from the finalized contract state.

The contract conservatively entered `INVALID_PENDING` with `appeal_used=false`. No winner, claimable credit, or withdrawal was created. The bounded appeal deadline remains recorded on-chain, and the prize plus challenger bond remain locked. This evidence therefore proves a real negative adjudication while preserving the distinction between an INVALID verdict and terminal post-appeal settlement.

The complete machine-readable evidence is [`docs/evidence/loophole-current-invalid-lifecycle-2026-10-12.json`](evidence/loophole-current-invalid-lifecycle-2026-10-12.json).
