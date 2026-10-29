const ADDRESS_RE = /^0x[a-fA-F0-9]{40}$/;
const COMMIT_RE = /^[a-fA-F0-9]{40}$/;
const SHA256_RE = /^[0-9a-f]{64}$/;

export const V2_METHODS = Object.freeze({
  config: 'get_config',
  challenge: 'get_challenge',
  challengePage: 'get_challenges_page',
  attempt: 'get_attempt',
  adjudication: 'get_adjudication',
  credit: 'get_credit',
  withdrawal: 'get_withdrawal',
  withdrawalsPage: 'get_withdrawals_page',
  policyVersion: 'get_policy_version',
  policyHistory: 'get_policy_history',
  repairProposal: 'get_repair_proposal',
  repairAdjudication: 'get_repair_adjudication',
  auditHistory: 'get_audit_history',
  createChallenge: 'create_challenge',
  createSourceChallenge: 'create_source_challenge',
  commitAttempt: 'commit_attempt',
  commitSourceAttempt: 'commit_source_attempt',
  revealAttempt: 'reveal_attempt',
  revealSourceAttempt: 'reveal_source_attempt',
  startReview: 'start_review',
  adjudicateReview: 'adjudicate_review',
  proposeRepair: 'propose_repair',
  startRepairReview: 'start_repair_review',
  adjudicateRepair: 'adjudicate_repair',
  recoverStalledRepair: 'recover_stalled_repair',
  createRechallenge: 'create_rechallenge',
});

const READ_METHODS = new Set(Object.values(V2_METHODS).filter(name => name.startsWith('get_')));
const WRITE_METHODS = new Set(Object.values(V2_METHODS).filter(name => !name.startsWith('get_')));

export function assertAddress(address) {
  if (!ADDRESS_RE.test(String(address))) throw new TypeError('A canonical 20-byte contract address is required.');
  return String(address);
}

export function assertCommit(commit) {
  if (!COMMIT_RE.test(String(commit))) throw new TypeError('The source reference must use a full 40-hex commit SHA.');
  return String(commit).toLowerCase();
}

export function assertSha256(digest) {
  if (!SHA256_RE.test(String(digest))) throw new TypeError('The source digest must be a lowercase SHA-256 hex string.');
  return String(digest);
}

export function buildV2Call({ address, functionName, args = [], value = 0n } = {}) {
  assertAddress(address);
  if (!WRITE_METHODS.has(functionName)) throw new TypeError(`Unsupported V2 write method: ${functionName}`);
  if (!Array.isArray(args)) throw new TypeError('Contract arguments must be an array.');
  if (typeof value !== 'bigint' && typeof value !== 'number' && typeof value !== 'string') {
    throw new TypeError('Transaction value must be an integer-compatible value.');
  }
  return { address, functionName, args, value };
}

export async function readV2(readContract, functionName, args = []) {
  if (typeof readContract !== 'function') throw new TypeError('readContract must be a function.');
  if (!READ_METHODS.has(functionName)) throw new TypeError(`Unsupported V2 read method: ${functionName}`);
  const raw = await readContract({ functionName, args });
  if (raw === '' || raw === null || raw === undefined) return null;
  if (typeof raw !== 'string') return raw;
  try { return JSON.parse(raw); } catch { return raw; }
}

export const readPolicyHistory = (readContract, challengeId) => readV2(readContract, V2_METHODS.policyHistory, [BigInt(challengeId)]);
export const readRepairProposal = (readContract, proposalId) => readV2(readContract, V2_METHODS.repairProposal, [BigInt(proposalId)]);
export const readAuditHistory = (readContract, challengeId) => readV2(readContract, V2_METHODS.auditHistory, [BigInt(challengeId)]);

export function explorerTx(hash, base = 'https://explorer-studio.genlayer.com') {
  return `${String(base).replace(/\/$/, '')}/tx/${encodeURIComponent(hash)}`;
}

export function explorerAddress(address, base = 'https://explorer-studio.genlayer.com') {
  assertAddress(address);
  return `${String(base).replace(/\/$/, '')}/address/${encodeURIComponent(address)}`;
}

async function sha256Hex(bytes) {
  if (!globalThis.crypto?.subtle) throw new Error('Web Crypto SHA-256 is unavailable in this runtime.');
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, '0')).join('');
}

export async function resolvePinnedGithubSource({ owner, repo, commit, path, versionMarker = '', fetchImpl = globalThis.fetch } = {}) {
  if (!owner || !repo || !path || path.startsWith('/') || path.includes('..')) throw new TypeError('A public repository owner, repository and safe file path are required.');
  const fullCommit = assertCommit(commit);
  if (typeof fetchImpl !== 'function') throw new TypeError('A fetch implementation is required.');
  const rawUrl = `https://raw.githubusercontent.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/${fullCommit}/${path.split('/').map(encodeURIComponent).join('/')}`;
  const response = await fetchImpl(rawUrl, { headers: { accept: 'text/plain' } });
  if (!response.ok) throw new Error(`Pinned source retrieval failed with HTTP ${response.status}.`);
  const bytes = await response.arrayBuffer();
  const sha256 = await sha256Hex(bytes);
  const content = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  if (versionMarker && !content.includes(versionMarker)) throw new Error('The pinned source does not contain the required version marker.');
  return { owner, repo, commit: fullCommit, path, rawUrl, sha256, byteLength: bytes.byteLength, content, versionMarker };
}

function statusName(value) {
  if (typeof value === 'string') return value.toUpperCase();
  if (value && typeof value.status === 'string') return value.status.toUpperCase();
  return '';
}

function successfulExecution(receipt) {
  if (!receipt || typeof receipt !== 'object') return false;
  if (receipt.txExecutionResultName) return receipt.txExecutionResultName === 'FINISHED_WITH_RETURN';
  const leader = receipt.consensus_data?.leader_receipt?.[0] ?? receipt.leader_receipt?.[0];
  return leader?.execution_result === 'SUCCESS' && (leader?.result?.status === 'return' || leader?.result === 'AAA=');
}

export async function waitForFinalized({ hash, getStatus, getReceipt, timeoutMs = 900000, intervalMs = 5000 } = {}) {
  if (!hash || typeof getStatus !== 'function' || typeof getReceipt !== 'function') throw new TypeError('hash, getStatus and getReceipt are required.');
  const started = Date.now();
  while (Date.now() - started <= timeoutMs) {
    const statusResult = await getStatus(hash);
    const status = statusName(statusResult);
    if (['CANCELED', 'CANCELLED', 'FAILED', 'REVERTED'].includes(status)) throw new Error(`Transaction ${hash} ended ${status}; no successful finality.`);
    if (status === 'FINALIZED') {
      const receipt = await getReceipt(hash);
      if (!receipt || !successfulExecution(receipt)) throw new Error(`Transaction ${hash} is finalized but execution was not independently verified successful.`);
      return { hash, status, receipt };
    }
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
  throw new Error(`Transaction ${hash} did not reach authoritative FINALIZED status before the timeout.`);
}

export const isSuccessfulExecution = successfulExecution;
