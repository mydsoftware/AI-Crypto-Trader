"""
ماژول مستقل استراتژی‌های عمومی پورصمدی.

فقط مفاهیم عمومی قابل دسترس:
- Spike / Channel / Range / Breakout / Retest
- Pro BTB, SP2L, MicroMAP به‌عنوان رأی مستقل

قوانین خصوصی یا محتوای پولی حدس زده نمی‌شود.
هیچ Strategy به‌تنهایی تصمیم نهایی نمی‌دهد.
"""
from .engine import PoursamadiEngine, PoursamadiResult
from .pro_btb import vote_pro_btb
from .sp2l import vote_sp2l
from .micromap import vote_micromap

__all__ = [
    "PoursamadiEngine",
    "PoursamadiResult",
    "vote_pro_btb",
    "vote_sp2l",
    "vote_micromap",
]
