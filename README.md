# PACT-OS

## دستیار شخصی هوش مصنوعی معامله‌گری ارز دیجیتال

PACT-OS یک دستیار معامله‌گری مبتنی بر Python است که بازار را بررسی می‌کند، فرصت‌ها را رتبه‌بندی می‌کند و برای هر فرصت یک برنامه معاملاتی قابل بررسی می‌سازد.

### وضعیت فعلی

- اتصال به صرافی Tabdeal برای دریافت داده بازار
- اسکن Watchlist
- تحلیل تکنیکال
- تحلیل چندتایم‌فریمی
- تحلیل روند بازار
- Support / Resistance
- Breakout / Pullback
- Volume / Liquidity / Order Flow
- Confidence Score
- Ranking فرصت‌ها
- توضیح دلایل تحلیل
- پیشنهاد Entry / Stop Loss / Take Profit
- محاسبه Risk/Reward
- پیشنهاد درصد ریسک
- ثبت تحلیل در ژورنال
- **بدون اجرای معامله**

### اصل ایمنی

این نسخه عمداً فقط **دستیار** است. هیچ سفارش واقعی یا شبیه‌سازی‌شده‌ای توسط برنامه اجرا نمی‌شود و تصمیم نهایی همیشه با کاربر است.

## نصب

```bash
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

فایل `.env`:

```text
TABDEAL_API_KEY=
TABDEAL_API_SECRET=
```

کلید API باید تا حد امکان فقط دسترسی خواندن داشته باشد.

## اجرا

```bash
python main.py
```

## معماری

```text
Market Data
    ↓
Market Scanner
    ↓
Technical Analysis
    ↓
Multi Timeframe
    ↓
Confidence + Ranking
    ↓
AI Trading Assistant
    ↓
Trade Plan
    ├── Entry
    ├── Stop Loss
    ├── Take Profit
    ├── Risk/Reward
    └── Warnings
    ↓
تصمیم نهایی با کاربر
```

## تست

```bash
python -m unittest discover -s tests -v
```
