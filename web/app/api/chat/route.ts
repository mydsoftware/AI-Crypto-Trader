import OpenAI from "openai";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const { message } = await request.json();
    if (!message || typeof message !== "string") return NextResponse.json({ message: "پیام نامعتبر است." }, { status: 400 });
    if (!process.env.OPENAI_API_KEY) return NextResponse.json({ message: "کلید OpenAI هنوز در تنظیمات Vercel ثبت نشده است." }, { status: 503 });
    const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const response = await client.responses.create({
      model: process.env.OPENAI_MODEL || "gpt-5-mini",
      instructions: "تو دستیار شخصی معامله‌گری ارز دیجیتال هستی. فارسی پاسخ بده. تحلیل و آموزش ارائه کن و هرگز ادعا نکن که سفارش اجرا کرده‌ای. بدون داده زنده، قیمت یا سیگنال لحظه‌ای را جعل نکن. تصمیم نهایی معامله با کاربر است.",
      input: message,
    });
    return NextResponse.json({ message: response.output_text });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ message: "خطا در ارتباط با مدل هوش مصنوعی." }, { status: 500 });
  }
}
