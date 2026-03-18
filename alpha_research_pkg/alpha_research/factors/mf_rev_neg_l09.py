from __future__ import annotations
import pandas as pd
from .mf_base import mf_shock_reversal_panel

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """Matched filter (shock-reversal): mf_rev_neg_l09

    window=10, decay=0.9, direction='neg', vol_window=20
    """
    return mf_shock_reversal_panel(prices, window=10, decay=0.9, direction="neg", vol_window=20)
