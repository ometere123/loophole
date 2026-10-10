#!/usr/bin/env node

import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';

const rpcUrl = process.env.GENLAYER_RPC ?? 'https://studio.genlayer.com/api';
const path = process.argv[2] ?? 'diagnostics/AdjudicationProbe.py';
const revision = process.argv[3] ?? '875c22953498940a839b95141994a565adbc0476';

function sourceRecord(label, bytes) {
  return {
    label,
    bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'),
    code_hex: `0x${bytes.toString('hex')}`,
  };
}

async function request(method, params) {
  const response = await fetch(rpcUrl, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params}),
  });
  return {http_status: response.status, body: await response.json()};
}

const original = execFileSync('git', ['show', `${revision}:${path}`]);
const corrected = readFileSync(path);
const results = [];
for (const [label, bytes] of [['original', original], ['corrected', corrected]]) {
  results.push({
    source: sourceRecord(label, bytes),
    rpc: await request('gen_getContractSchemaForCode', [`0x${bytes.toString('hex')}`]),
  });
}
console.log(JSON.stringify({rpc: rpcUrl, path, revision, results}, null, 2));
