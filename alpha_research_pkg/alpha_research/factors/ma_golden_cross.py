from __future__ import annotations
import pandas as pd
from .base import require_columns

def compute_factor_panel(prices: pd.DataFrame, short: int = 5, long: int = 20) -> pd.DataFrame:
    """均线金叉（强度版）
    ma_s = MA(close, short)
    ma_l = MA(close, long)
    factor = (ma_s - ma_l) / ma_l

    Input: prices panel with MultiIndex (date, asset) and 'close'.
    Output: DataFrame indexed by date, columns=asset, values=factor.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    ma_s = close.rolling(short, min_periods=short).mean()
    ma_l = close.rolling(long, min_periods=long).mean()
    fac = (ma_s - ma_l) / ma_l
    fac.name = "mem_ma_gc"
    return fac
