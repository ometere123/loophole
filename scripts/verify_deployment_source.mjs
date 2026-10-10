#!/usr/bin/env node

import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';

const evidence = process.argv[2] ?? 'docs/evidence/adjudication-probe-deployment-rpc-2026-10-10.json';
const revision = process.argv[3] ?? '875c22953498940a839b95141994a565adbc0476';
const path = process.argv[4] ?? 'diagnostics/AdjudicationProbe.py';
const data = JSON.parse(readFileSync(evidence, 'utf8').replace(/^\uFEFF/, ''));
const tx = data.rows[0].transaction;
const signed = tx?.sim_config?.signed_rollup_transaction;
const expected = execFileSync('git', ['show', `${revision}:${path}`]);
const result = {
  transaction_hash: data.rows[0].hash,
  source_available_in_rpc: Boolean(signed),
  expected_source_bytes: expected.length,
  expected_source_sha256: createHash('sha256').update(expected).digest('hex'),
};
if (signed) {
  const encoded = Buffer.from(signed.replace(/^0x/, ''), 'hex');
  const offset = encoded.indexOf(expected);
  result.signed_rollup_bytes = encoded.length;
  result.source_offset = offset;
  result.exact_source_match = offset >= 0;
  result.submitted_source_sha256 = offset >= 0
    ? createHash('sha256').update(encoded.subarray(offset, offset + expected.length)).digest('hex')
    : null;
  result.submitted_source_bytes = offset >= 0 ? encoded.subarray(offset, offset + expected.length).length : null;
}
console.log(JSON.stringify(result, null, 2));
