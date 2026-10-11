#!/usr/bin/env node

import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const [probe, deployment, transaction, challenge = '2', attempt = '2', round = '1'] = process.argv.slice(2);
if (![probe, deployment, transaction].every(Boolean)) {
  console.error('usage: node scripts/inspect_direct_workload_probe.mjs <probe> <deployment-tx> <adjudication-tx> [challenge] [attempt] [round]');
  process.exit(2);
}

const rpcUrl = process.env.GENLAYER_RPC ?? 'https://studio.genlayer.com/api';
const client = createClient({chain: studionet});

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

const key = `${challenge}:${attempt}:${round}`;
const repositorySource = await readFile('diagnostics/DirectGapJudgeWorkloadProbe.py');
const deployedSource = await client.getContractCode(probe);
const deployedText = typeof deployedSource === 'string' ? deployedSource : String(deployedSource);
const source = {
  repository_sha256: createHash('sha256').update(repositorySource).digest('hex'),
  deployed_sha256: createHash('sha256').update(deployedText, 'utf8').digest('hex'),
  exact_match: createHash('sha256').update(repositorySource).digest('hex') === createHash('sha256').update(deployedText, 'utf8').digest('hex'),
};

const [chainId, deploymentTx, adjudicationTx, deploymentReceipt, adjudicationReceipt,
  deploymentStatus, adjudicationStatus, schema, configuration, caseResult, children] = await Promise.all([
  rpc('eth_chainId', []),
  rpc('eth_getTransactionByHash', [deployment]),
  rpc('eth_getTransactionByHash', [transaction]),
  probeRpc('eth_getTransactionReceipt', [deployment]),
  probeRpc('eth_getTransactionReceipt', [transaction]),
  probeRpc('gen_getTransactionStatus', [deployment]),
  probeRpc('gen_getTransactionStatus', [transaction]),
  client.getContractSchema(probe),
  client.readContract({address: probe, functionName: 'get_configuration', args: []}),
  client.readContract({address: probe, functionName: 'get_case', args: [key]}),
  probeRpc('gen_getTriggeredTransactionIds', [transaction]),
]);

const diagnostics = {};
for (const method of ['gen_getConsensusData', 'gen_getTransactionFee', 'gen_getTransactionExecution', 'gen_getTransactionLifecycle', 'gen_dbg_traceTransaction']) {
  diagnostics[method] = await probeRpc(method, [transaction]);
}

console.log(JSON.stringify({
  rpc: rpcUrl,
  chain_id: chainId,
  expected_chain_id: '0xf22f',
  probe,
  key,
  source,
  schema,
  configuration,
  case: caseResult,
  transactions: {
    deployment: {hash: deployment, transaction: deploymentTx, receipt: deploymentReceipt, status: deploymentStatus},
    adjudication: {hash: transaction, transaction: adjudicationTx, receipt: adjudicationReceipt, status: adjudicationStatus},
  },
  triggered_children: children,
  lifecycle_diagnostics: diagnostics,
}, null, 2));
