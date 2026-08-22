"use client";

import { FormEvent, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "سلام. من دستیار معامله‌گری شما هستم. بازار را تحلیل می‌کنم و پیشنهاد می‌دهم؛ هیچ معامله‌ای را خودکار اجرا نمی‌کنم." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(e: FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: text }) });
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", content: data.message || "پاسخی دریافت نشد." }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "ارتباط با دستیار برقرار نشد." }]);
    } finally { setLoading(false); }
  }

  return <main dir="rtl"><section className="shell"><header><div><span className="badge">PACT-OS</span><h1>دستیار هوشمند معامله‌گری</h1><p>تحلیل بازار، مدیریت ریسک و پیشنهاد معامله — بدون اجرای خودکار.</p></div><div className="status">● آماده</div></header><div className="chat">{messages.map((m, i) => <div key={i} className={m.role === "user" ? "msg user" : "msg assistant"}><b>{m.role === "user" ? "شما" : "دستیار"}</b><p>{m.content}</p></div>)}{loading && <div className="msg assistant"><b>دستیار</b><p>در حال تحلیل...</p></div>}</div><form onSubmit={send}><input value={input} onChange={(e) => setInput(e.target.value)} placeholder="مثلاً BTC را الان تحلیل کن" /><button disabled={loading}>ارسال</button></form><div className="notice">⚠️ دستیار فقط تحلیل و پیشنهاد ارائه می‌کند. تصمیم نهایی و اجرای معامله کاملاً با شماست.</div></section><style jsx>{`*{box-sizing:border-box}body{margin:0;background:#07111f;color:#e8eef7;font-family:Tahoma,Arial,sans-serif}.shell{max-width:980px;margin:0 auto;padding:36px 18px}header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}.badge{font-size:12px;border:1px solid #29415d;border-radius:20px;padding:6px 10px;color:#78b7ff}h1{font-size:32px;margin:16px 0 8px}header p{color:#91a4ba;margin:0}.status{color:#63e6a7;font-size:14px;padding-top:8px}.chat{min-height:55vh;border:1px solid #1b3047;border-radius:20px;background:#0b1828;padding:20px;display:flex;flex-direction:column;gap:14px}.msg{max-width:82%;padding:14px 16px;border-radius:16px;line-height:1.9}.msg p{margin:5px 0 0;white-space:pre-wrap}.assistant{background:#12243a;align-self:flex-start}.user{background:#163d64;align-self:flex-end}form{display:flex;gap:10px;margin-top:16px}input{flex:1;background:#0b1828;border:1px solid #29415d;color:white;border-radius:14px;padding:15px;font-size:15px}button{border:0;border-radius:14px;padding:0 24px;background:#2d8cff;color:white;font-weight:bold}.notice{margin-top:14px;padding:13px;border-radius:12px;background:#1b1820;color:#f0c674;font-size:13px}@media(max-width:650px){h1{font-size:24px}.shell{padding:20px 12px}.msg{max-width:92%}form button{padding:0 16px}}`}</style></main>;
}
