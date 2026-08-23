import { NextResponse } from "next/server";
import { fetchOkxTickers } from "../../../lib/market";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const tickers = await fetchOkxTickers();
    const pumps = tickers
      .filter((t) => t.changePct >= 6 && t.quoteVolume >= 500_000)
      .slice(0, 15)
      .map((t) => ({
        symbol: t.symbol,
        price: t.last,
        changePct: Math.round(t.changePct * 100) / 100,
        quoteVolume: t.quoteVolume,
        warning: "شتاب غیرعادی — Pump Potential ≠ BUY. ریسک بالا.",
      }));
    return NextResponse.json({
      updatedAt: new Date().toISOString(),
      items: pumps,
      live: true,
      note: "این فهرست فقط پایش است و سیگنال خرید قطعی نیست.",
    });
  } catch (e) {
    return NextResponse.json({ live: false, items: [], error: String(e) }, { status: 200 });
  }
}
