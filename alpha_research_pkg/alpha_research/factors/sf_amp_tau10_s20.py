from __future__ import annotations
import pandas as pd
from .sf_variability import compute_sf_amp

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """sf_amp_tau10_s20: Structure Function amplitude."""
    return compute_sf_amp(prices, tau=10, smooth=20)
