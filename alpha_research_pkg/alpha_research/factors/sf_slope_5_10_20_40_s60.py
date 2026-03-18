from __future__ import annotations
import pandas as pd
from .sf_variability import compute_sf_slope

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """sf_slope_5_10_20_40_s60: Structure Function slope across taus."""
    return compute_sf_slope(prices, taus=(5, 10, 20, 40), smooth=60)
