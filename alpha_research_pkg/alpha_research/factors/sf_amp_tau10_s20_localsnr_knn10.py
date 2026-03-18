from __future__ import annotations
import pandas as pd
from .sf_amp_local_knn import sf_amp_localsnr_knn

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    return sf_amp_localsnr_knn(prices, tau=10, smooth=20, k=10)
