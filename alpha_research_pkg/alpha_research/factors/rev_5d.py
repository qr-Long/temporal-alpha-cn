from __future__ import annotations
import pandas as pd
from .base import require_columns

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """5日反转因子: rev_5d(t) = - (close_t / close_{t-5} - 1)

    Input: prices panel with MultiIndex (date, asset) and 'close'.
    Output: DataFrame indexed by date, columns=asset, values=factor.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    rev = -close.pct_change(5, fill_method=None)
    rev.name = "rev_5d"
    return rev
