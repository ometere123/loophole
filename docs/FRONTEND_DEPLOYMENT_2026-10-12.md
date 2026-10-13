# Frontend production deployment — 2026-10-12

> **Historical environment record.** The address recorded below belonged to
> the superseded `0xec98…` monolith. The active public frontend binding was
> independently rechecked against `0xB873…` on 2026-10-13 in
> [`FRONTEND_DEPLOYMENT_2026-10-13.md`](FRONTEND_DEPLOYMENT_2026-10-13.md).

The linked Vercel project `delealufejoel-4184s-projects/loophole` was rebuilt
from the repository root with its verified `frontend` Root Directory setting.
The deployment completed with state `READY` and target `production`.

- Deployment: [`dpl_FUDWXBPAnye2cMrSeyDC4SuZSqYC`](https://vercel.com/delealufejoel-4184s-projects/loophole/FUDWXBPAnye2cMrSeyDC4SuZSqYC)
- Deployment URL: [`https://loophole-iiy6b2rel-delealufejoel-4184s-projects.vercel.app`](https://loophole-iiy6b2rel-delealufejoel-4184s-projects.vercel.app)
- Production alias: [`https://loophole-one.vercel.app/`](https://loophole-one.vercel.app/)
- Public verification: HTTP `200`
- Canonical address bundle hits: `1`
- Historical RuleVault and GapJudge address bundle hits: `0`

Vercel Development, Preview and Production contained
`NEXT_PUBLIC_LOOPHOLE_ADDRESS` set to the then-current source-verified
monolith address `0xec98AFC80bda4b664F20d782aA8a0bd49e436233`. The stale two-contract
public address variables were removed. The RPC and explorer variables remain
the Studionet values, and no signing secret is configured for the project.

The reproducible public bundle check is
`node scripts/verify_frontend_deployment.mjs https://loophole-one.vercel.app`.
It verified the canonical address in one client bundle, no historical
production addresses, and a successful HTTP response. The earlier Vercel
deployment remains historical evidence; this deployment is the current
frontend binding. The production profile was also checked in a fresh browser
session after deployment and recovered the existing withdrawal as
`DELIVERY VERIFIED`, with both the parent and transfer-child explorer links.
