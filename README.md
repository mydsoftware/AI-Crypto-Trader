# PACT-OS / AI-Crypto-Trader

## دستیار هوش مصنوعی معامله‌گری ارز دیجیتال

سیستم **فقط دستیار تصمیم‌گیری** است. معامله خودکار خاموش است (`AUTO_TRADING = OFF`). هیچ سودی تضمین نمی‌شود.

### قابلیت‌های فعلی (واقعی)

| بخش | وضعیت |
|------|--------|
| Multi-Exchange Adapter (OKX / Kraken / Binance / Bybit) | ✅ |
| DataEngine زنده + Discovery بازار | ✅ |
| Technical Engine + Evidence | ✅ |
| OpportunityEngine + Ranking | ✅ |
| API پایتون (`api/server.py`) | ✅ |
| داشبورد Vercel (زنده بدون وابستگی اجباری به پایتون) | ✅ |
| Pump Watch / Market Overview | ✅ |
| AUTO TRADING | ❌ خاموش |

### اصل ایمنی

- هیچ سفارش واقعی ارسال نمی‌شود.
- سیگنال‌ها توصیه مالی نیستند.
- تصمیم نهایی همیشه با کاربر است.

---

## معماری

```text
Exchange Adapters (OKX primary)
        ↓
   DataEngine
        ↓
 Technical Evidence + Strategy Votes + Ensemble
        ↓
 OpportunityEngine → Ranking → Classification
        ↓
   API / Vercel Dashboard
```

دسته‌بندی خروجی:

- 🔥 STRONG_BUY
- 🟢 BUY_CANDIDATE
- 🟡 WAIT
- 🔴 AVOID
- 🚀 PUMP_WATCH
- ⚠️ HIGH_RISK

---

## نصب موتور پایتون

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`.env` (اختیاری — برای داده عمومی OKX نیازی به کلید نیست):

```text
TABDEAL_API_KEY=
TABDEAL_API_SECRET=
TRADING_ENGINE_URL=
```

اجرای API:

```bash
python -m api.server
# GET http://localhost:8080/api/opportunities
# GET http://localhost:8080/api/market
# GET http://localhost:8080/api/health
```

اسکن مستقیم:

```bash
python -c "from core.opportunity_engine import OpportunityEngine; print(OpportunityEngine().scan()[:3])"
```

---

## داشبورد Vercel

داشبورد Next.js در پوشه `web/` است و **بدون سرور پایتون** هم کار می‌کند:

- داده زنده از OKX (endpoint عمومی)
- تحلیل سبک (EMA / SMA / RSI / Volume / ATR) داخل Route Handler
- در صورت تنظیم `TRADING_ENGINE_URL` از موتور پایتون استفاده می‌کند

### Deploy روی Vercel

1. Repository را به Vercel وصل کنید.
2. Root Directory را خالی بگذارید (از `vercel.json` استفاده می‌شود).
3. Build: `cd web && npm run build`
4. (اختیاری) Environment Variable:
   - `TRADING_ENGINE_URL` = آدرس API پایتون اگر deploy شده باشد

APIهای داشبورد:

| مسیر | توضیح |
|------|--------|
| `/api/opportunities` | فرصت‌های رتبه‌بندی‌شده |
| `/api/market` | نمای کلی + gainers/losers |
| `/api/pump-watch` | پایش شتاب غیرعادی |
| `/api/health` | سلامت سرویس |

صفحه اصلی:

- 🔥 بهترین فرصت‌های فعلی
- 🚀 Pump Watch
- 📊 Market Overview
- ⚠️ Risk Alerts
- رفرش خودکار هر ۹۰ ثانیه

---

## محدودیت‌های واقعی

- از برخی IPها Binance/Bybit مسدود است → primary = **OKX**
- Derivatives / On-chain / Telegram ErfTrade / Paper Trading هنوز کامل نیست
- تحلیل Vercel سبک‌تر از موتور پایتون است

---

## تست

```bash
python -m unittest discover -s tests -v
```

---

**AUTO_TRADING همچنان OFF است.**
