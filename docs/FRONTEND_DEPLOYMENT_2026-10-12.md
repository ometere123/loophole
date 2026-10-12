# Frontend production deployment — 2026-10-12

The linked Vercel project `delealufejoel-4184s-projects/loophole` was rebuilt
from the repository root with its verified `frontend` Root Directory setting.
The deployment completed with state `READY` and target `production`.

- Deployment: [`4jeMAJ74cDg2mL4NcyZVzwQWDLHU`](https://vercel.com/delealufejoel-4184s-projects/loophole/4jeMAJ74cDg2mL4NcyZVzwQWDLHU)
- Deployment URL: [`https://loophole-4xok3ddhj-delealufejoel-4184s-projects.vercel.app`](https://loophole-4xok3ddhj-delealufejoel-4184s-projects.vercel.app)
- Production alias: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- Public verification: HTTP `200`
- Canonical address bundle hits: `1`
- Historical RuleVault and GapJudge address bundle hits: `0`

Vercel Development, Preview and Production contain
`NEXT_PUBLIC_LOOPHOLE_ADDRESS` set to the current source-verified monolith
address `0xec98AFC80bda4b664F20d782aA8a0bd49e436233`. The stale two-contract
public address variables were removed. The RPC and explorer variables remain
the Studionet values, and no signing secret is configured for the project.

The reproducible public bundle check is
`node scripts/verify_frontend_deployment.mjs https://loophole-one.vercel.app`.
It verified the canonical address in one client bundle, no historical
production addresses, and a successful HTTP response. The earlier Vercel
deployment remains historical evidence; this deployment is the current
frontend binding.
