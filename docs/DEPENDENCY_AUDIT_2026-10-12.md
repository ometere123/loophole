# Dependency audit — 2026-10-12

Audits were run against both committed lockfiles in the current checkout. The
frontend was installed with `npm --prefix frontend ci` and the repository root
with `npm ci`.

## Frontend

`npm --prefix frontend audit --json` reported zero vulnerabilities:

```text
total 0; info 0; low 0; moderate 0; high 0; critical 0
```

The committed frontend override pins PostCSS to the compatible fixed release:

```json
"overrides": { "postcss": "8.5.29" }
```

The Next.js package metadata still declares its requested range as
`postcss: 8.4.31` in `frontend/package-lock.json` (the lockfile records the
parent dependency request). The installed and resolved package is
`postcss@8.5.29`, verified with `npm --prefix frontend ls postcss --all`; Next,
Vite and the repository-local GenLayer tool path all resolve to 8.5.29. This is
why the old 8.4.31 text remains without an installed 8.4.31 package.

## Repository-local CLI

`npm audit --json` reports six transitive development-tool findings: four
moderate and two critical. They enter through the pinned `genlayer@0.39.1`
dependency graph (`vitest`, `@vitest/mocker`, `tinypool`, `dockerode` and
`uuid`). npm's suggested automatic fix replaces the required CLI with
`genlayer@0.0.35`, a semver-major change. No override was applied because
changing the pinned GenLayer CLI's test/runtime stack without compatibility
evidence would invalidate the required verification environment.

These findings are confined to the repository-local development CLI. The
shipped frontend lockfile has zero audit findings. Re-run the two audit
commands above to reproduce the result.
