import { NextResponse } from "next/server";

export const runtime = "nodejs";

const fallback = [
  { symbol: "BTC/USDT", score: 0, action: "WAIT", confidence: 0, entry: null, stopLoss: null, tp1: null, tp2: null, riskReward: null, reasons: ["داده زنده هنوز به داشبورد متصل نشده است."] },
];

export async function GET() {
  try {
    const upstream = process.env.TRADING_ENGINE_URL;
    if (!upstream) {
      return NextResponse.json({ updatedAt: new Date().toISOString(), opportunities: fallback, live: false, message: "موتور تحلیل زنده هنوز متصل نشده است." });
    }
    const response = await fetch(`${upstream.replace(/\/$/, "")}/opportunities`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Trading engine returned ${response.status}`);
    return NextResponse.json({ ...(await response.json()), live: true });
  } catch (error) {
    console.error("OPPORTUNITIES_ERROR", error);
    return NextResponse.json({ updatedAt: new Date().toISOString(), opportunities: [], live: false, message: "دریافت فرصت‌های زنده موقتاً ناموفق بود." }, { status: 200 });
  }
}
