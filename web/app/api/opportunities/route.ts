import { NextResponse } from "next/server";
import { analyzeSymbol, fetchOkxCandles, fetchOkxTickers, type Opportunity } from "../../../lib/market";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

const MAX_ANALYZE = 18;
const MIN_QUOTE_VOLUME = 1_000_000;

/**
 * اسکن زنده بازار از OKX (عمومی).
 * اگر TRADING_ENGINE_URL تنظیم باشد، از موتور پایتون استفاده می‌کند؛
 * در غیر این صورت تحلیل سبک داخل Vercel انجام می‌شود.
 * AUTO TRADING خاموش است — فقط تحلیل.
 */
export async function GET() {
  try {
    const upstream = process.env.TRADING_ENGINE_URL;
    if (upstream) {
      try {
        const response = await fetch(`${upstream.replace(/\/$/, "")}/opportunities`, {
          cache: "no-store",
        });
        if (response.ok) {
          const data = await response.json();
          return NextResponse.json({ ...data, live: true, source: "python-engine" });
        }
      } catch (e) {
        console.warn("Upstream engine unavailable, fallback to embedded scanner", e);
      }
    }

    const tickers = await fetchOkxTickers();
    const candidates = tickers
      .filter((t) => t.quoteVolume >= MIN_QUOTE_VOLUME)
      .slice(0, MAX_ANALYZE);

    const opportunities: Opportunity[] = [];
    const batchSize = 6;
    for (let i = 0; i < candidates.length; i += batchSize) {
      const batch = candidates.slice(i, i + batchSize);
      const results = await Promise.all(
        batch.map(async (t) => {
          try {
            const candles = await fetchOkxCandles(t.symbol, "1H", 100);
            return analyzeSymbol(t, candles);
          } catch (err) {
            console.warn(`analyze ${t.symbol}`, err);
            return null;
          }
        }),
      );
      for (const r of results) {
        if (r) opportunities.push(r);
      }
    }

    const priority: Record<string, number> = {
      STRONG_BUY: 5,
      BUY_CANDIDATE: 4,
      PUMP_WATCH: 3,
      WAIT: 2,
      HIGH_RISK: 1,
      AVOID: 0,
    };

    opportunities.sort(
      (a, b) =>
        (priority[b.category] ?? 0) - (priority[a.category] ?? 0) ||
        b.score - a.score,
    );

    const display = opportunities.filter(
      (o) =>
        o.category === "STRONG_BUY" ||
        o.category === "BUY_CANDIDATE" ||
        o.category === "PUMP_WATCH" ||
        o.category === "WAIT" ||
        (o.category === "AVOID" && o.score >= 70),
    );

    return NextResponse.json({
      updatedAt: new Date().toISOString(),
      opportunities: display.slice(0, 24),
      allCount: opportunities.length,
      live: true,
      source: "vercel-okx",
      message: `${display.length} فرصت از اسکن زنده OKX`,
      autoTrading: false,
    });
  } catch (error) {
    console.error("OPPORTUNITIES_ERROR", error);
    return NextResponse.json(
      {
        updatedAt: new Date().toISOString(),
        opportunities: [],
        live: false,
        message: "دریافت فرصت‌های زنده موقتاً ناموفق بود.",
        error: String(error),
      },
      { status: 200 },
    );
  }
}
