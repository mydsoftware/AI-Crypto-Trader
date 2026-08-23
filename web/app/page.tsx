"use client";
import { useCallback, useEffect, useState } from "react";

type Opp = {
  symbol: string; score: number; action: string; category?: string; confidence: number;
  entry: number | null; stopLoss: number | null; tp1: number | null; tp2: number | null;
  riskReward: number | null; reasons: string[]; warnings?: string[]; direction?: string;
  changePct?: number; liquidity?: number; price?: number;
};
type Brief = { symbol: string; changePct: number; price: number; quoteVolume?: number };
type Pump = { symbol: string; price: number; changePct: number };
type SignalFilter = "ALL" | "BUY" | "SELL";

const fmt = (v: number | null | undefined) =>
  v == null || Number.isNaN(v) ? "—" : v.toLocaleString("en-US", { maximumFractionDigits: 6 });

const catLabel: Record<string, string> = {
  STRONG_BUY: "🔥 خرید قوی", BUY_CANDIDATE: "🟢 نامزد خرید", BUY: "🟢 خرید",
  STRONG_SELL: "🔻 فروش قوی", SELL_CANDIDATE: "🔴 نامزد فروش", SELL: "🔴 فروش",
  PUMP_WATCH: "🚀 پایش پامپ", WAIT: "🟡 انتظار", AVOID: "⛔ اجتناب", HIGH_RISK: "⚠️ ریسک بالا",
};

export default function Home() {
  const [items, setItems] = useState<Opp[]>([]);
  const [pumps, setPumps] = useState<Pump[]>([]);
  const [majors, setMajors] = useState<Brief[]>([]);
  const [gainers, setGainers] = useState<Brief[]>([]);
  const [losers, setLosers] = useState<Brief[]>([]);
  const [updated, setUpdated] = useState("");
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [message, setMessage] = useState("");
  const [source, setSource] = useState("");
  const [showHelp, setShowHelp] = useState(false);
  const [signalFilter, setSignalFilter] = useState<SignalFilter>("ALL");

  const load = useCallback(async () => {
    try {
      const [oppRes, marketRes, pumpRes] = await Promise.all([
        fetch("/api/opportunities", { cache: "no-store" }),
        fetch("/api/market", { cache: "no-store" }),
        fetch("/api/pump-watch", { cache: "no-store" }),
      ]);
      const opp = await oppRes.json();
      const market = await marketRes.json();
      const pump = await pumpRes.json();
      setItems(opp.opportunities || []);
      setUpdated(opp.updatedAt || "");
      setLive(Boolean(opp.live));
      setMessage(opp.message || "");
      setSource(opp.source || "");
      setMajors(market.majors || []);
      setGainers(market.gainers || []);
      setLosers(market.losers || []);
      setPumps(pump.items || []);
    } catch {
      setItems([]); setLive(false); setMessage("ارتباط با موتور تحلیل برقرار نشد.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 90000); return () => clearInterval(t); }, [load]);

  const risks = items.filter((o) => ["STRONG_SELL", "SELL_CANDIDATE", "AVOID", "HIGH_RISK"].includes(o.category || o.action));
  const buySignals = items.filter((o) => {
    const cat = o.category || o.action;
    return ["STRONG_BUY", "BUY_CANDIDATE", "BUY"].includes(cat) || o.direction === "BUY";
  });
  const sellSignals = items.filter((o) => {
    const cat = o.category || o.action;
    return ["STRONG_SELL", "SELL_CANDIDATE", "SELL", "AVOID", "HIGH_RISK"].includes(cat) || o.direction === "SELL";
  });

  const displayed =
    signalFilter === "BUY" ? buySignals
    : signalFilter === "SELL" ? sellSignals
    : items;

  return (
    <main dir="rtl"><div className="shell">
      <header>
        <div>
          <span className="badge">PACT-OS · AI Crypto Assistant</span>
          <h1>🔥 بهترین فرصت‌های فعلی</h1>
          <p>دستیار تصمیم‌گیری — اسکن زنده بازار، بدون معامله خودکار و بدون تضمین سود</p>
        </div>
        <div className="header-actions">
          <div className={live ? "status live" : "status"}>● {live ? `داده زنده${source ? ` (${source})` : ""}` : "در انتظار داده"}</div>
          <button type="button" className="help-btn" onClick={() => setShowHelp(!showHelp)}>
            {showHelp ? "بستن راهنما" : "❓ راهنمای استفاده"}
          </button>
        </div>
      </header>

      {showHelp && (
        <section className="help-box">
          <h2>📖 راهنمای استفاده از داشبورد</h2>
          <ol>
            <li><b>ارزهای اصلی:</b> قیمت لحظه‌ای BTC، ETH، SOL و بقیهٔ بزرگ‌های بازار.</li>
            <li><b>نمای کلی بازار:</b> بیشترین رشد، افت و پایش پامپ (رشد ≥۳٪).</li>
            <li><b>فرصت‌ها:</b> ترکیب چند استراتژی با امتیاز، ورود، حد ضرر و TP.</li>
            <li><b>دکمه سیگنال:</b> فیلتر سریع فقط خرید یا فقط فروش.</li>
            <li><b>بروزرسانی:</b> هر ۹۰ ثانیه خودکار؛ یا دستی با دکمه.</li>
          </ol>

          <h3>📊 معنی امتیاز (Score / 100)</h3>
          <ul>
            <li><b>۸۰–۱۰۰:</b> سیگنال قوی در همان جهت — اگر جهت خرید باشد خرید قوی؛ اگر جهت فروش باشد فشار فروش قوی (نه خرید!).</li>
            <li><b>۶۵–۷۹:</b> نامزد خوب در همان جهت.</li>
            <li><b>۵۰–۶۴:</b> متوسط — منتظر تأیید بیشتر.</li>
            <li><b>زیر ۵۰:</b> ضعیف یا پرریسک → اجتناب.</li>
          </ul>
          <p style={{color:"#f0c674",fontSize:13}}>نکته مهم: امتیاز اندازه‌گیری قدرت سیگنال است، نه فقط قدرت خرید. امتیاز ۱۰۰ + برچسب فروش = اجماع نزولی قوی.</p>

          <h3>🎯 معنی اعتماد (Confidence %)</h3>
          <ul>
            <li>میزان توافق استراتژی‌ها روی جهت.</li>
            <li>بالای ۷۰٪ = اجماع نسبتاً قوی · زیر ۵۰٪ = اختلاف رأی زیاد.</li>
          </ul>

          <h3>📐 نسبت ریسک به ریوارد (R/R)</h3>
          <ul>
            <li><b>۱:۲ یا بهتر:</b> مطلوب‌تر.</li>
            <li>اگر R/R ضعیف است، حتی با امتیاز بالا احتیاط کنید.</li>
          </ul>

          <h3>🏷️ برچسب‌ها</h3>
          <div className="help-labels">
            <span>🔥 خرید قوی</span>
            <span>🟢 نامزد خرید</span>
            <span>🔻 فروش قوی</span>
            <span>🔴 نامزد فروش</span>
            <span>🟡 انتظار</span>
            <span>🚀 پایش پامپ (≠ خرید)</span>
            <span>⚠️ ریسک بالا</span>
            <span>⛔ اجتناب (کیفیت پایین)</span>
          </div>

          <h3>چطور از سیگنال استفاده کنم؟</h3>
          <ul>
            <li>دکمه <b>سیگنال خرید</b> → فقط نامزدهای خرید.</li>
            <li>دکمه <b>سیگنال فروش</b> → فشار فروش / اجتناب.</li>
            <li>ورود · حد ضرر · TP را یادداشت کنید.</li>
            <li>پامپ‌واچ فقط پایش است — سیگنال خرید نیست.</li>
          </ul>

          <p className="help-warn">
            ⚠️ این ابزار <b>توصیه مالی نیست</b> و سود را تضمین نمی‌کند.
            معامله خودکار خاموش است — تصمیم نهایی با شماست.
          </p>
        </section>
      )}

      <div className="meta">
        <span>آخرین بروزرسانی: {updated ? new Date(updated).toLocaleString("fa-IR") : "—"}</span>
        <div className="meta-btns">
          <button type="button" onClick={() => { setLoading(true); load(); }}>بروزرسانی</button>
        </div>
      </div>
      {message && !live && <div className="info">ℹ️ {message}</div>}

      <section className="section">
        <h2 className="section-title">💎 ارزهای اصلی بازار</h2>
        <div className="majors-grid">
          {majors.length === 0 && <div className="muted">در حال بارگذاری...</div>}
          {majors.map((m) => (
            <div className="major-chip" key={m.symbol}>
              <b>{m.symbol.replace("/USDT", "")}</b>
              <span className="price">{fmt(m.price)}</span>
              <strong className={m.changePct >= 0 ? "up" : "down"}>
                {m.changePct >= 0 ? "+" : ""}{m.changePct.toFixed(2)}%
              </strong>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">📊 نمای کلی بازار</h2>
        <div className="overview">
          <div className="ov-card"><h3>بیشترین رشد ۲۴س</h3>
            <ul>{gainers.slice(0,5).map(g => <li key={g.symbol}><span>{g.symbol}</span><strong className="up">+{g.changePct.toFixed(1)}%</strong></li>)}
            {gainers.length===0 && <li className="muted">—</li>}</ul>
          </div>
          <div className="ov-card"><h3>بیشترین افت ۲۴س</h3>
            <ul>{losers.slice(0,5).map(g => <li key={g.symbol}><span>{g.symbol}</span><strong className="down">{g.changePct.toFixed(1)}%</strong></li>)}
            {losers.length===0 && <li className="muted">—</li>}</ul>
          </div>
          <div className="ov-card"><h3>🚀 Pump Watch</h3>
            <ul>{pumps.slice(0,10).map(p => <li key={p.symbol}><span>{p.symbol}</span><strong className="up">+{p.changePct.toFixed(1)}%</strong></li>)}
            {pumps.length===0 && <li className="muted">مورد غیرعادی یافت نشد</li>}</ul>
            <p className="note">Pump ≠ BUY — فقط پایش با ریسک بالا · رشد ≥۳٪</p>
          </div>
        </div>
      </section>

      {risks.length > 0 && signalFilter === "ALL" && (
        <section className="section">
          <h2 className="section-title">⚠️ هشدار ریسک / فروش</h2>
          <div className="risk-row">{risks.slice(0,8).map(o => (
            <div className="risk-chip" key={o.symbol}><b>{o.symbol}</b><span>{catLabel[o.category||o.action]||o.action}</span></div>
          ))}</div>
        </section>
      )}

      <section className="section">
        <div className="section-head">
          <h2 className="section-title" style={{margin:0}}>
            {signalFilter === "BUY" ? "🟢 سیگنال‌های خرید"
              : signalFilter === "SELL" ? "🔴 سیگنال‌های فروش"
              : "🔥 فرصت‌های رتبه‌بندی‌شده"}
            {signalFilter === "ALL" && buySignals.length ? ` (${buySignals.length} نامزد خرید)` : ""}
            {signalFilter === "BUY" ? ` (${buySignals.length})` : ""}
            {signalFilter === "SELL" ? ` (${sellSignals.length})` : ""}
          </h2>
          <div className="signal-btns">
            <button type="button" className={signalFilter === "ALL" ? "sig active" : "sig"} onClick={() => setSignalFilter("ALL")}>همه</button>
            <button type="button" className={signalFilter === "BUY" ? "sig buy active" : "sig buy"} onClick={() => setSignalFilter("BUY")}>🟢 سیگنال خرید ({buySignals.length})</button>
            <button type="button" className={signalFilter === "SELL" ? "sig sell active" : "sig sell"} onClick={() => setSignalFilter("SELL")}>🔴 سیگنال فروش ({sellSignals.length})</button>
          </div>
        </div>

        {loading ? <div className="empty">در حال اسکن بازار و رتبه‌بندی فرصت‌ها...</div>
        : displayed.length === 0 ? (
          <div className="empty">
            <strong>
              {signalFilter === "BUY" ? "فعلاً سیگنال خرید معتبری نیست."
                : signalFilter === "SELL" ? "فعلاً سیگنال فروش نیست."
                : "🟡 فعلاً فرصت با کیفیت مناسب پیدا نشد."}
            </strong>
            <span>منتظر شرایط بهتر بمانید یا دکمه بروزرسانی را بزنید.</span>
          </div>
        ) : (
          <div className="grid">{displayed.map((o,i) => {
            const cat = o.category || o.action;
            return (
              <article className={`card cat-${cat}`} key={`${o.symbol}-${i}`}>
                <div className="top"><div><span className="rank">#{i+1}</span><h2>{o.symbol}</h2></div>
                  <div className="score">{o.score}<small>/100</small></div></div>
                <div className="buy">{catLabel[cat]||cat}</div>
                <div className="stats">
                  <div><b>اعتماد</b><strong>{o.confidence}%</strong></div>
                  <div><b>قیمت</b><strong>{fmt(o.price??o.entry)}</strong></div>
                  <div><b>۲۴س</b><strong className={(o.changePct||0)>=0?"up":"down"}>{o.changePct!=null?`${o.changePct>=0?"+":""}${o.changePct.toFixed(1)}%`:"—"}</strong></div>
                  <div><b>ورود</b><strong>{fmt(o.entry)}</strong></div>
                  <div><b>حد ضرر</b><strong>{fmt(o.stopLoss)}</strong></div>
                  <div><b>TP1</b><strong>{fmt(o.tp1)}</strong></div>
                  <div><b>TP2</b><strong>{fmt(o.tp2)}</strong></div>
                  <div><b>R/R</b><strong>{o.riskReward==null?"—":`1:${o.riskReward.toFixed(1)}`}</strong></div>
                  <div><b>نقدشوندگی</b><strong>{o.liquidity??"—"}</strong></div>
                </div>
                <div className="why"><h3>دلایل</h3><ul>{(o.reasons||[]).map((r,j)=><li key={j}>✓ {r}</li>)}</ul></div>
                {(o.warnings||[]).length>0 && <div className="warn-list">{o.warnings!.map((w,j)=><div key={j}>⚠️ {w}</div>)}</div>}
                <div className="warning">⚠️ توصیه مالی نیست. تصمیم نهایی با شماست. معامله خودکار خاموش است.</div>
              </article>
            );
          })}</div>
        )}
      </section>
      <footer><p>منبع داده: OKX عمومی · AUTO_TRADING = OFF · هیچ سودی تضمین نمی‌شود</p></footer>
    </div>
    <style jsx>{`
      *{box-sizing:border-box}body{margin:0;background:#07111f;color:#e8eef7;font-family:Tahoma,Arial,sans-serif}
      .shell{max-width:1200px;margin:auto;padding:28px 16px 60px}
      header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}
      .header-actions{display:flex;flex-direction:column;align-items:flex-end;gap:10px}
      .badge{font-size:12px;border:1px solid #29415d;border-radius:20px;padding:6px 12px;color:#78b7ff}
      h1{font-size:30px;margin:14px 0 8px}header p{color:#91a4ba;margin:0;line-height:1.6}
      .status{padding-top:4px;color:#f0c674;font-size:13px;white-space:nowrap}.status.live{color:#63e6a7}
      .help-btn{background:#153453;border:1px solid #29415d;color:#dbeafe;border-radius:10px;padding:8px 12px;cursor:pointer;font-size:13px}
      .help-box{margin-top:20px;background:#0b1828;border:1px solid #29415d;border-radius:16px;padding:22px 24px;line-height:1.8}
      .help-box h2{margin:0 0 12px;font-size:18px;color:#cfe3ff}
      .help-box h3{margin:16px 0 8px;font-size:15px;color:#cfe3ff}
      .help-box ol,.help-box ul{margin:0;padding-right:22px;color:#c8d6e5;font-size:14px}
      .help-box li{margin-bottom:6px}
      .help-labels{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
      .help-labels span{background:#101f31;border:1px solid #1b3047;border-radius:8px;padding:6px 10px;font-size:12px}
      .help-warn{background:#211d17;color:#f0c674;border-radius:10px;padding:12px;font-size:13px;margin:12px 0 0}
      .meta{display:flex;justify-content:space-between;align-items:center;margin:22px 0 12px;color:#91a4ba;font-size:13px}
      .meta-btns{display:flex;gap:8px}
      .meta button{background:#153453;border:1px solid #29415d;color:#dbeafe;border-radius:10px;padding:9px 14px;cursor:pointer}
      .info,.empty{border:1px solid #29415d;background:#0b1828;border-radius:16px;padding:18px;margin-top:12px}
      .empty{text-align:center;display:flex;flex-direction:column;gap:8px;color:#aebfd2}
      .section{margin-top:28px}.section-title{font-size:18px;margin:0 0 14px;color:#cfe3ff}
      .section-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px}
      .signal-btns{display:flex;flex-wrap:wrap;gap:8px}
      .sig{background:#101f31;border:1px solid #29415d;color:#aebfd2;border-radius:10px;padding:9px 14px;cursor:pointer;font-size:13px}
      .sig.active{border-color:#78b7ff;color:#e8eef7;background:#153453}
      .sig.buy.active{border-color:#2f6b4f;background:#0f2a1c;color:#63e6a7}
      .sig.sell.active{border-color:#5a3040;background:#211820;color:#ff8f8f}
      .majors-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}
      .major-chip{background:#0b1828;border:1px solid #1b3047;border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}
      .major-chip b{font-size:14px;color:#cfe3ff}.major-chip .price{font-size:13px;color:#aebfd2}
      .major-chip strong{font-size:13px}
      .overview{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
      .ov-card{background:#0b1828;border:1px solid #1b3047;border-radius:16px;padding:16px}
      .ov-card h3{margin:0 0 12px;font-size:14px;color:#91a4ba}
      .ov-card ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
      .ov-card li{display:flex;justify-content:space-between;font-size:13px}
      .ov-card .note{margin:12px 0 0;font-size:11px;color:#f0c674}.muted{color:#6b7c90}
      .up{color:#63e6a7}.down{color:#ff8f8f}
      .risk-row{display:flex;flex-wrap:wrap;gap:10px}
      .risk-chip{background:#211820;border:1px solid #5a3040;border-radius:12px;padding:10px 14px;font-size:13px;display:flex;gap:10px;align-items:center}
      .risk-chip span{color:#f0a8a8}
      .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
      .card{background:#0b1828;border:1px solid #1b3047;border-radius:18px;padding:18px;box-shadow:0 10px 28px #0003}
      .card.cat-STRONG_BUY{border-color:#2f6b4f}.card.cat-BUY_CANDIDATE,.card.cat-BUY{border-color:#2a5a40}
      .card.cat-PUMP_WATCH{border-color:#6b5a20}.card.cat-STRONG_SELL,.card.cat-SELL_CANDIDATE,.card.cat-SELL{border-color:#8b3a4a}.card.cat-AVOID,.card.cat-HIGH_RISK{border-color:#5a3040;opacity:.92}
      .top{display:flex;justify-content:space-between;align-items:center}
      .top h2{display:inline;margin:0 0 0 8px;font-size:20px}.rank{color:#78b7ff;font-weight:bold}
      .score{font-size:28px;font-weight:bold;color:#63e6a7}.score small{font-size:12px;color:#91a4ba}
      .buy{margin:12px 0;font-size:16px;font-weight:bold}
      .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
      .stats div{background:#101f31;border-radius:12px;padding:10px}
      .stats b{display:block;color:#91a4ba;font-size:11px;margin-bottom:4px}.stats strong{font-size:12px}
      .why{margin-top:14px}.why h3{font-size:13px;margin:0 0 8px}
      .why ul{list-style:none;padding:0;margin:0;display:grid;gap:6px;color:#c8d6e5;font-size:13px}
      .warn-list{margin-top:10px;color:#f0c674;font-size:12px;display:grid;gap:4px}
      .warning{margin-top:14px;background:#211d17;color:#f0c674;border-radius:10px;padding:10px;font-size:11px}
      footer{margin-top:40px;text-align:center;color:#6b7c90;font-size:12px}
      @media(max-width:650px){h1{font-size:22px}.shell{padding:18px 12px 40px}.grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}header{flex-direction:column}.majors-grid{grid-template-columns:repeat(2,1fr)}.section-head{flex-direction:column;align-items:flex-start}}
    `}</style></main>
  );
}
