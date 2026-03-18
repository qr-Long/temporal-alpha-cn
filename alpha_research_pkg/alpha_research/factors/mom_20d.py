from __future__ import annotations
import pandas as pd
from .base import require_columns

def compute_factor_panel(prices: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
    """Pure 20-day momentum: close(t)/close(t-lookback) - 1"""
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    mom = close.pct_change(lookback, fill_method=None)
    mom.name = f"mom_{lookback}d"
    return mom
