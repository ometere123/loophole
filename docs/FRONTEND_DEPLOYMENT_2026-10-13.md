# Active frontend production verification — 2026-10-13

This is a read-only verification of the existing public Vercel production
alias. It does not redeploy the frontend or change any wallet configuration.

- Public URL: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- HTTP status: `200`
- Final URL: `https://loophole-one.vercel.app/`
- Active contract: [`0xB87353201CeC791cc16c25e8eE1077076D90548E`](https://explorer-studio.genlayer.com/address/0xB87353201CeC791cc16c25e8eE1077076D90548E)
- Canonical address bundle hits: `1`
- Historical RuleVault/GapJudge address hits: `0`
- Script: [`scripts/verify_frontend_deployment.mjs`](../scripts/verify_frontend_deployment.mjs)

The verification command was:

```powershell
node scripts/verify_frontend_deployment.mjs https://loophole-one.vercel.app 0xB87353201CeC791cc16c25e8eE1077076D90548E
```

The public page and its JavaScript bundles therefore point at the canonical
Studionet 61999 monolith. Browser tests separately cover injected wallet
connection, wrong-network gating, wallet rejection and desktop/mobile public
navigation; they do not claim additional live wallet writes.
