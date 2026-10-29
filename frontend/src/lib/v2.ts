import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionHashVariant } from 'genlayer-js/types';
import { readV2, resolvePinnedGithubSource } from 'loophole/sdk';
import type { CalldataEncodable } from 'genlayer-js/types';
import type { V2AuditHistory } from './types';

export const V2_ADDRESS = process.env.NEXT_PUBLIC_LOOPHOLE_V2_ADDRESS || '';
export const V2_READY = /^0x[a-fA-F0-9]{40}$/.test(V2_ADDRESS);
const client = createClient({ chain: studionet });

function requireV2() {
  if (!V2_READY) throw new Error('The V2 contract is not deployed/configured yet.');
}

function parse<T>(value: unknown): T | null {
  if (value === '' || value === null || value === undefined) return null;
  return (typeof value === 'string' ? JSON.parse(value) : value) as T;
}

export async function readV2Contract(functionName: string, args: CalldataEncodable[] = []) {
  requireV2();
  return client.readContract({
    address: V2_ADDRESS as `0x${string}`,
    functionName,
    args,
    transactionHashVariant: TransactionHashVariant.LATEST_FINAL,
  });
}

export async function fetchV2Config() {
  const read = ({ functionName, args }: { functionName: string; args: unknown[] }) => readV2Contract(functionName, args as CalldataEncodable[]);
  return parse<Record<string, string>>(await readV2(read, 'get_config'));
}

export async function fetchV2Audit(challengeId: string): Promise<V2AuditHistory | null> {
  if (!/^\d+$/.test(challengeId)) throw new Error('Challenge IDs must be positive integers.');
  const read = ({ functionName, args }: { functionName: string; args: unknown[] }) => readV2Contract(functionName, args as CalldataEncodable[]);
  return parse<V2AuditHistory>(await readV2(read, 'get_audit_history', [BigInt(challengeId)]));
}

export async function resolveV2GithubSource(input: { owner: string; repo: string; commit: string; path: string; versionMarker?: string }) {
  return resolvePinnedGithubSource(input);
}
