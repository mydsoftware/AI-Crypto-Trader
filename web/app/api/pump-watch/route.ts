import { NextResponse } from "next/server";
import { fetchOkxTickers } from "../../../lib/market";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const tickers = await fetchOkxTickers();
    // آستانه نرم‌تر تا چند ارز نمایش داده شود (نه فقط یکی)
    const pumps = tickers
      .filter((t) => t.changePct >= 3 && t.quoteVolume >= 200_000)
      .sort((a, b) => b.changePct - a.changePct)
      .slice(0, 20)
      .map((t) => ({
        symbol: t.symbol,
        price: t.last,
        changePct: Math.round(t.changePct * 100) / 100,
        quoteVolume: Math.round(t.quoteVolume),
        warning: "شتاب غیرعادی — Pump Potential ≠ BUY. ریسک بالا.",
      }));
    return NextResponse.json({
      updatedAt: new Date().toISOString(),
      items: pumps,
      live: true,
      count: pumps.length,
      note: "این فهرست فقط پایش است و سیگنال خرید قطعی نیست. آستانه: رشد ≥۳٪ و حجم ≥۲۰۰k USDT.",
    });
  } catch (e) {
    return NextResponse.json({ live: false, items: [], error: String(e) }, { status: 200 });
  }
}
