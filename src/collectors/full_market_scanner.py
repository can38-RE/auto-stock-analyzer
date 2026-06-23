"""Full market scanner - scan all A-share mainboard stocks with 1-year historical data."""

import time
import math
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import numpy as np
import baostock as bs
from loguru import logger


@dataclass
class StockMetrics:
    code: str
    name: str
    price: float
    cost_100: float
    change_1w: float = 0.0
    change_1m: float = 0.0
    change_3m: float = 0.0
    change_6m: float = 0.0
    change_1y: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    support_20: float = 0.0
    support_60: float = 0.0
    support_252: float = 0.0
    resistance_20: float = 0.0
    resistance_60: float = 0.0
    resistance_252: float = 0.0
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    ma60: float = 0.0
    ma250: float = 0.0
    avg_volume: float = 0.0
    volume_trend: float = 0.0
    trend: str = "consolidation"
    composite_score: float = 0.0
    score_details: Dict[str, float] = field(default_factory=dict)
    affordable: bool = True


class FullMarketScanner:
    """Scan all A-share mainboard stocks with comprehensive analysis."""

    MAINBOARD_PREFIXES = ("000", "001", "002", "600", "601", "603", "605")

    def __init__(self, cache_dir: str = "./cache/market_scan"):
        self._logged_in = False
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _login(self):
        if not self._logged_in:
            lg = bs.login()
            if lg.error_code == "0":
                self._logged_in = True
                logger.info("BaoStock login successful (full scanner)")
            else:
                raise RuntimeError(f"BaoStock login failed: {lg.error_msg}")

    def _logout(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False

    def _get_cache_key(self, date_str: str) -> str:
        return hashlib.md5(date_str.encode()).hexdigest()[:12]

    def _load_cache(self, key: str) -> Optional[Dict]:
        cache_file = self._cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    logger.info(f"Using cached scan results ({len(data.get('stocks', []))} stocks)")
                    return data
            except Exception:
                pass
        return None

    def _save_cache(self, key: str, data: Dict):
        cache_file = self._cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _get_stock_name(self, code: str) -> str:
        rs = bs.query_stock_basic(code=code)
        while (rs.error_code == "0") and rs.next():
            row = rs.get_row_data()
            if len(row) > 1 and row[1]:
                return row[1]
        return ""

    def _fetch_all_mainboard_codes(self) -> List[str]:
        logger.info("Fetching all mainboard stock codes...")
        rs = bs.query_stock_basic()
        codes = []
        while (rs.error_code == "0") and rs.next():
            row = rs.get_row_data()
            bs_code = row[0]
            if "." not in bs_code:
                continue
            num_part = bs_code.split(".")[1]
            if any(num_part.startswith(p) for p in self.MAINBOARD_PREFIXES):
                codes.append(bs_code)
        logger.info(f"Found {len(codes)} mainboard stocks")
        return codes

    def _fetch_history(self, code: str, start_date: str, end_date: str) -> List[List[str]]:
        rs = bs.query_history_k_data_plus(
            code,
            "date,open,high,low,close,volume,amount,turn",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="3",
        )
        data = []
        while (rs.error_code == "0") and rs.next():
            data.append(rs.get_row_data())
        return data

    def _safe_float(self, val: str, default: float = 0.0) -> float:
        try:
            if val is None or val == "":
                return default
            v = float(val)
            return v if math.isfinite(v) else default
        except (ValueError, TypeError):
            return default

    def _calc_returns(self, closes: np.ndarray) -> Dict[str, float]:
        n = len(closes)
        if n < 2:
            return {"1w": 0, "1m": 0, "3m": 0, "6m": 0, "1y": 0}

        latest = closes[-1]
        result = {}
        for label, days in [("1w", 5), ("1m", 21), ("3m", 63), ("6m", 126), ("1y", 252)]:
            idx = max(0, n - days - 1)
            base = closes[idx]
            result[label] = ((latest - base) / base * 100) if base > 0 else 0.0
        return result

    def _calc_volatility(self, daily_returns: np.ndarray) -> float:
        if len(daily_returns) < 10:
            return 0.0
        return float(np.std(daily_returns) * np.sqrt(252) * 100)

    def _calc_sharpe(self, daily_returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        if len(daily_returns) < 20:
            return 0.0
        mean_ret = float(np.mean(daily_returns) * 252)
        std_ret = float(np.std(daily_returns) * np.sqrt(252))
        if std_ret < 1e-9:
            return 0.0
        return (mean_ret - risk_free_rate) / std_ret

    def _calc_max_drawdown(self, closes: np.ndarray) -> float:
        if len(closes) < 2:
            return 0.0
        peak = closes[0]
        max_dd = 0.0
        for c in closes:
            if c > peak:
                peak = c
            dd = (peak - c) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        return max_dd * 100

    def _calc_support_resistance(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, Dict[str, float]]:
        result = {}
        for label, window in [("20", 20), ("60", 60), ("252", 252)]:
            n = min(window, len(lows))
            if n < 2:
                result[label] = {"support": 0, "resistance": 0}
                continue
            support = float(np.percentile(lows[-n:], 10))
            resistance = float(np.percentile(highs[-n:], 90))
            result[label] = {"support": round(support, 2), "resistance": round(resistance, 2)}
        return result

    def _calc_moving_averages(self, closes: np.ndarray) -> Dict[str, float]:
        result = {}
        for label, window in [("ma5", 5), ("ma10", 10), ("ma20", 20), ("ma60", 60), ("ma250", 250)]:
            if len(closes) >= window:
                result[label] = round(float(np.mean(closes[-window:])), 2)
            else:
                result[label] = 0.0
        return result

    def _calc_volume_analysis(self, volumes: np.ndarray) -> Dict[str, float]:
        if len(volumes) < 5:
            return {"avg_volume": 0, "volume_trend": 0}

        avg_vol = float(np.mean(volumes))

        if len(volumes) >= 20:
            recent = float(np.mean(volumes[-10:]))
            older = float(np.mean(volumes[-20:-10]))
            vol_trend = ((recent - older) / older * 100) if older > 0 else 0
        else:
            vol_trend = 0

        return {"avg_volume": avg_vol, "volume_trend": vol_trend}

    def _identify_trend(self, closes: np.ndarray, mas: Dict[str, float]) -> str:
        if len(closes) < 20:
            return "consolidation"

        price = closes[-1]
        ma5 = mas.get("ma5", 0)
        ma20 = mas.get("ma20", 0)
        ma60 = mas.get("ma60", 0)

        if ma5 == 0 or ma20 == 0:
            return "consolidation"

        above_ma5 = price > ma5
        above_ma20 = price > ma20
        ma5_above_ma20 = ma5 > ma20
        ma20_rising = mas.get("ma20", 0) > 0 and len(closes) > 25

        ret_20d = (closes[-1] - closes[-21]) / closes[-21] * 100 if len(closes) > 21 and closes[-21] > 0 else 0

        if above_ma5 and above_ma20 and ma5_above_ma20 and ret_20d > 10:
            return "strong_uptrend"
        elif above_ma5 and above_ma20 and ma5_above_ma20:
            return "uptrend"
        elif not above_ma5 and not above_ma20 and not ma5_above_ma20 and ret_20d < -10:
            return "strong_downtrend"
        elif not above_ma5 and not above_ma20 and not ma5_above_ma20:
            return "downtrend"
        else:
            return "consolidation"

    def _score_stock(self, metrics: StockMetrics) -> float:
        score = 0.0
        details = {}

        ret_score = 0
        if metrics.change_1w > 5:
            ret_score += 15
        elif metrics.change_1w > 2:
            ret_score += 10
        elif metrics.change_1w > 0:
            ret_score += 5
        if metrics.change_1m > 10:
            ret_score += 15
        elif metrics.change_1m > 5:
            ret_score += 10
        elif metrics.change_1m > 0:
            ret_score += 5
        if metrics.change_3m > 20:
            ret_score += 10
        elif metrics.change_3m > 5:
            ret_score += 5
        if metrics.change_1y > 30:
            ret_score += 5
        elif metrics.change_1y < -30:
            ret_score += 8
        details["return"] = min(ret_score, 50)

        trend_score = 0
        if metrics.trend == "strong_uptrend":
            trend_score = 25
        elif metrics.trend == "uptrend":
            trend_score = 18
        elif metrics.trend == "consolidation":
            trend_score = 10
        elif metrics.trend == "downtrend":
            trend_score = 3
        else:
            trend_score = 0
        details["trend"] = trend_score

        risk_score = 0
        if 0 < metrics.volatility < 20:
            risk_score += 10
        elif 20 <= metrics.volatility < 35:
            risk_score += 5
        if metrics.sharpe_ratio > 1.5:
            risk_score += 15
        elif metrics.sharpe_ratio > 0.8:
            risk_score += 10
        elif metrics.sharpe_ratio > 0.3:
            risk_score += 5
        if metrics.max_drawdown < 10:
            risk_score += 10
        elif metrics.max_drawdown < 20:
            risk_score += 5
        details["risk"] = min(risk_score, 35)

        vol_score = 0
        if metrics.avg_volume > 5_000_000:
            vol_score += 5
        elif metrics.avg_volume > 1_000_000:
            vol_score += 3
        if metrics.volume_trend > 30:
            vol_score += 8
        elif metrics.volume_trend > 10:
            vol_score += 5
        elif metrics.volume_trend > 0:
            vol_score += 2
        details["volume"] = min(vol_score, 13)

        price_score = 0
        if metrics.price > 0 and metrics.ma250 > 0:
            pct_above_250 = (metrics.price - metrics.ma250) / metrics.ma250
            if -0.1 < pct_above_250 < 0.1:
                price_score += 5
        if 8 <= metrics.price <= 18:
            price_score += 5
        elif 5 <= metrics.price < 8:
            price_score += 3
        details["price_position"] = min(price_score, 10)

        total = sum(details.values())
        metrics.score_details = details
        return total

    def scan(
        self,
        budget: float = 1900,
        max_price: float = 19.0,
        min_price: float = 3.0,
        top_n: int = 20,
        use_cache: bool = True,
    ) -> List[StockMetrics]:
        today_str = datetime.now().strftime("%Y-%m-%d")
        cache_key = self._get_cache_key(today_str)

        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                stocks = []
                for s in cached.get("stocks", []):
                    m = StockMetrics(
                        code=s["code"],
                        name=s.get("name", ""),
                        price=s["price"],
                        cost_100=s["cost_100"],
                    )
                    for k in ["change_1w", "change_1m", "change_3m", "change_6m", "change_1y",
                              "volatility", "sharpe_ratio", "max_drawdown",
                              "support_20", "support_60", "support_252",
                              "resistance_20", "resistance_60", "resistance_252",
                              "ma5", "ma10", "ma20", "ma60", "ma250",
                              "avg_volume", "volume_trend", "composite_score"]:
                        if k in s:
                            setattr(m, k, s[k])
                    m.trend = s.get("trend", "consolidation")
                    m.score_details = s.get("score_details", {})
                    m.affordable = s.get("affordable", True)
                    stocks.append(m)
                return stocks[:top_n]

        self._login()

        end_date = today_str
        start_date = (datetime.now() - timedelta(days=380)).strftime("%Y-%m-%d")

        codes = self._fetch_all_mainboard_codes()
        logger.info(f"Scanning {len(codes)} mainboard stocks ({start_date} to {end_date})...")

        all_metrics: List[StockMetrics] = []
        processed = 0
        skipped_price = 0
        skipped_data = 0
        errors = 0

        for i, code in enumerate(codes):
            if (i + 1) % 100 == 0:
                logger.info(f"Progress: {i + 1}/{len(codes)} stocks scanned, {len(all_metrics)} candidates found")

            try:
                data = self._fetch_history(code, start_date, end_date)
                if len(data) < 20:
                    skipped_data += 1
                    continue

                closes_raw = [self._safe_float(row[4]) for row in data]
                highs_raw = [self._safe_float(row[2]) for row in data]
                lows_raw = [self._safe_float(row[3]) for row in data]
                volumes_raw = [self._safe_float(row[5]) for row in data]

                closes = np.array(closes_raw, dtype=np.float64)
                highs = np.array(highs_raw, dtype=np.float64)
                lows = np.array(lows_raw, dtype=np.float64)
                volumes = np.array(volumes_raw, dtype=np.float64)

                latest_price = closes[-1]
                if latest_price <= 0:
                    skipped_data += 1
                    continue

                if latest_price > max_price or latest_price < min_price:
                    skipped_price += 1
                    continue

                cost_100 = latest_price * 100
                if cost_100 > budget:
                    skipped_price += 1
                    continue

                daily_returns = np.diff(closes) / closes[:-1]
                daily_returns = daily_returns[np.isfinite(daily_returns)]

                returns = self._calc_returns(closes)
                vol = self._calc_volatility(daily_returns)
                sharpe = self._calc_sharpe(daily_returns)
                max_dd = self._calc_max_drawdown(closes)
                sr = self._calc_support_resistance(highs, lows, closes)
                mas = self._calc_moving_averages(closes)
                vol_analysis = self._calc_volume_analysis(volumes)
                trend = self._identify_trend(closes, mas)

                name = self._get_stock_name(code)
                short_code = code.split(".")[1]

                m = StockMetrics(
                    code=short_code,
                    name=name,
                    price=round(latest_price, 2),
                    cost_100=round(cost_100, 2),
                    change_1w=round(returns["1w"], 2),
                    change_1m=round(returns["1m"], 2),
                    change_3m=round(returns["3m"], 2),
                    change_6m=round(returns["6m"], 2),
                    change_1y=round(returns["1y"], 2),
                    volatility=round(vol, 2),
                    sharpe_ratio=round(sharpe, 2),
                    max_drawdown=round(max_dd, 2),
                    support_20=sr["20"]["support"],
                    support_60=sr["60"]["support"],
                    support_252=sr["252"]["support"],
                    resistance_20=sr["20"]["resistance"],
                    resistance_60=sr["60"]["resistance"],
                    resistance_252=sr["252"]["resistance"],
                    ma5=mas["ma5"],
                    ma10=mas["ma10"],
                    ma20=mas["ma20"],
                    ma60=mas["ma60"],
                    ma250=mas["ma250"],
                    avg_volume=round(vol_analysis["avg_volume"]),
                    volume_trend=round(vol_analysis["volume_trend"], 2),
                    trend=trend,
                )

                m.composite_score = self._score_stock(m)
                all_metrics.append(m)
                processed += 1

            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"Error processing {code}: {e}")
                continue

        self._logout()

        all_metrics.sort(key=lambda x: x.composite_score, reverse=True)
        top_stocks = all_metrics[:top_n]

        logger.info(
            f"Scan complete: {processed} processed, {skipped_price} price-filtered, "
            f"{skipped_data} insufficient data, {errors} errors. "
            f"Returning top {len(top_stocks)} stocks."
        )

        cache_data = {
            "date": today_str,
            "stocks": [
                {
                    "code": m.code,
                    "name": m.name,
                    "price": m.price,
                    "cost_100": m.cost_100,
                    "change_1w": m.change_1w,
                    "change_1m": m.change_1m,
                    "change_3m": m.change_3m,
                    "change_6m": m.change_6m,
                    "change_1y": m.change_1y,
                    "volatility": m.volatility,
                    "sharpe_ratio": m.sharpe_ratio,
                    "max_drawdown": m.max_drawdown,
                    "support_20": m.support_20,
                    "support_60": m.support_60,
                    "support_252": m.support_252,
                    "resistance_20": m.resistance_20,
                    "resistance_60": m.resistance_60,
                    "resistance_252": m.resistance_252,
                    "ma5": m.ma5,
                    "ma10": m.ma10,
                    "ma20": m.ma20,
                    "ma60": m.ma60,
                    "ma250": m.ma250,
                    "avg_volume": m.avg_volume,
                    "volume_trend": m.volume_trend,
                    "trend": m.trend,
                    "composite_score": m.composite_score,
                    "score_details": m.score_details,
                    "affordable": m.affordable,
                }
                for m in all_metrics[:200]
            ],
        }
        self._save_cache(cache_key, cache_data)

        return top_stocks

    def generate_buy_plan(self, stocks: List[StockMetrics], budget: float = 1900) -> Dict[str, Any]:
        if not stocks:
            return {
                "budget": budget,
                "positions": [],
                "total_cost": 0,
                "remaining": budget,
                "summary": "未找到符合条件的股票",
            }

        positions = []
        remaining = budget

        for stock in stocks:
            if stock.cost_100 <= remaining:
                positions.append({
                    "code": stock.code,
                    "name": stock.name,
                    "price": stock.price,
                    "shares": 100,
                    "cost": stock.cost_100,
                    "score": stock.composite_score,
                    "trend": stock.trend,
                    "change_1m": stock.change_1m,
                    "volatility": stock.volatility,
                    "sharpe_ratio": stock.sharpe_ratio,
                })
                remaining -= stock.cost_100
                if len(positions) >= 3:
                    break

        total_cost = sum(p["cost"] for p in positions)

        if positions:
            pos_desc = " + ".join([f"{p['name']}({p['cost']:.0f}元)" for p in positions])
            summary = f"建议买入: {pos_desc}，总计{total_cost:.0f}元，剩余{remaining:.0f}元"
        else:
            summary = "当前预算不足或无合适标的"

        return {
            "budget": budget,
            "positions": positions,
            "total_cost": round(total_cost, 2),
            "remaining": round(remaining, 2),
            "summary": summary,
        }

    @staticmethod
    def to_dict_list(stocks: List[StockMetrics]) -> List[Dict[str, Any]]:
        result = []
        for m in stocks:
            result.append({
                "code": m.code,
                "name": m.name,
                "price": m.price,
                "cost_100": m.cost_100,
                "change_1w": m.change_1w,
                "change_1m": m.change_1m,
                "change_3m": m.change_3m,
                "change_6m": m.change_6m,
                "change_1y": m.change_1y,
                "volatility": m.volatility,
                "sharpe_ratio": m.sharpe_ratio,
                "max_drawdown": m.max_drawdown,
                "support_20": m.support_20,
                "support_60": m.support_60,
                "support_252": m.support_252,
                "resistance_20": m.resistance_20,
                "resistance_60": m.resistance_60,
                "resistance_252": m.resistance_252,
                "ma5": m.ma5,
                "ma10": m.ma10,
                "ma20": m.ma20,
                "ma60": m.ma60,
                "ma250": m.ma250,
                "avg_volume": m.avg_volume,
                "volume_trend": m.volume_trend,
                "trend": m.trend,
                "composite_score": m.composite_score,
                "score_details": m.score_details,
                "affordable": m.affordable,
            })
        return result

    @staticmethod
    def trend_label(trend: str) -> str:
        labels = {
            "strong_uptrend": "强势上涨",
            "uptrend": "上涨趋势",
            "consolidation": "横盘整理",
            "downtrend": "下跌趋势",
            "strong_downtrend": "强势下跌",
        }
        return labels.get(trend, "未知")
