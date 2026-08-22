import OpenAI from "openai";
import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const message = body?.message;

    if (!message || typeof message !== "string") {
      return NextResponse.json({ message: "پیام نامعتبر است." }, { status: 400 });
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { message: "کلید OpenAI در محیط سرور Vercel پیدا نشد. Environment Variables را بررسی و سپس Redeploy کن." },
        { status: 503 },
      );
    }

    const client = new OpenAI({ apiKey });
    const model = process.env.OPENAI_MODEL || "gpt-5-mini";

    const response = await client.responses.create({
      model,
      instructions:
        "تو دستیار شخصی معامله‌گری ارز دیجیتال هستی. همیشه فارسی پاسخ بده. تحلیل، آموزش و مدیریت ریسک ارائه کن. هرگز ادعا نکن که سفارش اجرا کرده‌ای. بدون داده زنده قیمت یا سیگنال لحظه‌ای را جعل نکن. تصمیم نهایی معامله همیشه با کاربر است.",
      input: message,
    });

    return NextResponse.json({ message: response.output_text || "مدل پاسخی تولید نکرد." });
  } catch (error: unknown) {
    console.error("OPENAI_CHAT_ERROR", error);

    const status = typeof error === "object" && error !== null && "status" in error
      ? Number((error as { status?: number }).status)
      : 500;

    const code = typeof error === "object" && error !== null && "code" in error
      ? String((error as { code?: unknown }).code)
      : "";

    if (status === 401 || code === "invalid_api_key") {
      return NextResponse.json({ message: "کلید OpenAI معتبر نیست. مقدار OPENAI_API_KEY را در Vercel بررسی کن." }, { status: 502 });
    }

    if (status === 429) {
      return NextResponse.json({ message: "درخواست OpenAI با محدودیت یا کمبود اعتبار مواجه شد. وضعیت API و اعتبار حساب را بررسی کن." }, { status: 429 });
    }

    const detail = error instanceof Error ? error.message : "خطای ناشناخته";
    return NextResponse.json({ message: `خطا در ارتباط با OpenAI: ${detail}` }, { status: 500 });
  }
}
