'use client';
import React,{createContext,useContext,useEffect,useState,useCallback} from 'react';
import {CheckCircle2,AlertTriangle,LoaderCircle,Wallet,ExternalLink,X,RefreshCcw} from 'lucide-react';
import {connectWallet,getWalletState,reconcilePersistedTransaction,switchStudionet,writeVault} from '@/lib/genlayer';
import {clearPersistedTransaction,explorerTx,getPendingTransaction,READY,short} from '@/lib/helpers';
import type {TxInfo} from '@/lib/types';

type Context = {account:string;chain:number;connect:()=>Promise<void>;switchChain:()=>Promise<void>;disconnect:()=>void;submit:(method:string,args:unknown[],value?:bigint)=>Promise<string>;busy:boolean;tx:TxInfo;setTx:(x:TxInfo)=>void;refreshWallet:()=>Promise<void>};
const C=createContext<Context|null>(null);
export function useWallet(){const v=useContext(C);if(!v)throw new Error('WalletProvider missing');return v;}
const EMPTY:TxInfo={phase:'idle'};
export function Providers({children}:{children:React.ReactNode}){
 const [account,setAccount]=useState('');const [chain,setChain]=useState(0);
 const [tx,setTx]=useState<TxInfo>(EMPTY);const [busy,setBusy]=useState(false);
 const refreshWallet=useCallback(async()=>{try{const state=await getWalletState();setAccount(state.account);setChain(state.chain);const saved=state.account?getPendingTransaction(state.account):null;if(!saved){setTx(EMPTY);return;}setTx({phase:saved.phase,hash:saved.hash,title:saved.title,error:saved.error});try{const live=await reconcilePersistedTransaction(saved);if(live.phase==='finalized')clearPersistedTransaction(saved.hash);setTx(live);}catch{/* Keep the persisted state when the RPC is temporarily unavailable. */}}catch{setAccount('');setChain(0);}},[]);
 useEffect(()=>{refreshWallet();const p=window.ethereum;const cb=()=>{setTx(EMPTY);refreshWallet();};p?.on?.('accountsChanged',cb);p?.on?.('chainChanged',cb);p?.on?.('disconnect',cb);return()=>{p?.removeListener?.('accountsChanged',cb);p?.removeListener?.('chainChanged',cb);p?.removeListener?.('disconnect',cb);};},[refreshWallet]);
 const connect=async()=>{const a=await connectWallet();setAccount(a);await refreshWallet();};
 const switchChain=async()=>{await switchStudionet();await refreshWallet();};
 const disconnect=()=>{setAccount('');setChain(0);setTx(EMPTY);};
 const submit=async(method:string,args:unknown[],value?:bigint)=>{
  if(busy)throw new Error('Another transaction is in progress.');
  if(!account)throw new Error('Connect a wallet to continue.');
  if(chain!==61999)throw new Error('Switch to Studionet 61999 before writing.');
  if(!READY)throw new Error('Deployment addresses must be configured first.');
  setBusy(true);try{return await writeVault(method,args,value,account,setTx);}catch(e){setTx(prev=>prev.phase==='unknown'||prev.phase==='execution_failed'?prev:{phase:prev.hash?'unknown':'rejected',hash:prev.hash,title:method,error:(e as Error).message});throw e;}finally{setBusy(false);}
 };
 return <C.Provider value={{account,chain,connect,switchChain,disconnect,submit,busy,tx,setTx,refreshWallet}}>{children}<TransactionDrawer/></C.Provider>;
}
function TransactionDrawer(){const {tx,setTx}=useWallet();if(tx.phase==='idle')return null;
 const steps=['awaiting_wallet','submitted','accepted','finalized'];const current=steps.indexOf(tx.phase);
 return <aside className="tx-drawer" role="status" aria-live="polite">
  <button className="icon-button tx-close" onClick={()=>setTx(EMPTY)} aria-label="Close transaction panel"><X size={19}/></button>
  <div className="eyebrow">TRANSACTION TRACKER <span className="online-dot"/></div>
  <h3>{tx.phase==='finalized'?'Transaction finalized!':tx.phase==='execution_failed'?'Execution not verified':tx.phase==='unknown'?'Check your transaction':tx.phase==='rejected'?'Action was not submitted':tx.phase==='awaiting_wallet'?'Confirm in wallet': 'Your transaction is moving'}</h3>
  <p className="muted">{tx.title?.replaceAll('_',' ')} · {tx.phase==='finalized'?'Check the contract again for any follow-up child transaction.':tx.phase==='rejected'?'No transaction hash was issued.':'A signed submission is not a completed payout.'}</p>
  <div className="tx-progress">{steps.map((s,i)=><div key={s} className={`tx-step ${tx.phase==='finalized'||(current>=i&&current!==-1)?'done':''}`}><span>{tx.phase==='finalized'||(current>=i&&current!==-1)?<CheckCircle2 size={16}/>:i===current+1?<LoaderCircle size={16}/>:<span className="tiny-circle"/>}</span><small>{s==='awaiting_wallet'?'Wallet approval':s==='submitted'?'Broadcast':s==='accepted'?'Accepted':'Finalized + checked'}</small></div>)}</div>
  {tx.error&&<div className="notice danger"><AlertTriangle size={17}/>{tx.error}</div>}
  {tx.hash&&<a target="_blank" rel="noopener noreferrer" className="link-arrow" href={explorerTx(tx.hash)}>Inspect on explorer <ExternalLink size={15}/></a>}
 </aside>;
}
