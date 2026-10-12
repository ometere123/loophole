# Frontend production deployment — 2026-10-12

The linked Vercel project `delealufejoel-4184s-projects/loophole` was deployed
from the repository root with its verified `frontend` Root Directory setting.
The deployment completed with state `READY` and target `production`.

- Deployment: [`GGNFUySWc78dE5CkwyAmcx11o19L`](https://vercel.com/delealufejoel-4184s-projects/loophole/GGNFUySWc78dE5CkwyAmcx11o19L)
- Deployment URL: [`https://loophole-23osdoxpv-delealufejoel-4184s-projects.vercel.app`](https://loophole-23osdoxpv-delealufejoel-4184s-projects.vercel.app)
- Production alias: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- Public verification: HTTP `200`
- Canonical address bundle hits: `1`
- Historical RuleVault and GapJudge address bundle hits: `0`

Vercel Production, Preview and Development contain
`NEXT_PUBLIC_LOOPHOLE_ADDRESS` set to the corrected source-verified monolith
address `0xe5e2b5E9Bc53c9D19FEce32a72238842AD8B093e`. The stale two-contract public
address variables were removed. The RPC and explorer variables remain the
Studionet values, and no signing secret is configured for the project.

The local Playwright suite and the CI Chromium suite cover public rendering,
injected wallet connection, wrong-network blocking, wallet rejection and the
mobile navigation. The public bundle check is reproducible with
`node scripts/verify_frontend_deployment.mjs https://loophole-one.vercel.app`.

The earlier 2026-10-11 deployment record remains historical evidence for the
previous frontend binding; this deployment is the current release binding.
