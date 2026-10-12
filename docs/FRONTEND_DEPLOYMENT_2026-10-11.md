> **Historical superseded record.** This deployment predates the corrected
> single-contract binding. The current production URL and canonical address
> verification are in
> [`FRONTEND_DEPLOYMENT_2026-10-12`](FRONTEND_DEPLOYMENT_2026-10-12.md).

# Frontend production deployment — 2026-10-11

The restored Vercel project `delealufejoel-4184s-projects/loophole` was
deployed from verified repository commit
[`db6016d0f47aba02afd5ae1d5609ab075cdf4309`](https://github.com/ometere123/loophole/commit/db6016d0f47aba02afd5ae1d5609ab075cdf4309),
with the project Root Directory set to `frontend`. This deployment includes
the diagnostic evidence, behavioral mutation tests, lockfile remediation,
withdrawal delivery reconciliation, and the isolated cross-contract relay
diagnostic source.

- Deployment: [`dpl_HskpoV1g7YZGo487m7H3qtCLwHL6`](https://vercel.com/delealufejoel-4184s-projects/loophole/HskpoV1g7YZGo487m7H3qtCLwHL6)
- Deployment URL: [`https://loophole-ckqgbi7qs-delealufejoel-4184s-projects.vercel.app`](https://loophole-ckqgbi7qs-delealufejoel-4184s-projects.vercel.app)
- Production URL: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- Deployment state: `READY`, target `production`
- Anonymous HTTP verification: `200 OK`
- Page title: `Loophole! — Find the flaw. Claim the prize.`

The production client bundle contains the canonical configuration values:

- RuleVault: `0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26`
- GapJudge: `0xb14B08cd35Fa64FE795e14931DdA09999627785d`
- RPC: `https://studio.genlayer.com/api`
- Explorer: `https://explorer-studio.genlayer.com`

Vercel project environment configuration contains these four public variables
for Production, Preview, and Development. No signing key or wallet secret is
configured. Project protection is set to `preview`, so the production alias
is public while preview deployments remain protected.

## Latest production verification

After receipt reconciliation was hardened and pushed at commit
`ab76d3484eaa46892895b44b0f51465df97e6cd1`, Vercel created a newer production
deployment:

- Deployment: [`dpl_9PQsbtBKp7a7sUicvN5GpegZqyUw`](https://vercel.com/delealufejoel-4184s-projects/loophole/dpl_9PQsbtBKp7a7sUicvN5GpegZqyUw)
- Deployment URL: [`https://loophole-lbdm2vlv8-delealufejoel-4184s-projects.vercel.app`](https://loophole-lbdm2vlv8-delealufejoel-4184s-projects.vercel.app)
- State: `READY`, target `production`
- Alias: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- Public verification: HTTP `200`, canonical contract addresses present, and the receipt/lifecycle reconciliation code present in the client bundle.

## Read-only browser verification

Using a separate preserved browser tab on 2026-10-11:

- The public home page loaded its finalized chain statistics and exposed both active challenge links.
- Search for `Hashtag` narrowed the list to challenge #2; the Community and Open-only filters remained usable.
- The direct challenge route loaded the real RuleVault state for challenge #2, showing attempt #2 as awaiting the finalized judge callback.
- `Start next review`, `Recover stalled review`, and `Refund unwon bounty` were visibly disabled while that review remained active, matching the five-day timeout protection.

This was read-only browser verification. It did not claim wallet connection, transaction signing, adjudication completion, or payout delivery.
