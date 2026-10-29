import test from 'node:test';
import assert from 'node:assert/strict';
import { buildV2Call, explorerTx, readV2, resolvePinnedGithubSource, waitForFinalized } from '../index.js';

test('builds only declared V2 writes and explorer links', () => {
  const call = buildV2Call({ address: '0x' + 'a'.repeat(40), functionName: 'propose_repair', args: [1n], value: 0n });
  assert.equal(call.functionName, 'propose_repair');
  assert.equal(explorerTx('0xabc'), 'https://explorer-studio.genlayer.com/tx/0xabc');
  assert.throws(() => buildV2Call({ address: '0x' + 'a'.repeat(40), functionName: 'unknown' }));
});

test('parses JSON reads but preserves scalar reads', async () => {
  const calls = [];
  const read = async input => { calls.push(input); return input.functionName === 'get_config' ? '{"protocol_version":"2.0.0-policy-repair"}' : '7'; };
  assert.deepEqual(await readV2(read, 'get_config'), { protocol_version: '2.0.0-policy-repair' });
  assert.equal(await readV2(read, 'get_credit', ['0x' + 'b'.repeat(40)]), 7);
  assert.equal(calls.length, 2);
});

test('pins exact GitHub bytes and rejects a missing marker', async () => {
  const body = new TextEncoder().encode('VERSION: sdk-test-v1\nRule: exact bytes\n');
  const result = await resolvePinnedGithubSource({ owner: 'ometere123', repo: 'loophole', commit: 'd'.repeat(40), path: 'docs/evidence/rule.md', versionMarker: 'sdk-test-v1', fetchImpl: async () => ({ ok: true, arrayBuffer: async () => body }) });
  assert.equal(result.byteLength, body.byteLength);
  assert.equal(result.rawUrl, `https://raw.githubusercontent.com/ometere123/loophole/${'d'.repeat(40)}/docs/evidence/rule.md`);
  await assert.rejects(() => resolvePinnedGithubSource({ owner: 'o', repo: 'r', commit: 'd'.repeat(40), path: 'rule.md', versionMarker: 'missing', fetchImpl: async () => ({ ok: true, arrayBuffer: async () => body }) }));
});

test('waits for finality and fails closed on unsuccessful execution', async () => {
  let count = 0;
  const result = await waitForFinalized({ hash: '0x1', intervalMs: 0, getStatus: async () => (++count > 1 ? 'FINALIZED' : 'ACCEPTED'), getReceipt: async () => ({ txExecutionResultName: 'FINISHED_WITH_RETURN' }) });
  assert.equal(result.status, 'FINALIZED');
  await assert.rejects(() => waitForFinalized({ hash: '0x2', intervalMs: 0, getStatus: async () => 'FINALIZED', getReceipt: async () => ({ txExecutionResultName: 'CANCELED' }) }));
});
