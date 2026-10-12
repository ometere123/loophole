# Frontend production deployment — 2026-10-12

The linked Vercel project `delealufejoel-4184s-projects/loophole` was deployed
from the repository root with its verified `frontend` Root Directory setting.
The deployment completed with state `READY` and target `production`.

- Deployment: [`dpl_7fndczbfJhtg2rYYg8W3FXXSi4hf`](https://vercel.com/delealufejoel-4184s-projects/loophole/7fndczbfJhtg2rYYg8W3FXXSi4hf)
- Deployment URL: [`https://loophole-rfao2i510-delealufejoel-4184s-projects.vercel.app`](https://loophole-rfao2i510-delealufejoel-4184s-projects.vercel.app)
- Production alias: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- Public verification: HTTP `200`
- Canonical address bundle hits: `1`
- Historical RuleVault and GapJudge address bundle hits: `0`

Vercel Production, Preview and Development contain
`NEXT_PUBLIC_LOOPHOLE_ADDRESS` set to the source-verified monolith address
`0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf`. The stale two-contract public
address variables were removed. The RPC and explorer variables remain the
Studionet values, and no signing secret is configured for the project.

The local Playwright suite and the CI Chromium suite cover public rendering,
injected wallet connection, wrong-network blocking, wallet rejection and the
mobile navigation. The public bundle check is reproducible with
`node scripts/verify_frontend_deployment.mjs https://loophole-one.vercel.app`.

The earlier 2026-10-11 deployment record remains historical evidence for the
previous frontend binding; this deployment is the current release binding.
