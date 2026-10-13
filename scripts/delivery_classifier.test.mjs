import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyDelivery, DELIVERY_STATES} from './delivery_classifier.mjs';

const parent = (overrides = {}) => ({
  found: true,
  destination_matches: true,
  status_conflict: false,
  failed: false,
  receipt_pending: false,
  receipt_unavailable: false,
  receipt_category: null,
  receipt_failed: false,
  finalized: true,
  execution_failed: false,
  status: 'FINALIZED',
  ...overrides,
});

const child = (overrides = {}) => ({
  hash: '0xchild',
  exact_origin_recipient_value: true,
  finalized: true,
  execution_succeeded: true,
  authoritative_credit: true,
  status_conflict: false,
  receipt_failed: false,
  failed: false,
  receipt_acceptable: true,
  ...overrides,
});

test('requires exact finalized child credit for delivery verification', () => {
  const result = classifyDelivery({parent: parent(), children: [child()]});
  assert.equal(result.status, DELIVERY_STATES.DELIVERY_VERIFIED);
  assert.equal(result.child_hash, '0xchild');
});

test('a finalized successful parent without a child remains parent-finalized', () => {
  const result = classifyDelivery({parent: parent(), children: []});
  assert.equal(result.status, DELIVERY_STATES.PARENT_FINALIZED);
});

test('a matching child that is still pending remains transfer-submitted', () => {
  const result = classifyDelivery({parent: parent(), children: [child({finalized: false})]});
  assert.equal(result.status, DELIVERY_STATES.TRANSFER_SUBMITTED);
});

test('an authoritative matching child receipt failure is failed', () => {
  const result = classifyDelivery({parent: parent(), children: [child({receipt_failed: true, authoritative_credit: false})]});
  assert.equal(result.status, DELIVERY_STATES.FAILED);
});

test('missing value_credited evidence is unresolved, never verified', () => {
  const result = classifyDelivery({parent: parent(), children: [child({authoritative_credit: false})]});
  assert.equal(result.status, DELIVERY_STATES.UNRESOLVED);
});

test('rate-limited parent receipt is unresolved, while method absence stays explicit', () => {
  const rateLimited = classifyDelivery({
    parent: parent({receipt_unavailable: true, receipt_category: 'rate_limited'}),
    children: [child()],
  });
  assert.equal(rateLimited.status, DELIVERY_STATES.UNRESOLVED);
  assert.match(rateLimited.reasons[0], /rate_limited/);

  const unsupported = classifyDelivery({
    parent: parent(),
    children: [child({receipt_acceptable: true})],
  });
  assert.equal(unsupported.status, DELIVERY_STATES.DELIVERY_VERIFIED);
});

test('status disagreement and wrong parent destination quarantine the result', () => {
  assert.equal(
    classifyDelivery({parent: parent({status_conflict: true}), children: [child()]}).status,
    DELIVERY_STATES.UNRESOLVED,
  );
  assert.equal(
    classifyDelivery({parent: parent({destination_matches: false}), children: [child()]}).status,
    DELIVERY_STATES.UNRESOLVED,
  );
});

test('failed parent cannot be converted into a payout by a positive child', () => {
  const result = classifyDelivery({parent: parent({failed: true}), children: [child()]});
  assert.equal(result.status, DELIVERY_STATES.FAILED);
});
