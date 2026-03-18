from __future__ import annotations
import pandas as pd

def trade_notional(weight_old: pd.Series, weight_new: pd.Series) -> float:
    """Total traded notional in weight space: sum(|Δw|)."""
    w_old = weight_old.reindex(weight_new.index).fillna(0.0)
    w_new = weight_new.fillna(0.0)
    return float((w_new - w_old).abs().sum())

def turnover_oneway(weight_old: pd.Series, weight_new: pd.Series) -> float:
    """Standard one-way turnover: 0.5 * sum(|Δw|)."""
    return 0.5 * trade_notional(weight_old, weight_new)

def cost_from_trade_notional(traded_notional: float, total_cost_bps: float) -> float:
    return traded_notional * (total_cost_bps / 10000.0)
