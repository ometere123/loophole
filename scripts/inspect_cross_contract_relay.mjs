#!/usr/bin/env node

import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';

const [relay, probe, deployment, parent, child] = process.argv.slice(2);
if (![relay, probe, deployment, parent, child].every(Boolean)) {
  console.error('usage: node scripts/inspect_cross_contract_relay.mjs <relay> <probe> <deployment> <parent> <child>');
  process.exit(2);
}

const rpcUrl = process.env.GENLAYER_RPC ?? 'https://studio.genlayer.com/api';
const client = createClient({chain: studionet});

async function rpc(method, params) {
  const response = await fetch(rpcUrl, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params}),
  });
  const body = await response.json();
  if (body.error) throw new Error(`${method}: ${body.error.code} ${body.error.message}`);
  return body.result;
}

async function probeRpc(method, params) {
  try {
    return {supported: true, result: await rpc(method, params)};
  } catch (error) {
    const message = String(error);
    let category = 'error';
    if (message.includes('Method not found') || message.includes('-32601')) category = 'unsupported';
    else if (message.includes('rate limit') || message.includes('-32029') || message.includes('429')) category = 'rate_limited';
    else if (message.includes('timeout') || message.includes('fetch failed') || message.includes('502') || message.includes('503') || message.includes('504')) category = 'temporary_failure';
    return {supported: false, category, error: message};
  }
}

const hashes = {deployment, parent, child};
const transactions = {};
for (const [name, hash] of Object.entries(hashes)) {
  transactions[name] = {
    hash,
    transaction: await rpc('eth_getTransactionByHash', [hash]),
    evm_receipt: await probeRpc('eth_getTransactionReceipt', [hash]),
    gen_status: await probeRpc('gen_getTransactionStatus', [hash]),
  };
}

const relayCode = await client.getContractCode(relay);
const relaySource = typeof relayCode === 'string' ? relayCode : String(relayCode);
const relaySchema = await client.getContractSchema(relay);
const relaySourceSha256 = createHash('sha256').update(relaySource, 'utf8').digest('hex');
const repositorySource = await readFile('diagnostics/CrossContractRelay.py', 'utf8');
const repositorySourceSha256 = createHash('sha256').update(repositorySource, 'utf8').digest('hex');

const [relayState, probeState, chainId, parentChildren] = await Promise.all([
  client.readContract({address: relay, functionName: 'get_state', args: []}),
  client.readContract({address: probe, functionName: 'get_state', args: []}),
  rpc('eth_chainId', []),
  probeRpc('gen_getTriggeredTransactionIds', [parent]),
]);

const diagnostics = {};
for (const method of ['gen_getTransactionReceipt', 'gen_getConsensusData', 'gen_getTransactionFee', 'gen_getTransactionExecution', 'gen_dbg_traceTransaction']) {
  diagnostics[method] = await probeRpc(method, [child]);
}

console.log(JSON.stringify({
  rpc: rpcUrl,
  chain_id: chainId,
  relay,
  probe,
  fixed_prompt: 'Return the fixed control label for this harmless diagnostic probe.',
  source: {repository_sha256: repositorySourceSha256, deployed_sha256: relaySourceSha256, exact_match: relaySourceSha256 === repositorySourceSha256, deployed_code: relaySource},
  schema: relaySchema,
  state_readbacks: {relay_after_trigger: relayState, probe_after_child: probeState},
  transactions,
  parent_children: parentChildren,
  lifecycle_diagnostics: diagnostics,
}, null, 2));
