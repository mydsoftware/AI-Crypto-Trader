import { NextResponse } from "next/server";
import { fetchOkxTickers } from "../../../lib/market";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const tickers = await fetchOkxTickers();
    const top = tickers.slice(0, 40).map((t) => ({
      symbol: t.symbol,
      price: t.last,
      changePct: Math.round(t.changePct * 100) / 100,
      quoteVolume: t.quoteVolume,
      bid: t.bid,
      ask: t.ask,
    }));
    const gainers = [...tickers].sort((a, b) => b.changePct - a.changePct).slice(0, 8);
    const losers = [...tickers].sort((a, b) => a.changePct - b.changePct).slice(0, 8);
    return NextResponse.json({
      updatedAt: new Date().toISOString(),
      count: tickers.length,
      symbols: top,
      gainers: gainers.map((t) => ({ symbol: t.symbol, changePct: t.changePct, price: t.last })),
      losers: losers.map((t) => ({ symbol: t.symbol, changePct: t.changePct, price: t.last })),
      live: true,
    });
  } catch (e) {
    return NextResponse.json({ live: false, error: String(e), symbols: [] }, { status: 200 });
  }
}
