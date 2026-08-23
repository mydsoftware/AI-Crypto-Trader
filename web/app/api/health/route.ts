import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "AI-Crypto-Trader",
    autoTrading: false,
    time: new Date().toISOString(),
  });
}
