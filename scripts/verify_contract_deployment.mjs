#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const rpcUrl = process.env.GENLAYER_RPC ?? 'https://studio.genlayer.com/api';
const expectedChainId = process.env.GENLAYER_CHAIN_ID ?? '0xf22f';
const expectedMethods = [
  'adjudicate_review',
  'appeal_invalid',
  'commit_attempt',
  'commit_source_attempt',
  'create_challenge',
  'create_source_challenge',
  'finalize_invalid',
  'get_adjudication',
  'get_attempt',
  'get_challenge',
  'get_challenges_page',
  'get_config',
  'get_credit',
  'get_withdrawal',
  'get_withdrawals_page',
  'recover_stalled_review',
  'refund_unwon',
  'reveal_attempt',
  'reveal_source_attempt',
  'settle_remaining_bond',
  'start_review',
  'withdraw',
];

function usage() {
  console.error('usage: node scripts/verify_contract_deployment.mjs <address> <deployment-tx> [source-path] [--out output.json]');
  process.exit(2);
}

const positional = [];
let outputPath = null;
for (let index = 2; index < process.argv.length; index += 1) {
  const value = process.argv[index];
  if (value === '--out') {
    outputPath = process.argv[++index];
    if (!outputPath) usage();
  } else {
    positional.push(value);
  }
}
if (positional.length < 2) usage();

const [address, deploymentTx, sourcePath = 'contracts/Loophole.py'] = positional;

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

function sha256(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

function decodeSource(value) {
  if (typeof value !== 'string') return null;
  if (value.startsWith('0x') && /^[0-9a-f]+$/i.test(value.slice(2)) && value.length % 2 === 0) {
    return Buffer.from(value.slice(2), 'hex');
  }
  const normalized = value.replace(/\s+/g, '');
  const base64 = Buffer.from(normalized, 'base64');
  if (base64.length > 0 && base64.toString('base64') === normalized) return base64;
  return Buffer.from(value, 'utf8');
}

function summarizeConsensus(transaction) {
  const consensus = transaction?.consensus_data ?? {};
  const leaderReceipt = Array.isArray(consensus.leader_receipt)
    ? consensus.leader_receipt[0]
    : consensus.leader_receipt;
  return {
    result_name: transaction?.result_name ?? null,
    result: transaction?.result ?? null,
    status_name: transaction?.status_name ?? null,
    leader_execution: leaderReceipt?.execution_result ?? null,
    leader_result_code: leaderReceipt?.result_code ?? null,
    votes: consensus.votes ?? {},
    validator_count: Array.isArray(consensus.validators)
      ? consensus.validators.length
      : Object.keys(consensus.votes ?? {}).length,
    votes_committed: transaction?.votes_committed ?? null,
    votes_revealed: transaction?.votes_revealed ?? null,
    num_of_rounds: transaction?.num_of_rounds ?? null,
    error: consensus.error ?? null,
  };
}

const localPath = path.resolve(sourcePath);
const localBytes = fs.readFileSync(localPath);
const [chainId, status, transaction, evmReceipt, deployedCode, schema] = await Promise.all([
  rpc('eth_chainId', []),
  rpc('gen_getTransactionStatus', [deploymentTx]),
  rpc('eth_getTransactionByHash', [deploymentTx]),
  rpc('eth_getTransactionReceipt', [deploymentTx]),
  rpc('gen_getContractCode', [address]),
  rpc('gen_getContractSchema', [address]),
]);

if (!transaction) throw new Error(`deployment transaction not found: ${deploymentTx}`);
const deployedBytes = decodeSource(deployedCode);
const submittedBytes = decodeSource(transaction?.data?.contract_code);
const methods = Object.keys(schema?.methods ?? {}).sort();
const expectedSorted = [...expectedMethods].sort();
const result = {
  rpc: rpcUrl,
  chain_id: chainId,
  expected_chain_id: expectedChainId,
  address,
  deployment_tx: deploymentTx,
  source: {
    path: sourcePath,
    local_bytes: localBytes.length,
    local_sha256: sha256(localBytes),
    gen_getContractCode_bytes: deployedBytes?.length ?? null,
    gen_getContractCode_sha256: deployedBytes ? sha256(deployedBytes) : null,
    submitted_contract_code_bytes: submittedBytes?.length ?? null,
    submitted_contract_code_sha256: submittedBytes ? sha256(submittedBytes) : null,
    deployed_exact_match: Boolean(deployedBytes && localBytes.equals(deployedBytes)),
    submitted_exact_match: Boolean(submittedBytes && localBytes.equals(submittedBytes)),
  },
  finality: {
    gen_getTransactionStatus: status,
    eth_receipt_status: evmReceipt?.status ?? null,
    from: transaction?.from_address ?? null,
    to: transaction?.to_address ?? null,
    consensus: summarizeConsensus(transaction),
  },
  schema: {
    constructor_params: schema?.ctor?.params ?? null,
    method_count: methods.length,
    methods,
    expected_methods: expectedSorted,
    exact_method_set: JSON.stringify(methods) === JSON.stringify(expectedSorted),
  },
};

const failures = [];
if (chainId?.toLowerCase() !== expectedChainId.toLowerCase()) failures.push('wrong chain id');
if (status !== 'FINALIZED') failures.push(`deployment status is ${status}`);
if (evmReceipt?.status !== '0x1') failures.push(`EVM receipt status is ${evmReceipt?.status ?? 'missing'}`);
if (!result.source.deployed_exact_match) failures.push('gen_getContractCode does not exactly match the repository source');
if (!result.source.submitted_exact_match) failures.push('submitted contract_code does not exactly match the repository source');
if (result.finality.consensus.leader_execution !== 'SUCCESS') failures.push('leader execution was not SUCCESS');
if (result.schema.constructor_params?.length !== 0) failures.push('constructor schema is not parameterless');
if (!result.schema.exact_method_set) failures.push('schema method set differs from the expected production surface');

result.verification = {passed: failures.length === 0, failures};
const serialized = JSON.stringify(result, null, 2) + '\n';
if (outputPath) {
  fs.writeFileSync(path.resolve(outputPath), serialized, 'utf8');
}
console.log(serialized);
if (failures.length) process.exit(1);
