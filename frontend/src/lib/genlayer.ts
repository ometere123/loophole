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
function requireDeployment(){if(!READY)throw new Error('The Loophole contract is not deployed/configured. Set NEXT_PUBLIC_LOOPHOLE_ADDRESS.');}
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
type RpcFailureCategory='unsupported'|'rate_limited'|'temporary_failure'|'error';
type RpcProbe={supported:true;result:any}|{supported:false;category:RpcFailureCategory;error:string};
type RpcError=Error & {rpcCode?:number;httpStatus?:number};
async function rawRpc(method:string,params:unknown[]){
 let response:Response;
 try{response=await fetch(deliveryRpc,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:Date.now(),method,params})});}
 catch(e){const error=new Error(`${method}: ${e instanceof Error?e.message:String(e)}`) as RpcError;throw error;}
 if(!response.ok){const error=new Error(`${method}: RPC HTTP ${response.status}`) as RpcError;error.httpStatus=response.status;throw error;}
 const body=await response.json() as {result?:unknown;error?:{code?:number;message?:string}};
 if(body.error){const error=new Error(`${method}: ${body.error.message||'RPC error'}`) as RpcError;error.rpcCode=body.error.code;throw error;}
 return body.result as any;
}
function rpcFailureCategory(error:unknown):RpcFailureCategory{
 const e=error as RpcError;const message=String(e?.message||error);
 if(e?.rpcCode===-32601||/method not found/i.test(message))return 'unsupported';
 if(e?.httpStatus===429||e?.rpcCode===-32029||/rate.?limit|too many requests/i.test(message))return 'rate_limited';
 if([408,502,503,504].includes(e?.httpStatus||0)||/timeout|timed out|fetch failed|network|temporar/i.test(message))return 'temporary_failure';
 return 'error';
}
async function probeRpc(method:string,params:unknown[]):Promise<RpcProbe>{try{return {supported:true,result:await rawRpc(method,params)};}catch(error){return {supported:false,category:rpcFailureCategory(error),error:error instanceof Error?error.message:String(error)};}}
type ReceiptExecutionEvidence={execution_result?:string;result?:{status?:string}};
function hasSuccessfulExecution(receipt:GenLayerTransaction):boolean{
  if(receipt.txExecutionResultName)return receipt.txExecutionResultName===ExecutionResult.FINISHED_WITH_RETURN;
  const raw=receipt as GenLayerTransaction & {consensus_data?:{leader_receipt?:ReceiptExecutionEvidence[]};leader_receipt?:ReceiptExecutionEvidence[]};
  const leader=raw.consensus_data?.leader_receipt?.[0]??raw.leader_receipt?.[0];
  return leader?.execution_result==='SUCCESS'&&leader.result?.status==='return';
}
function probeStatus(probe:RpcProbe):string|null{if(!probe.supported)return null;if(typeof probe.result==='string')return probe.result.toUpperCase();if(probe.result&&typeof probe.result.status==='string')return probe.result.status.toUpperCase();return null;}
function lifecycleStatus(tx:any,statusProbe:RpcProbe):string|null{const status=probeStatus(statusProbe)??String(tx?.status_name??tx?.status??'').toUpperCase();return status||null;}
function statusConflict(tx:any,statusProbe:RpcProbe){const a=probeStatus(statusProbe),b=String(tx?.status_name??tx?.status??'').toUpperCase();return Boolean(a&&b&&a!==b);}
function receiptStatus(probe:RpcProbe):string|null{if(!probe.supported||probe.result==null||typeof probe.result!=='object')return null;return probe.result.status==null?null:String(probe.result.status).toLowerCase();}
function receiptSucceeded(probe:RpcProbe):boolean|null{if(!probe.supported||probe.result==null)return null;const status=receiptStatus(probe);return status==='0x1'||status==='1';}
function receiptEvidenceOptional(probe:RpcProbe){return !probe.supported&&probe.category==='unsupported';}
function receiptEvidenceAvailable(probe:RpcProbe){return receiptEvidenceOptional(probe)||(probe.supported&&probe.result!=null);}
function rawFinal(tx:any,statusProbe:RpcProbe){return lifecycleStatus(tx,statusProbe)==='FINALIZED';}
function rawSucceeded(tx:any){const leader=tx?.consensus_data?.leader_receipt?.[0]??tx?.leader_receipt?.[0];return leader?.execution_result==='SUCCESS'&&(leader?.result==='AAA='||leader?.result?.status==='return');}
function childTransferSucceeded(tx:any,receiptProbe:RpcProbe){
 if(tx?.consensus_data||tx?.leader_receipt)return rawSucceeded(tx);
 const receiptOk=receiptSucceeded(receiptProbe);
 return receiptOk===true||(receiptOk===null&&tx?.value_credited===true);
}
function rawFailed(tx:any,statusProbe:RpcProbe){const status=lifecycleStatus(tx,statusProbe);return ['CANCELED','CANCELLED','FAILED','REVERTED'].includes(status??'')||(rawFinal(tx,statusProbe)&&tx?.consensus_data&&rawSucceeded(tx)===false);}
export async function reconcilePersistedTransaction(saved:PersistedTransaction):Promise<TxInfo>{
 const [tx,statusProbe,receiptProbe]=await Promise.all([rawRpc('eth_getTransactionByHash',[saved.hash]),probeRpc('gen_getTransactionStatus',[saved.hash]),probeRpc('eth_getTransactionReceipt',[saved.hash])]);
 if(!tx)return {phase:'unknown',hash:saved.hash,title:saved.title,error:'The transaction hash is not visible from the configured RPC yet. Do not resubmit.'};
 if(!statusProbe.supported&&statusProbe.category!=='unsupported')return {phase:'unknown',hash:saved.hash,title:saved.title,error:`Transaction lifecycle could not be checked (${statusProbe.category}). Do not resubmit.`};
 const status=lifecycleStatus(tx,statusProbe);
 if(statusConflict(tx,statusProbe))return {phase:'unknown',hash:saved.hash,title:saved.title,error:'Transaction lifecycle status conflicts across the configured RPC surfaces. Inspect the explorer before retrying.'};
 if(status==='FINALIZED'){
  if(!receiptEvidenceOptional(receiptProbe)&&(!receiptProbe.supported||receiptProbe.result==null))return {phase:'unknown',hash:saved.hash,title:saved.title,error:`Transaction finalized in GenLayer, but its EVM receipt could not be checked (${receiptProbe.supported?'not returned':receiptProbe.category}).`};
  if(receiptProbe.supported&&receiptSucceeded(receiptProbe)===false)return {phase:'execution_failed',hash:saved.hash,title:saved.title,error:'Finalized, but the EVM receipt reports unsuccessful transport execution.'};
  if(rawSucceeded(tx))return {phase:'finalized',hash:saved.hash,title:saved.title};
  return {phase:'execution_failed',hash:saved.hash,title:saved.title,error:`Finalized, but execution was not verified successful (${tx.result_name??'unknown'}).`};
 }
 if(['CANCELED','CANCELLED','FAILED','REVERTED'].includes(status??''))return {phase:'execution_failed',hash:saved.hash,title:saved.title,error:`Transaction ended ${status}. Do not resubmit without inspecting the contract state.`};
 if(status==='ACCEPTED')return {phase:'accepted',hash:saved.hash,title:saved.title};
 return {phase:'submitted',hash:saved.hash,title:saved.title};
}
export async function verifyWithdrawalDelivery(parentHash:string,beneficiary:string,amountWei:string):Promise<DeliveryVerification>{
 const base={parentHash,beneficiary:beneficiary.toLowerCase(),amountWei,reasons:[],checkedAt:Date.now()} as Omit<DeliveryVerification,'status'>;
 try{
   const chain=String(await rawRpc('eth_chainId',[])).toLowerCase();
   if(chain!=='0xf22f')return {...base,status:'UNRESOLVED',reasons:[`wrong chain: expected 0xf22f, got ${chain}`]};
   const [parent,parentReceiptProbe,parentStatusProbe]=await Promise.all([rawRpc('eth_getTransactionByHash',[parentHash]),probeRpc('eth_getTransactionReceipt',[parentHash]),probeRpc('gen_getTransactionStatus',[parentHash])]);
   if(!parent)return {...base,status:'UNRESOLVED',reasons:['parent transaction is unavailable']};
   const parentStatus=lifecycleStatus(parent,parentStatusProbe),parentReceipt=receiptStatus(parentReceiptProbe);
   const parentBase={...base,parentLifecycleStatus:parentStatus,parentEvmReceiptStatus:parentReceipt};
   if(String(parent.to_address||'').toLowerCase()!==VAULT_ADDRESS.toLowerCase())return {...parentBase,status:'UNRESOLVED',reasons:['parent destination is not the configured Loophole contract']};
   if(statusConflict(parent,parentStatusProbe))return {...parentBase,status:'UNRESOLVED',reasons:['parent lifecycle status conflicts between transaction and gen_getTransactionStatus']};
   if(rawFailed(parent,parentStatusProbe))return {...parentBase,status:'FAILED',reasons:['parent transaction failed or finalized without successful execution']};
   if(parentReceiptProbe.supported&&parentReceiptProbe.result==null)return {...parentBase,status:'UNRESOLVED',reasons:['parent EVM receipt is not available yet']};
   if(!parentReceiptProbe.supported&&!receiptEvidenceOptional(parentReceiptProbe))return {...parentBase,status:'UNRESOLVED',reasons:[`parent EVM receipt could not be checked (${parentReceiptProbe.category})`]};
   if(parentReceiptProbe.supported&&receiptSucceeded(parentReceiptProbe)===false)return {...parentBase,status:'FAILED',reasons:['parent EVM receipt reports unsuccessful transport execution']};
   if(!rawFinal(parent,parentStatusProbe))return {...parentBase,status:'TRANSFER SUBMITTED',reasons:[`parent status is ${parentStatus||'unknown'}`]};
   if(!rawSucceeded(parent))return {...parentBase,status:'FAILED',reasons:['parent finalized without successful leader return evidence']};
   const children=Array.isArray(parent.triggered_transactions)?parent.triggered_transactions:[];
   const records=await Promise.all(children.map(async(hash:string)=>{const [tx,receiptProbe,statusProbe]=await Promise.all([rawRpc('eth_getTransactionByHash',[hash]),probeRpc('eth_getTransactionReceipt',[hash]),probeRpc('gen_getTransactionStatus',[hash])]);return {hash,tx,receiptProbe,statusProbe};}));
   const exact=records.filter(({tx})=>String(tx?.from_address||'').toLowerCase()===VAULT_ADDRESS.toLowerCase()&&String(tx?.to_address||'').toLowerCase()===beneficiary.toLowerCase()&&String(tx?.value??'')===amountWei);
   if(!exact.length)return {...parentBase,status:'PARENT FINALIZED',reasons:['parent finalized, but no exact external child transfer is visible yet']};
   const failed=exact.find(({tx,statusProbe,receiptProbe})=>rawFailed(tx,statusProbe)||(receiptProbe.supported&&receiptSucceeded(receiptProbe)===false));
   if(failed)return {...parentBase,status:'FAILED',childHash:failed.hash,childLifecycleStatus:lifecycleStatus(failed.tx,failed.statusProbe),childEvmReceiptStatus:receiptStatus(failed.receiptProbe),reasons:['matching child transfer failed or finalized without successful execution']};
   const conflicted=exact.find(({tx,statusProbe})=>statusConflict(tx,statusProbe));
   if(conflicted)return {...parentBase,status:'UNRESOLVED',childHash:conflicted.hash,childLifecycleStatus:lifecycleStatus(conflicted.tx,conflicted.statusProbe),childEvmReceiptStatus:receiptStatus(conflicted.receiptProbe),reasons:['matching child lifecycle status conflicts between transaction and gen_getTransactionStatus']};
   const blocked=exact.find(({tx,statusProbe,receiptProbe})=>rawFinal(tx,statusProbe)&&!receiptEvidenceAvailable(receiptProbe));
   if(blocked)return {...parentBase,status:'UNRESOLVED',childHash:blocked.hash,childLifecycleStatus:lifecycleStatus(blocked.tx,blocked.statusProbe),childEvmReceiptStatus:receiptStatus(blocked.receiptProbe),reasons:[`matching child is finalized, but its EVM receipt evidence is unavailable (${blocked.receiptProbe.supported?'not returned':blocked.receiptProbe.category})`]};
   const pending=exact.find(({tx,statusProbe})=>!rawFinal(tx,statusProbe));
   if(pending)return {...parentBase,status:'TRANSFER SUBMITTED',childHash:pending.hash,childLifecycleStatus:lifecycleStatus(pending.tx,pending.statusProbe),childEvmReceiptStatus:receiptStatus(pending.receiptProbe),reasons:['matching child transfer is not finalized']};
   const credited=exact.find(({tx,statusProbe,receiptProbe})=>rawFinal(tx,statusProbe)&&childTransferSucceeded(tx,receiptProbe)&&tx?.value_credited===true&&receiptEvidenceAvailable(receiptProbe)&&!(receiptProbe.supported&&receiptSucceeded(receiptProbe)===false));
   if(credited)return {...parentBase,status:'DELIVERY VERIFIED',childHash:credited.hash,childLifecycleStatus:lifecycleStatus(credited.tx,credited.statusProbe),childEvmReceiptStatus:receiptStatus(credited.receiptProbe),reasons:[]};
   return {...parentBase,status:'UNRESOLVED',reasons:['matching child finalized without authoritative successful value_credited evidence']};
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
