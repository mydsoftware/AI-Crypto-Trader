import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PACT-OS | دستیار معامله‌گری ارز دیجیتال",
  description: "اسکن زنده بازار، رتبه‌بندی فرصت‌ها، بدون معامله خودکار",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
