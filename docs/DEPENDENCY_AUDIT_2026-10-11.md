# Dependency audit — 2026-10-11

Audits were run against the committed lockfiles after a clean install.

## Frontend

`npm --prefix frontend ci --ignore-scripts` completed successfully and
`npm --prefix frontend audit --json` reported zero vulnerabilities:

```text
total 0; info 0; low 0; moderate 0; high 0; critical 0
```

The lockfile pins the compatible PostCSS remediation through the root
`frontend/package.json` override:

```json
"overrides": { "postcss": "8.5.29" }
```

`npm --prefix frontend ls postcss --all` resolves every installed PostCSS
instance to `8.5.29`, including the Next.js and repository-local GenLayer
tool paths.

## Repository-local CLI

`npm ci` followed by `npm audit --json` reports six transitive development-tool
findings: four moderate and two critical. They enter through the pinned
`genlayer@0.39.1` dependency graph (`vitest`, `@vitest/mocker`, `tinypool`,
`dockerode`, and `uuid`). The suggested automatic fix replaces the pinned
GenLayer CLI with `genlayer@0.0.35`, which is a semver-major change and would
violate the release requirement to keep the repository-local CLI at `0.39.1`.
No override was applied because changing the CLI's transitive test/runtime
stack without compatibility evidence would undermine the GenVM verification
results. The findings are confined to the repository-local development CLI;
the shipped frontend has a clean audit.

The exact machine-readable audit output was generated from the committed
`package-lock.json` and is intentionally not committed because it contains
registry metadata that changes independently of the lockfile. Re-run the two
commands above to reproduce the result.
