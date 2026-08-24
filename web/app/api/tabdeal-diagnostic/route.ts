import { NextResponse } from "next/server";
export const runtime="nodejs";
export const dynamic="force-dynamic";
export const maxDuration=15;
const BASE="https://api1.tabdeal.org/r/api/v1";
async function probe(path:string){const c=new AbortController();const timer=setTimeout(()=>c.abort(),7000);const started=Date.now();try{const r=await fetch(`${BASE}${path}`,{cache:"no-store",headers:{accept:"application/json","user-agent":"AI-Crypto-Trader/diagnostic"},signal:c.signal});const text=await r.text();let body:any=text;try{body=JSON.parse(text)}catch{}return {url:`${BASE}${path}`,status:r.status,ok:r.ok,contentType:r.headers.get("content-type"),ms:Date.now()-started,body};}catch(e){return {url:`${BASE}${path}`,status:0,ok:false,ms:Date.now()-started,error:e instanceof Error?e.message:String(e)}}finally{clearTimeout(timer)}}
export async function GET(){const exchangeInfo=await probe("/exchangeInfo");const samples=["BTC_IRT","ETH_IRT","USDT_IRT","SOL_IRT"];const trades=await Promise.all(samples.map(s=>probe(`/trades?symbol=${s}&limit=3`)));const depth=await Promise.all(samples.slice(0,2).map(s=>probe(`/depth?symbol=${s}&limit=5`)));return NextResponse.json({ok:exchangeInfo.ok||trades.some(x=>x.ok),testedAt:new Date().toISOString(),base:BASE,exchangeInfo,trades,depth},{status:200});}
