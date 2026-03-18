from __future__ import annotations
import pandas as pd
from .sf_variability import compute_sf_amp

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """sf_amp_tau5_s20: Structure Function amplitude."""
    return compute_sf_amp(prices, tau=5, smooth=20)
