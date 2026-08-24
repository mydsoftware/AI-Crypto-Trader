"""موتور نهایی فرصت‌ها؛ داده زنده از تبدیل به‌صورت پیش‌فرض."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from core.data_engine import DataEngine, MarketSnapshot
from core.technical import atr, generate_technical_evidence, technical_score
from core.regime import detect_regime
from poursamadi import PoursamadiEngine
from scanner.cost_model import CostModel
from scanner.ensemble_engine import EnsembleEngine, StrategyVote, TradePlan
from scanner.ranking import rank as rank_opportunity
from scanner.strategy_votes import generate_votes
logger = logging.getLogger(__name__)
STABLES={"USDC","USDT","USD","DAI","BUSD","TUSD","FDUSD","USDE","USDD"}
@dataclass
class FinalOpportunity:
    rank:int; symbol:str; category:str; final_score:float; direction:str; confidence:float; price:float
    entry_low:float|None=None; entry_high:float|None=None; stop_loss:float|None=None; take_profit_1:float|None=None; take_profit_2:float|None=None; risk_reward:float|None=None
    reasons:list[str]=field(default_factory=list); warnings:list[str]=field(default_factory=list); strategy_votes:list[dict[str,Any]]=field(default_factory=list)
    technical_direction:str="NEUTRAL"; liquidity_score:float=0.0; spread_pct:float|None=None; exchange:str=""; updated_at:str=""
class OpportunityEngine:
    def __init__(self,data_engine:DataEngine|None=None,min_quote_volume:float=1_000_000,max_symbols:int=40,min_score:float=55.0):
        self.data=data_engine or DataEngine(primary="tabdeal",fallbacks=["okx","binance"],quote="IRT")
        self.min_quote_volume=min_quote_volume; self.max_symbols=max_symbols; self.min_score=min_score
        self.ensemble=EnsembleEngine(); self.cost=CostModel(); self.poursamadi=PoursamadiEngine()
    def _analyze_symbol(self,snap:MarketSnapshot)->FinalOpportunity|None:
        candles=self.data.fetch_ohlcv(snap.symbol,"1h",120)
        if len(candles)<60:return None
        evidences=generate_technical_evidence(candles); tech_score,tech_dir=technical_score(evidences)
        from scanner.indicators import Candle as ScannerCandle
        scanner_candles=[ScannerCandle(c.timestamp,c.open,c.high,c.low,c.close,c.volume) for c in candles]
        votes=generate_votes(scanner_candles); ps=self.poursamadi.analyze(candles)
        for v in ps.votes:votes.append(v)
        regime=detect_regime(candles); atr_val=atr(candles)
        plan:TradePlan=self.ensemble.build_plan(votes=[StrategyVote(v.name,v.direction,v.score,v.reason,v.reliability) for v in votes],price=snap.price,atr=atr_val)
        expected_move=abs(plan.take_profit_1-plan.entry_low)/plan.entry_low if plan.take_profit_1 and plan.entry_low and plan.entry_low>0 else ((atr_val*2)/snap.price if atr_val and snap.price>0 else 0)
        risk=max(0,min(100,100-snap.liquidity_score+(snap.spread_pct or 0)*20)); tf_score=plan.strategy_agreement or 50
        opp_score=rank_opportunity(symbol=snap.symbol,technical=tech_score,timeframe=tf_score,external=50,liquidity=snap.liquidity_score,risk=risk,expected_move=expected_move,cost=self.cost)
        category=self._classify(opp_score.final_score,plan.direction,snap,tech_dir); reasons=list(opp_score.reasons)
        reasons += [f"{e.name}: {e.reason}" for e in evidences if e.direction in ("BUY","SELL") and e.score>=70]
        reasons += [f"پورصمدی {n}: {s}" for n,s in ps.summary.items() if not s.startswith("NEUTRAL")]; reasons.append(f"رژیم: {regime.primary}/{regime.structure}/{regime.volatility}"); reasons=reasons[:10]
        warnings=list(opp_score.warnings)
        if snap.spread_pct and snap.spread_pct>.3:warnings.append(f"اسپرد نسبتاً بالا ({snap.spread_pct:.3f}%).")
        if snap.liquidity_score<55:warnings.append("نقدشوندگی متوسط رو به پایین.")
        return FinalOpportunity(0,snap.symbol,category,opp_score.final_score,plan.direction if plan.direction!="WAIT" else tech_dir,round(plan.confidence*100 if plan.confidence<=1 else plan.confidence,1),snap.price,plan.entry_low,plan.entry_high,plan.stop_loss,plan.take_profit_1,plan.take_profit_2,plan.risk_reward,reasons,warnings,[{"name":v.name,"direction":v.direction,"score":round(v.score,1),"reason":v.reason} for v in votes],tech_dir,snap.liquidity_score,snap.spread_pct,snap.exchange,datetime.now(timezone.utc).isoformat())
    def _classify(self,score,plan_dir,snap,tech_dir):
        if snap.price_change_pct>=8 and snap.liquidity_score>=40:return "PUMP_WATCH"
        if score>=80 and plan_dir=="BUY" and tech_dir=="BUY":return "STRONG_BUY"
        if score>=65 and (plan_dir=="BUY" or tech_dir=="BUY"):return "BUY_CANDIDATE"
        if score<40 or plan_dir=="SELL":return "AVOID"
        if snap.liquidity_score<40 or (snap.spread_pct and snap.spread_pct>.8):return "HIGH_RISK"
        return "WAIT"
    def scan(self):
        snapshots=self.data.build_snapshots(min_quote_volume=self.min_quote_volume,max_symbols=self.max_symbols); snapshots=[s for s in snapshots if s.symbol.split('/')[0] not in STABLES]; results=[]
        for snap in snapshots:
            try:
                opp=self._analyze_symbol(snap)
                if opp and opp.final_score>=self.min_score:results.append(opp)
            except Exception as exc:logger.warning("تحلیل %s ناموفق: %s",snap.symbol,exc)
        priority={"STRONG_BUY":5,"BUY_CANDIDATE":4,"PUMP_WATCH":3,"WAIT":2,"HIGH_RISK":1,"AVOID":0}; results.sort(key=lambda x:(priority.get(x.category,0),x.final_score),reverse=True)
        for i,r in enumerate(results,1):r.rank=i
        return results
    def to_api_dict(self,opportunities):
        items=[]
        for o in opportunities:items.append({"symbol":o.symbol,"score":o.final_score,"action":"BUY" if o.category in ("STRONG_BUY","BUY_CANDIDATE") else o.category,"category":o.category,"confidence":o.confidence,"entry":o.entry_low,"stopLoss":o.stop_loss,"tp1":o.take_profit_1,"tp2":o.take_profit_2,"riskReward":o.risk_reward,"reasons":o.reasons,"warnings":o.warnings,"direction":o.direction,"liquidity":o.liquidity_score,"spreadPct":o.spread_pct,"exchange":o.exchange,"votes":o.strategy_votes})
        return {"updatedAt":datetime.now(timezone.utc).isoformat(),"opportunities":items,"live":True,"message":f"{len(items)} فرصت از اسکن زنده بازار تبدیل","count":len(items),"exchange":"tabdeal","quote":"IRT","autoTrading":False}
