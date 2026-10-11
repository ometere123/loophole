import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { ExecutionResult, TransactionHashVariant, TransactionStatus } from 'genlayer-js/types';
import type { CalldataEncodable, GenLayerTransaction } from 'genlayer-js/types';
import { clearPersistedTransaction, savePersistedTransaction, VAULT_ADDRESS, READY } from './helpers';
import type { Attempt, Challenge, DeliveryVerification, DeliveryStatus, PersistedTransaction, TxInfo, VaultConfig } from './types';

export interface EIP1193 {request(args:{method:string;params?:unknown[]}):Promise<unknown>;on?(e:string,fn:(...args:any[])=>void):void;removeListener?(e:string,fn:(...args:any[])=>void):void;}
declare global {interface Window {ethereum?:EIP1193;}}
const readClient = createClient({chain:studionet});
const addr = VAULT_ADDRESS as `0x${string}`;
function requireDeployment(){if(!READY)throw new Error('Contracts are not deployed/configured. Set both public contract addresses.');}
function parseRecord<T>(data:unknown):T|null{if(!data||data==='')return null;const parsed=typeof data==='string'? JSON.parse(data): data;return parsed as T;}
export async function readVault(functionName:string,args:CalldataEncodable[]=[]):Promise<CalldataEncodable>{
  requireDeployment();
  return readClient.readContract({address:addr,functionName,args,transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
}
export async function fetchConfig():Promise<VaultConfig|null>{return parseRecord(await readVault('get_config'));}
export async function fetchChallenge(id:string):Promise<Challenge|null>{return parseRecord(await readVault('get_challenge',[BigInt(id)]));}
export async function fetchAttempt(id:string):Promise<Attempt|null>{return parseRecord(await readVault('get_attempt',[BigInt(id)]));}
export async function fetchCredit(address:string):Promise<bigint>{return BigInt(String(await readVault('get_credit',[address])));}
export async function fetchWithdrawal(id:string){return parseRecord<Record<string,string|number>>(await readVault('get_withdrawal',[BigInt(id)]));}
export async function fetchWithdrawals(count:number){const out:Record<string,string|number>[]=[];for(let end=count;end>0;end=Math.max(0,end-24)){const page=parseRecord<string[]>(await readVault('get_withdrawals_page',[BigInt(end),BigInt(Math.min(24,end))]))||[];out.push(...page.map(item=>JSON.parse(item) as Record<string,string|number>));}return out;}
export async function fetchChallenges():Promise<Challenge[]>{const cfg=await fetchConfig();const count=Number(cfg?.challenge_count||0);if(count===0)return[];const out:Challenge[]=[];for(let upper=count;upper>0;upper-=24){const raw=await readVault('get_challenges_page',[BigInt(upper),24n]);const page=JSON.parse(String(raw)) as string[];out.push(...page.map(item=>JSON.parse(item) as Challenge));}return out;}
export async function fetchAttempts(ids:string[]):Promise<Attempt[]>{const out=await Promise.all(ids.map(i=>fetchAttempt(i).catch(()=>null)));return out.filter((x):x is Attempt=>!!x);}
const deliveryRpc=process.env.NEXT_PUBLIC_STUDIONET_RPC||'https://studio.genlayer.com/api';
async function rawRpc(method:string,params:unknown[]){const response=await fetch(deliveryRpc,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:Date.now(),method,params})});if(!response.ok)throw new Error(`RPC HTTP ${response.status}`);const body=await response.json() as {result?:unknown;error?:{message?:string}};if(body.error)throw new Error(`${method}: ${body.error.message||'RPC error'}`);return body.result as any;}
type ReceiptExecutionEvidence={execution_result?:string;result?:{status?:string}};
function hasSuccessfulExecution(receipt:GenLayerTransaction):boolean{
  if(receipt.txExecutionResultName)return receipt.txExecutionResultName===ExecutionResult.FINISHED_WITH_RETURN;
  const raw=receipt as GenLayerTransaction & {consensus_data?:{leader_receipt?:ReceiptExecutionEvidence[]};leader_receipt?:ReceiptExecutionEvidence[]};
  const leader=raw.consensus_data?.leader_receipt?.[0]??raw.leader_receipt?.[0];
  return leader?.execution_result==='SUCCESS'&&leader.result?.status==='return';
}
function rawFinal(tx:any){return String(tx?.status??'').toUpperCase()==='FINALIZED';}
function rawSucceeded(tx:any){const leader=tx?.consensus_data?.leader_receipt?.[0]??tx?.leader_receipt?.[0];return leader?.execution_result==='SUCCESS'&&(leader?.result==='AAA='||leader?.result?.status==='return');}
function rawFailed(tx:any){const status=String(tx?.status??'').toUpperCase();return ['CANCELED','CANCELLED','FAILED','REVERTED'].includes(status)||(rawFinal(tx)&&tx?.consensus_data&&rawSucceeded(tx)===false);}
export async function reconcilePersistedTransaction(saved:PersistedTransaction):Promise<TxInfo>{
 const tx=await rawRpc('eth_getTransactionByHash',[saved.hash]);
 if(!tx)return {phase:'unknown',hash:saved.hash,title:saved.title,error:'The transaction hash is not visible from the configured RPC yet. Do not resubmit.'};
 const status=String(tx.status_name??tx.status??'').toUpperCase();
 if(status==='FINALIZED'){
  if(rawSucceeded(tx))return {phase:'finalized',hash:saved.hash,title:saved.title};
  return {phase:'execution_failed',hash:saved.hash,title:saved.title,error:`Finalized, but execution was not verified successful (${tx.result_name??'unknown'}).`};
 }
 if(['CANCELED','CANCELLED','FAILED','REVERTED'].includes(status))return {phase:'execution_failed',hash:saved.hash,title:saved.title,error:`Transaction ended ${status}. Do not resubmit without inspecting the contract state.`};
 if(status==='ACCEPTED')return {phase:'accepted',hash:saved.hash,title:saved.title};
 return {phase:'submitted',hash:saved.hash,title:saved.title};
}
export async function verifyWithdrawalDelivery(parentHash:string,beneficiary:string,amountWei:string):Promise<DeliveryVerification>{
 const base={parentHash,beneficiary:beneficiary.toLowerCase(),amountWei,reasons:[],checkedAt:Date.now()} as Omit<DeliveryVerification,'status'>;
 try{
  const chain=String(await rawRpc('eth_chainId',[])).toLowerCase();
  if(chain!=='0xf22f')return {...base,status:'UNRESOLVED',reasons:[`wrong chain: expected 0xf22f, got ${chain}`]};
  const parent=await rawRpc('eth_getTransactionByHash',[parentHash]);
  if(!parent)return {...base,status:'UNRESOLVED',reasons:['parent transaction is unavailable']};
  if(String(parent.to_address||'').toLowerCase()!==VAULT_ADDRESS.toLowerCase())return {...base,status:'UNRESOLVED',reasons:['parent destination is not the canonical RuleVault']};
  if(rawFailed(parent))return {...base,status:'FAILED',reasons:['parent transaction failed or finalized without successful execution']};
  if(!rawFinal(parent))return {...base,status:'TRANSFER SUBMITTED',reasons:[`parent status is ${parent.status||'unknown'}`]};
  if(!rawSucceeded(parent))return {...base,status:'FAILED',reasons:['parent finalized without successful leader return evidence']};
  const children=Array.isArray(parent.triggered_transactions)?parent.triggered_transactions:[];
  const records=await Promise.all(children.map(async(hash:string)=>({hash,tx:await rawRpc('eth_getTransactionByHash',[hash])})));
  const exact=records.filter(({tx})=>String(tx?.from_address||'').toLowerCase()===VAULT_ADDRESS.toLowerCase()&&String(tx?.to_address||'').toLowerCase()===beneficiary.toLowerCase()&&String(tx?.value??'')===amountWei);
  if(!exact.length)return {...base,status:'PARENT FINALIZED',reasons:['parent finalized, but no exact external child transfer is visible yet']};
  const failed=exact.find(({tx})=>rawFailed(tx));
  if(failed)return {...base,status:'FAILED',childHash:failed.hash,reasons:['matching child transfer failed or finalized without successful execution']};
  const pending=exact.find(({tx})=>!rawFinal(tx));
  if(pending)return {...base,status:'TRANSFER SUBMITTED',childHash:pending.hash,reasons:['matching child transfer is not finalized']};
  const credited=exact.find(({tx})=>rawFinal(tx)&&rawSucceeded(tx)&&tx?.value_credited===true);
  if(credited)return {...base,status:'DELIVERY VERIFIED',childHash:credited.hash,reasons:[]};
  return {...base,status:'UNRESOLVED',reasons:['matching child finalized without authoritative successful value_credited evidence']};
 }catch(error){return {...base,status:'UNRESOLVED',reasons:[error instanceof Error?error.message:String(error)]};}
}
export async function connectWallet():Promise<string>{const provider=window.ethereum;if(!provider)throw new Error('No injected wallet detected. Install an EIP-1193 wallet extension.');const accounts=await provider.request({method:'eth_requestAccounts'}) as string[];if(!accounts?.[0])throw new Error('Wallet did not provide an account.');return accounts[0];}
export async function getWalletState():Promise<{account:string;chain:number}>{if(typeof window==='undefined'||!window.ethereum)return {account:'',chain:0};const [accounts,chain]=await Promise.all([window.ethereum.request({method:'eth_accounts'}),window.ethereum.request({method:'eth_chainId'})]) as [string[],string];return {account:accounts?.[0]||'',chain:parseInt(chain,16)};}
export async function switchStudionet(){if(!window.ethereum)throw new Error('An injected wallet is required.');try{await window.ethereum.request({method:'wallet_switchEthereumChain',params:[{chainId:'0xf22f'}]});}catch(e:any){if(e?.code!==4902)throw e;await window.ethereum.request({method:'wallet_addEthereumChain',params:[{chainId:'0xf22f',chainName:'GenLayer Studionet',nativeCurrency:{name:'GEN',symbol:'GEN',decimals:18},rpcUrls:['https://studio.genlayer.com/api'],blockExplorerUrls:['https://explorer-studio.genlayer.com']}]});}}
export async function writeVault(method:string,args:unknown[],value:bigint|undefined,address:string,onUpdate:(s:TxInfo)=>void):Promise<string>{
 requireDeployment();if(!window.ethereum)throw new Error('Connect an injected wallet.');
 const state=await getWalletState();if(state.chain!==61999)throw new Error('Wrong network. Switch your wallet to Studionet 61999.');
 if(state.account.toLowerCase()!==address.toLowerCase())throw new Error('Wallet changed. Reconnect before signing.');
 const client=createClient({chain:studionet,account:address as `0x${string}`,provider:window.ethereum as any});
 // Stable Studionet uses the GenLayerJS 1.1.x write API. Deliberately no 61997 fee API here.
 // Do not call client.connect(): genlayer-js 1.1.8 routes that helper through
 // an optional wallet-extension API. The chain is already selected and
 // checked above, so writeContract can use the injected EIP-1193 provider
 // directly through eth_sendTransaction.
 const tx={address:addr,functionName:method,args:args as CalldataEncodable[],value:value??0n};
  onUpdate({phase:'awaiting_wallet',title:method});
 const hash=await client.writeContract(tx);
 const persist=(phase:'submitted'|'accepted'|'unknown'|'execution_failed',error?:string)=>savePersistedTransaction({hash,account:address.toLowerCase(),phase,title:method,error,updatedAt:Date.now()});
 persist('submitted');
  onUpdate({phase:'submitted',hash,title:method});
 try{await readClient.waitForTransactionReceipt({hash,status:TransactionStatus.ACCEPTED});persist('accepted');onUpdate({phase:'accepted',hash,title:method});}catch{/* final receipt remains authoritative */}
 try{
   const receipt:GenLayerTransaction=await readClient.waitForTransactionReceipt({hash,status:TransactionStatus.FINALIZED});
   const outcome=receipt.txExecutionResultName;
   if(!hasSuccessfulExecution(receipt)){
     persist('execution_failed',`Finalized, but execution was not verified successful (${outcome||'unknown'}).`);
     onUpdate({phase:'execution_failed',hash,title:method,error:`Finalized, but execution was not verified successful (${outcome||'unknown'}).`});
     throw new Error(`Execution was not verified: ${outcome||'unknown'}`);
   }
   clearPersistedTransaction(hash);
   onUpdate({phase:'finalized',hash,title:method});
   return hash;
 }catch(err){
   if((err as Error).message.includes('not verified'))throw err;
   persist('unknown','Submitted, but finalization could not be confirmed. Inspect the explorer and refresh before retrying.');
   onUpdate({phase:'unknown',hash,title:method,error:'Submitted, but finalization could not be confirmed. Inspect the explorer and refresh before retrying.'});
   throw new Error(`Transaction ${hash} could not be verified. Do not blindly resubmit.`);
 }
}
