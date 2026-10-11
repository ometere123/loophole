import type { Category, CommitmentBackup, PersistedTransaction, WithdrawalProvenance } from './types';
export const CHAIN_ID = 61999;
export const CHAIN_HEX = '0xf22f';
export const VAULT_ADDRESS = process.env.NEXT_PUBLIC_RULE_VAULT_ADDRESS || '';
export const JUDGE_ADDRESS = process.env.NEXT_PUBLIC_GAP_JUDGE_ADDRESS || '';
export const EXPLORER = process.env.NEXT_PUBLIC_STUDIONET_EXPLORER || 'https://explorer-studio.genlayer.com';
export const READY = /^0x[a-fA-F0-9]{40}$/.test(VAULT_ADDRESS) && /^0x[a-fA-F0-9]{40}$/.test(JUDGE_ADDRESS);
export const isAddress = (s:string): boolean => /^0x[a-fA-F0-9]{40}$/.test(s);
export const short = (s?:string) => s ? `${s.slice(0,6)}…${s.slice(-4)}` : '';
export function fromWei(s:string|bigint) { const v=BigInt(s||'0'); return (Number(v/10n**14n)/1e4).toLocaleString('en-US',{maximumFractionDigits:4}); }
export function toWei(s:string) { if(!/^\d+(\.\d{1,18})?$/.test(s.trim())) throw new Error('Enter a positive GEN amount (up to 18 decimals).'); const [whole,frac='']=s.split('.'); return BigInt(whole)*10n**18n + BigInt(frac.padEnd(18,'0')); }
export function timeLeft(end:number, now=Date.now()/1000) {const diff=end-now; if(diff<=0)return 'Closed';const d=Math.floor(diff/86400),h=Math.floor(diff%86400/3600);return d?`${d}d ${h}h left`:`${Math.max(1,h)}h left`;}
export function dateFormat(n:number) {return new Date(n*1000).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});}
export const categories: {id: Category; label:string; emoji:string}[] = [
 {id:'COMMUNITY',label:'Community',emoji:'🌈'}, {id:'CONTENT',label:'Content',emoji:'✏️'},
 {id:'REFERRAL',label:'Referrals',emoji:'🎯'}, {id:'GOVERNANCE',label:'Governance',emoji:'🗳️'}, {id:'OTHER',label:'Wildcard',emoji:'✨'}
];
export function categoryOf(s: string) {return categories.find(c=>c.id===s)||categories[4];}
export function saveBackup(b:CommitmentBackup){if(typeof window==='undefined')return;localStorage.setItem(`loophole:${b.address.toLowerCase()}:${b.commitment}`, JSON.stringify(b));}
export function getBackups(address:string):CommitmentBackup[]{if(typeof window==='undefined')return[];const out:CommitmentBackup[]=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i)||'';if(k.startsWith(`loophole:${address.toLowerCase()}:`)){try{out.push(JSON.parse(localStorage.getItem(k)||''));}catch{}}}return out.sort((a,b)=>b.savedAt-a.savedAt);}
export function deleteBackup(b:CommitmentBackup){if(typeof window!=='undefined')localStorage.removeItem(`loophole:${b.address.toLowerCase()}:${b.commitment}`);}
function withdrawalKey(address:string,id:string){return `loophole:withdrawal:${address.toLowerCase()}:${id}`;}
export function saveWithdrawalProvenance(p:WithdrawalProvenance){if(typeof window!=='undefined')localStorage.setItem(withdrawalKey(p.beneficiary,p.withdrawalId),JSON.stringify(p));}
export function getWithdrawalProvenance(address:string,id:string):WithdrawalProvenance|null{if(typeof window==='undefined')return null;try{const raw=localStorage.getItem(withdrawalKey(address,id));return raw?JSON.parse(raw) as WithdrawalProvenance:null;}catch{return null;}}
const txKey='loophole:transactions';
export function savePersistedTransaction(tx:PersistedTransaction){if(typeof window==='undefined')return;const all=getPersistedTransactions().filter(x=>x.hash!==tx.hash);localStorage.setItem(txKey,JSON.stringify([tx,...all].slice(0,20)));}
export function getPersistedTransactions():PersistedTransaction[]{if(typeof window==='undefined')return[];try{const raw=localStorage.getItem(txKey);return raw?JSON.parse(raw) as PersistedTransaction[]:[];}catch{return[];}}
export function getPendingTransaction(address:string):PersistedTransaction|null{return getPersistedTransactions().find(x=>x.account.toLowerCase()===address.toLowerCase())||null;}
export function clearPersistedTransaction(hash:string){if(typeof window==='undefined')return;localStorage.setItem(txKey,JSON.stringify(getPersistedTransactions().filter(x=>x.hash!==hash)));}
export async function makeCommitment(cid:string,address:string,salt:string,scenario:string,quote:string,impact:string){const raw=[cid,address.toLowerCase(),salt,scenario,quote,impact].join('|');const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw));return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');}
export function randomSalt(){const a=crypto.getRandomValues(new Uint8Array(32));return Array.from(a,x=>x.toString(16).padStart(2,'0')).join('');}
export function explorerTx(hash:string){return `${EXPLORER}/tx/${encodeURIComponent(hash)}`;}
export function explorerAddress(address:string){return `${EXPLORER}/address/${encodeURIComponent(address)}`;}
