import { resolvePinnedGithubSource } from '../sdk/index.js';

// Reproducible public example: this commit and file are public LOOPHOLE bytes.
const result = await resolvePinnedGithubSource({
  owner: 'ometere123',
  repo: 'loophole',
  commit: 'dc48fb847bb1e690a010d5a06912cdd4636cee3b',
  path: 'docs/evidence/source-backed-rulebook-2026-10-13.md',
  versionMarker: 'loophole-source-backed-demo-v1',
});
console.log(JSON.stringify({ rawUrl: result.rawUrl, sha256: result.sha256, byteLength: result.byteLength, versionMarker: result.versionMarker }, null, 2));
