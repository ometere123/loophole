'use client';
import Link from 'next/link';import {usePathname} from 'next/navigation';import {useState} from 'react';
import {Menu,X,Wallet,ArrowUpRight,TriangleAlert,ChevronDown,Power,CheckCircle2} from 'lucide-react';
import {useWallet} from './Providers';import {short,READY} from '@/lib/helpers';
export function Header(){const path=usePathname(),{account,chain,connect,switchChain,disconnect,busy}=useWallet();const [open,setOpen]=useState(false),[err,setErr]=useState('');
 const items=[['/','Explore'],['/create','Create challenge'],['/v2','Policy repair'],['/how-it-works','How it works'],['/profile','My vault']];
 const action=async()=>{try{setErr('');if(!account)await connect();else if(chain!==61999)await switchChain();else disconnect();}catch(e){setErr((e as Error).message);}};
 return <><header className="site-header"><div className="header-inner"><Link href="/" className="brand" aria-label="Loophole home"><span className="brand-mark"><span className="brand-eye"/><span className="brand-eye"/><span className="brand-smile"/></span><span>loop<span className="brand-alt">hole</span><span className="brand-dot">.</span></span></Link>
 <nav className={`nav-links ${open?'expanded':''}`} aria-label="Main navigation">{items.map(([href,label])=><Link onClick={()=>setOpen(false)} href={href} key={href} className={path===href?'active':''}>{label}</Link>)}</nav>
 <div className="header-right"><span className="network-pill"><span className="online-dot"/>{chain&&chain!==61999?'Wrong network':'Studionet'}</span><button type="button" onClick={action} disabled={busy} className={`wallet-button ${account&&chain!==61999?'wrong':''}`}>{account&&chain!==61999?<TriangleAlert size={17}/>:<Wallet size={17}/>}<span>{!account?'Connect wallet':chain!==61999?'Switch network':short(account)}</span><ChevronDown size={14}/></button><button className="menu-toggle" onClick={()=>setOpen(!open)} aria-label="Toggle menu">{open?<X/>:<Menu/>}</button></div></div></header>
 {!READY&&<div className="deployment-bar"><TriangleAlert size={15}/> <span>Deployment not configured. Live actions remain disabled until the Loophole address is set.</span></div>}
 {err&&<div className="global-alert" role="alert">{err}<button onClick={()=>setErr('')} aria-label="Dismiss"><X size={16}/></button></div>}
 </>;
}
