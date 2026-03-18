from __future__ import annotations
import pandas as pd
from .sf_variability import compute_sf_slope

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """sf_slope_2_5_10_20_s60: Structure Function slope across taus."""
    return compute_sf_slope(prices, taus=(2, 5, 10, 20), smooth=60)
