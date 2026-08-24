import { NextResponse } from "next/server";
import { fetchOkxTickers } from "../../../lib/market";
export const runtime="nodejs";
export const dynamic="force-dynamic";
export const maxDuration=30;
const MAJORS=["BTC/IRT","ETH/IRT","USDT/IRT","BNB/IRT","SOL/IRT","XRP/IRT","DOGE/IRT","ADA/IRT","AVAX/IRT","LINK/IRT","TON/IRT","TRX/IRT","DOT/IRT","LTC/IRT","BCH/IRT"];

async function directTabdeal(symbol:string){
 const base="https://api1.tabdeal.org/r/api/v1";
 const controller=new AbortController();
 const timer=setTimeout(()=>controller.abort(),6000);
 try{
  const r=await fetch(`${base}/trades?symbol=${encodeURIComponent(symbol)}&limit=10`,{cache:"no-store",signal:controller.signal});
  if(!r.ok) throw new Error(`HTTP ${r.status}`);
  const json=await r.json();
  const rows=Array.isArray(json)?json:Array.isArray(json?.data)?json.data:[];
  if(!rows.length) return null;
  const last=Number(rows[0]?.price);
  const first=Number(rows[rows.length-1]?.price);
  if(!Number.isFinite(last)||last<=0)return null;
  const quoteVolume=rows.reduce((s:number,x:any)=>s+(Number(x.quoteQty)||Number(x.price)*Number(x.qty)||0),0);
  return {symbol:symbol.replace("_","/"),last,changePct:first?((last-first)/first)*100:0,quoteVolume};
 }finally{clearTimeout(timer)}
}

export async function GET(){
 try{
  let tickers=await fetchOkxTickers();
  // اگر discovery بازارها به هر دلیل شکست خورد، چند بازار شناخته‌شده IRT را مستقیم تست کن.
  if(!tickers.length){
   const fallback=await Promise.all(["BTC_IRT","ETH_IRT","USDT_IRT","SOL_IRT","XRP_IRT","DOGE_IRT"].map(s=>directTabdeal(s).catch(()=>null)));
   tickers=fallback.filter(Boolean) as any[];
  }
  const bySymbol=new Map(tickers.map(t=>[t.symbol,t]));
  const majors=MAJORS.map(sym=>{const t=bySymbol.get(sym);if(!t)return null;return {symbol:t.symbol,price:t.last,changePct:Math.round(t.changePct*100)/100,quoteVolume:Math.round(t.quoteVolume)};}).filter(Boolean);
  const top=tickers.slice(0,40).map(t=>({symbol:t.symbol,price:t.last,changePct:Math.round(t.changePct*100)/100,quoteVolume:t.quoteVolume,bid:t.bid,ask:t.ask}));
  const gainers=[...tickers].sort((a,b)=>b.changePct-a.changePct).slice(0,8);
  const losers=[...tickers].sort((a,b)=>a.changePct-b.changePct).slice(0,8);
  return NextResponse.json({updatedAt:new Date().toISOString(),count:tickers.length,majors,symbols:top,gainers:gainers.map(t=>({symbol:t.symbol,changePct:t.changePct,price:t.last})),losers:losers.map(t=>({symbol:t.symbol,changePct:t.changePct,price:t.last})),live:tickers.length>0,exchange:"tabdeal",quote:"IRT",source:"tabdeal-irt",diagnostic:{received:tickers.length>0}});
 }catch(e){
  const fallback=await Promise.all(["BTC_IRT","ETH_IRT","USDT_IRT","SOL_IRT"].map(s=>directTabdeal(s).catch(()=>null)));
  const tickers=fallback.filter(Boolean) as any[];
  return NextResponse.json({updatedAt:new Date().toISOString(),count:tickers.length,majors:tickers,symbols:tickers,gainers:tickers,losers:tickers,live:tickers.length>0,exchange:"tabdeal",quote:"IRT",source:"tabdeal-irt",error:String(e),diagnostic:{received:tickers.length>0}},{status:200});
 }
}
