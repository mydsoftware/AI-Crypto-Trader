"use client";

import { useEffect, useState } from "react";

type Opportunity = { symbol: string; score: number; action: string; confidence: number; entry: number | null; stopLoss: number | null; tp1: number | null; tp2: number | null; riskReward: number | null; reasons: string[] };

const fmt = (v: number | null) => v == null ? "—" : v.toLocaleString("en-US", { maximumFractionDigits: 8 });

export default function Home() {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [updated, setUpdated] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [message, setMessage] = useState("");

  async function load() {
    try {
      const res = await fetch("/api/opportunities", { cache: "no-store" });
      const data = await res.json();
      setItems(data.opportunities || []);
      setUpdated(data.updatedAt || "");
      setLive(Boolean(data.live));
      setMessage(data.message || "");
    } catch {
      setItems([]); setLive(false); setMessage("ارتباط با موتور تحلیل برقرار نشد.");
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); const timer = setInterval(load, 120000); return () => clearInterval(timer); }, []);

  return <main dir="rtl"><div className="shell">
    <header><div><span className="badge">PACT-OS</span><h1>🔥 بهترین فرصت‌های خرید</h1><p>دستیار معامله‌گری — تحلیل و پیشنهاد، بدون اجرای خودکار معامله</p></div><div className={live ? "status live" : "status"}>● {live ? "داده زنده" : "در انتظار داده"}</div></header>
    <div className="meta"><span>آخرین بروزرسانی: {updated ? new Date(updated).toLocaleTimeString("fa-IR") : "—"}</span><button onClick={() => { setLoading(true); load(); }}>بروزرسانی</button></div>
    {message && !live && <div className="info">ℹ️ {message}</div>}
    {loading ? <div className="empty">در حال اسکن بازار و رتبه‌بندی فرصت‌ها...</div> : items.length === 0 ? <div className="empty"><strong>🟡 فعلاً فرصت خرید با کیفیت مناسب پیدا نشد.</strong><span>بهتر است منتظر شکل‌گیری شرایط بهتر بمانید.</span></div> : <section className="grid">{items.map((o, i) => <article className="card" key={`${o.symbol}-${i}`}>
      <div className="top"><div><span className="rank">#{i + 1}</span><h2>{o.symbol}</h2></div><div className="score">{o.score}<small>/100</small></div></div>
      <div className="buy">🟢 {o.action === "BUY" ? "خرید" : o.action}</div>
      <div className="stats"><div><b>اعتماد</b><strong>{o.confidence}%</strong></div><div><b>ورود</b><strong>{fmt(o.entry)}</strong></div><div><b>حد ضرر</b><strong>{fmt(o.stopLoss)}</strong></div><div><b>TP1</b><strong>{fmt(o.tp1)}</strong></div><div><b>TP2</b><strong>{fmt(o.tp2)}</strong></div><div><b>R/R</b><strong>{o.riskReward == null ? "—" : `1:${o.riskReward.toFixed(2)}`}</strong></div></div>
      <div className="why"><h3>چرا این فرصت انتخاب شده؟</h3><ul>{o.reasons?.map((r, j) => <li key={j}>✓ {r}</li>)}</ul></div>
      <div className="warning">⚠️ این اطلاعات توصیه مالی نیست. تصمیم نهایی معامله با کاربر است.</div>
    </article>)}</section>}
  </div><style jsx>{`*{box-sizing:border-box}body{margin:0;background:#07111f;color:#e8eef7;font-family:Tahoma,Arial,sans-serif}.shell{max-width:1180px;margin:auto;padding:30px 18px}header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}.badge{font-size:12px;border:1px solid #29415d;border-radius:20px;padding:6px 10px;color:#78b7ff}h1{font-size:32px;margin:16px 0 8px}header p{color:#91a4ba;margin:0}.status{padding-top:9px;color:#f0c674;font-size:13px}.status.live{color:#63e6a7}.meta{display:flex;justify-content:space-between;align-items:center;margin:26px 0 14px;color:#91a4ba;font-size:13px}.meta button{background:#153453;border:1px solid #29415d;color:#dbeafe;border-radius:10px;padding:9px 14px;cursor:pointer}.info,.empty{border:1px solid #29415d;background:#0b1828;border-radius:16px;padding:20px;margin-top:15px}.empty{text-align:center;display:flex;flex-direction:column;gap:8px;color:#aebfd2}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px}.card{background:#0b1828;border:1px solid #1b3047;border-radius:20px;padding:20px;box-shadow:0 10px 30px #0003}.top{display:flex;justify-content:space-between;align-items:center}.top h2{display:inline;margin:0 0 0 10px;font-size:22px}.rank{color:#78b7ff;font-weight:bold}.score{font-size:30px;font-weight:bold;color:#63e6a7}.score small{font-size:12px;color:#91a4ba}.buy{margin:16px 0;font-size:18px;font-weight:bold}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.stats div{background:#101f31;border-radius:12px;padding:10px}.stats b{display:block;color:#91a4ba;font-size:11px;margin-bottom:5px}.stats strong{font-size:13px}.why{margin-top:18px}.why h3{font-size:14px}.why ul{list-style:none;padding:0;margin:0;display:grid;gap:7px;color:#c8d6e5;font-size:13px}.warning{margin-top:16px;background:#211d17;color:#f0c674;border-radius:10px;padding:10px;font-size:11px}@media(max-width:650px){h1{font-size:24px}.shell{padding:20px 12px}.grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}`}</style></main>;
}
