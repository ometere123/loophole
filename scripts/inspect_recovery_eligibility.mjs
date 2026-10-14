#!/usr/bin/env node

import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionHashVariant } from 'genlayer-js/types';

const rpcUrl = process.env.GENLAYER_RPC ?? 'https://studio.genlayer.com/api';
// The active release is the single-contract Loophole monolith. Keep the
// environment override for historical investigations, but never default a
// current recovery read to the retired RuleVault deployment.
const vault = (process.env.LOOPHOLE_ADDRESS ??
  process.env.RULE_VAULT_ADDRESS ??
  '0xB87353201CeC791cc16c25e8eE1077076D90548E');
const readClient = createClient({chain: studionet});

async function rpc(method, params) {
  const response = await fetch(rpcUrl, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: Date.now(), method, params}),
  });
  const body = await response.json();
  if (body.error) throw new Error(`${method}: ${body.error.code} ${body.error.message}`);
  return body.result;
}

async function read(functionName, args = []) {
  return readClient.readContract({
    address: vault,
    functionName,
    args,
    transactionHashVariant: TransactionHashVariant.LATEST_FINAL,
  });
}

function parseRecord(value) {
  if (value == null || value === '') return null;
  return typeof value === 'string' ? JSON.parse(value) : value;
}

const [chainId, configRaw] = await Promise.all([
  rpc('eth_chainId', []),
  read('get_config'),
]);
const config = parseRecord(configRaw);
const nowUnix = Math.floor(Date.now() / 1000);
const challengeCount = Number(config?.challenge_count ?? 0);
const challenges = [];

for (let id = 1; id <= challengeCount; id += 1) {
  const challenge = parseRecord(await read('get_challenge', [BigInt(id)]));
  if (!challenge) continue;
  const attempts = [];
  for (const attemptId of challenge.attempts ?? []) {
    const attempt = parseRecord(await read('get_attempt', [BigInt(attemptId)]));
    if (attempt) attempts.push(attempt);
  }
  const reviewTimeoutAt = challenge.active_attempt !== '0'
    ? Number(challenge.review_started) + Number(config.review_timeout_seconds)
    : null;
  const timeoutElapsed = Boolean(
    challenge.status === 'OPEN' &&
    challenge.active_attempt !== '0' &&
    reviewTimeoutAt !== null &&
    nowUnix > reviewTimeoutAt,
  );
  challenges.push({
    id: String(id),
    challenge,
    attempts,
    review_timeout_at: reviewTimeoutAt,
    timeout_elapsed: timeoutElapsed,
    recovery_eligible: timeoutElapsed,
  });
}

console.log(JSON.stringify({
  observed_at: new Date().toISOString(),
  rpc: rpcUrl,
  chain_id: chainId,
  vault,
  now_unix: nowUnix,
  config,
  challenges,
  recovery_candidates: challenges
    .filter(item => item.recovery_eligible)
    .map(item => item.id),
  write_submitted: false,
  interpretation: 'Read-only finalized active Loophole state. A recovery candidate is reported only when the challenge is OPEN, has an active attempt, and its five-day review timeout has elapsed.',
}, null, 2));
