from typing import Dict, Any, List, Optional
import statistics


def safe_prices(comps: List[Dict[str, Any]]) -> List[float]:
    prices = []
    for c in comps or []:
        p = c.get("price")
        if isinstance(p, (int, float)) and p > 0:
            prices.append(float(p))
    return prices


def recommend(item: Dict[str, Any], comps: List[Dict[str, Any]]) -> Dict[str, Any]:
    prices = safe_prices(comps)
    market_avg = statistics.mean(prices) if prices else None
    market_med = statistics.median(prices) if prices else None

    buy = float(item.get("buy_price", 0) or 0)
    repair = float(item.get("repair_cost", 0) or 0)
    fees_pct = float(item.get("fees_pct", 0) or 0)

    # if no comps, fallback guess
    target_price = market_med if market_med else 0.0
    fees = (fees_pct / 100.0) * target_price
    profit = target_price - (buy + repair + fees)

    return {
        "market_avg_price": market_avg,
        "market_median_price": market_med,
        "suggested_list_price": target_price,
        "estimated_fees": fees,
        "estimated_profit": profit,
        "note": "If comps have no prices, refine query or use item model name."
    }
