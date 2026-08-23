/**
 * لایه داده بازار برای Dashboard روی Vercel
 * فقط endpointهای عمومی OKX — بدون API Key و بدون ارسال سفارش
 */

export type Ticker = {
  symbol: string;
  last: number;
  changePct: number;
  quoteVolume: number;
  bid?: number;
  ask?: number;
  high?: number;
  low?: number;
};

export type Candle = {
  ts: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

const STABLES = new Set([
  "USDC", "USDT", "USD", "DAI", "BUSD", "TUSD", "FDUSD", "USDE", "USDD", "EUR",
]);

function toStandard(instId: string): string {
  return instId.replace("-", "/").toUpperCase();
}

export async function fetchOkxTickers(): Promise<Ticker[]> {
  const res = await fetch("https://www.okx.com/api/v5/market/tickers?instType=SPOT", {
    next: { revalidate: 60 },
    headers: { "User-Agent": "AI-Crypto-Trader/1.0" },
  });
  if (!res.ok) throw new Error(`OKX tickers HTTP ${res.status}`);
  const json = await res.json();
  const list = (json?.data || []) as Array<Record<string, string>>;
  const out: Ticker[] = [];
  for (const item of list) {
    const inst = item.instId || "";
    if (!inst.endsWith("-USDT")) continue;
    const base = inst.split("-")[0];
    if (STABLES.has(base)) continue;
    const last = parseFloat(item.last || "0");
    const open24 = parseFloat(item.open24h || item.sodUtc0 || "0");
    const changePct = open24 > 0 ? ((last - open24) / open24) * 100 : 0;
    out.push({
      symbol: toStandard(inst),
      last,
      changePct,
      quoteVolume: parseFloat(item.volCcy24h || "0"),
      bid: parseFloat(item.bidPx || "0") || undefined,
      ask: parseFloat(item.askPx || "0") || undefined,
      high: parseFloat(item.high24h || "0") || undefined,
      low: parseFloat(item.low24h || "0") || undefined,
    });
  }
  return out.sort((a, b) => b.quoteVolume - a.quoteVolume);
}

export async function fetchOkxCandles(
  symbol: string,
  bar: string = "1H",
  limit: number = 100,
): Promise<Candle[]> {
  const inst = symbol.replace("/", "-").toUpperCase();
  const url = `https://www.okx.com/api/v5/market/candles?instId=${inst}&bar=${bar}&limit=${Math.min(limit, 300)}`;
  const res = await fetch(url, {
    next: { revalidate: 60 },
    headers: { "User-Agent": "AI-Crypto-Trader/1.0" },
  });
  if (!res.ok) throw new Error(`OKX candles HTTP ${res.status}`);
  const json = await res.json();
  const rows = (json?.data || []) as string[][];
  const candles: Candle[] = [];
  for (let i = rows.length - 1; i >= 0; i--) {
    const r = rows[i];
    candles.push({
      ts: parseInt(r[0], 10),
      open: parseFloat(r[1]),
      high: parseFloat(r[2]),
      low: parseFloat(r[3]),
      close: parseFloat(r[4]),
      volume: parseFloat(r[5]),
    });
  }
  return candles;
}

export function sma(values: number[], period: number): number | null {
  if (values.length < period) return null;
  let s = 0;
  for (let i = values.length - period; i < values.length; i++) s += values[i];
  return s / period;
}

export function ema(values: number[], period: number): number | null {
  if (values.length < period) return null;
  let v = 0;
  for (let i = 0; i < period; i++) v += values[i];
  v /= period;
  const mult = 2 / (period + 1);
  for (let i = period; i < values.length; i++) {
    v = (values[i] - v) * mult + v;
  }
  return v;
}

export function rsi(values: number[], period = 14): number | null {
  if (values.length < period + 1) return null;
  let gains = 0;
  let losses = 0;
  for (let i = values.length - period; i < values.length; i++) {
    const d = values[i] - values[i - 1];
    if (d >= 0) gains += d;
    else losses -= d;
  }
  const avgGain = gains / period;
  const avgLoss = losses / period;
  if (avgLoss === 0) return 100;
  return 100 - 100 / (1 + avgGain / avgLoss);
}

export function atr(candles: Candle[], period = 14): number | null {
  if (candles.length < period + 1) return null;
  let sum = 0;
  for (let i = candles.length - period; i < candles.length; i++) {
    const c = candles[i];
    const p = candles[i - 1];
    sum += Math.max(c.high - c.low, Math.abs(c.high - p.close), Math.abs(c.low - p.close));
  }
  return sum / period;
}

export type Opportunity = {
  symbol: string;
  score: number;
  action: string;
  category: string;
  confidence: number;
  entry: number | null;
  stopLoss: number | null;
  tp1: number | null;
  tp2: number | null;
  riskReward: number | null;
  reasons: string[];
  warnings: string[];
  direction: string;
  changePct: number;
  liquidity: number;
  price: number;
};

export function analyzeSymbol(ticker: Ticker, candles: Candle[]): Opportunity | null {
  if (candles.length < 50) return null;
  const closes = candles.map((c) => c.close);
  const price = ticker.last || closes[closes.length - 1];
  const reasons: string[] = [];
  const warnings: string[] = [];
  let buyScore = 0;
  let sellScore = 0;
  let weightSum = 0;

  const e9 = ema(closes, 9);
  const e21 = ema(closes, 21);
  if (e9 != null && e21 != null) {
    weightSum += 1;
    if (e9 > e21 && price > e9) {
      buyScore += 78;
      reasons.push("روند کوتاه‌مدت EMA صعودی است.");
    } else if (e9 < e21 && price < e9) {
      sellScore += 78;
      reasons.push("روند کوتاه‌مدت EMA نزولی است.");
    }
  }

  const s50 = sma(closes, 50);
  if (s50 != null) {
    weightSum += 1.05;
    if (price > s50) {
      buyScore += 70;
      reasons.push("قیمت بالای SMA50 قرار دارد.");
    } else {
      sellScore += 70;
      reasons.push("قیمت زیر SMA50 قرار دارد.");
    }
  }

  const r = rsi(closes);
  if (r != null) {
    weightSum += 0.9;
    if (r >= 50 && r <= 68) {
      buyScore += 70;
      reasons.push(`RSI مومنتوم صعودی سالم (${r.toFixed(1)}).`);
    } else if (r >= 32 && r < 50) {
      sellScore += 70;
      reasons.push(`RSI مومنتوم نزولی (${r.toFixed(1)}).`);
    } else if (r > 75) {
      warnings.push(`RSI بیش‌خرید (${r.toFixed(1)}).`);
    } else if (r < 25) {
      warnings.push(`RSI بیش‌فروش (${r.toFixed(1)}).`);
    }
  }

  if (candles.length >= 21) {
    let avgVol = 0;
    for (let i = candles.length - 21; i < candles.length - 1; i++) avgVol += candles[i].volume;
    avgVol /= 20;
    const vr = avgVol > 0 ? candles[candles.length - 1].volume / avgVol : 1;
    if (vr >= 1.8) {
      weightSum += 1;
      if (price >= closes[closes.length - 2]) {
        buyScore += 80;
        reasons.push(`حجم نسبی ${vr.toFixed(1)}x همراه با رشد قیمت.`);
      } else {
        sellScore += 80;
        reasons.push(`حجم نسبی ${vr.toFixed(1)}x همراه با افت قیمت.`);
      }
    }
  }

  if (ticker.changePct >= 5) {
    buyScore += 40;
    reasons.push(`تغییر ۲۴ساعته +${ticker.changePct.toFixed(1)}%.`);
  } else if (ticker.changePct <= -5) {
    sellScore += 40;
    reasons.push(`تغییر ۲۴ساعته ${ticker.changePct.toFixed(1)}%.`);
  }

  const total = buyScore + sellScore;
  let direction = "NEUTRAL";
  let score = 50;
  if (total > 0) {
    if (buyScore > sellScore * 1.15) {
      direction = "BUY";
      score = Math.min(100, (buyScore / (weightSum * 80 || 1)) * 100);
    } else if (sellScore > buyScore * 1.15) {
      direction = "SELL";
      score = Math.min(100, (sellScore / (weightSum * 80 || 1)) * 100);
    }
  }
  score = Math.round(Math.max(0, Math.min(100, score)) * 10) / 10;

  const liq = Math.min(100, Math.max(10, (ticker.quoteVolume / 10_000_000) * 50));
  if (liq < 45) warnings.push("نقدشوندگی نسبتاً پایین.");

  const a = atr(candles);
  let entry: number | null = null;
  let stopLoss: number | null = null;
  let tp1: number | null = null;
  let tp2: number | null = null;
  let rr: number | null = null;
  if (a && a > 0 && direction === "BUY") {
    entry = price;
    stopLoss = price - 1.5 * a;
    const risk = price - stopLoss;
    tp1 = price + 2 * risk;
    tp2 = price + 3 * risk;
    rr = 2;
    const edge = (2 * a) / price;
    if (edge < 0.005) {
      score *= 0.55;
      warnings.push("مزیت مورد انتظار پس از هزینه معامله کم است.");
    } else {
      reasons.push("حرکت مورد انتظار از هزینه تخمینی معامله بزرگ‌تر است.");
    }
  } else if (a && a > 0 && direction === "SELL") {
    entry = price;
    stopLoss = price + 1.5 * a;
    const risk = stopLoss - price;
    tp1 = price - 2 * risk;
    tp2 = price - 3 * risk;
    rr = 2;
  }

  // امتیاز بالا روی فروش = فشار فروش قوی، نه خرید
  let category = "WAIT";
  if (ticker.changePct >= 8 && liq >= 40 && direction !== "SELL") {
    category = "PUMP_WATCH";
    reasons.push("شتاب غیرعادی قیمت؛ فقط پایش — سیگنال خرید قطعی نیست.");
    if (liq < 60) warnings.push("ریسک نوسان و نقدشوندگی بالا.");
  } else if (direction === "SELL" && score >= 75) {
    category = "STRONG_SELL";
    reasons.push("اجماع نزولی قوی — امتیاز بالا یعنی فشار فروش، نه سیگنال خرید.");
  } else if (direction === "SELL" && score >= 55) {
    category = "SELL_CANDIDATE";
    reasons.push("تمایل نزولی — از ورود خرید خودداری کنید.");
  } else if (score >= 75 && direction === "BUY" && liq >= 50) {
    category = "STRONG_BUY";
  } else if (score >= 60 && direction === "BUY") {
    category = "BUY_CANDIDATE";
  } else if (score < 40) {
    category = "AVOID";
  } else if (liq < 40) {
    category = "HIGH_RISK";
  }

  if (reasons.length === 0) {
    reasons.push("شرایط هنوز برای ورود با کیفیت کافی نیست.");
  }

  const action =
    category === "STRONG_BUY" || category === "BUY_CANDIDATE"
      ? "BUY"
      : category === "STRONG_SELL" || category === "SELL_CANDIDATE"
      ? "SELL"
      : category;

  const confidence = Math.round(
    Math.max(0, Math.min(99, score - (100 - liq) * 0.15)),
  );

  return {
    symbol: ticker.symbol,
    score,
    action,
    category,
    confidence,
    entry,
    stopLoss,
    tp1,
    tp2,
    riskReward: rr,
    reasons: reasons.slice(0, 6),
    warnings: warnings.slice(0, 4),
    direction,
    changePct: ticker.changePct,
    liquidity: Math.round(liq * 10) / 10,
    price,
  };
}
