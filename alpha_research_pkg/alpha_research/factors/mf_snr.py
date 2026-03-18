from __future__ import annotations

import numpy as np
import pandas as pd
from .base import require_columns

def _std_logret(close: pd.DataFrame, vol_window: int = 20) -> pd.DataFrame:
    logret = np.log(close / close.shift(1))
    vol = logret.rolling(vol_window, min_periods=vol_window).std()
    x = logret / vol
    return x.replace([np.inf, -np.inf], np.nan)

def _bg_subtract(x: pd.DataFrame, method: str = "median") -> pd.DataFrame:
    if method == "median":
        bg = x.median(axis=1)
    elif method == "mean":
        bg = x.mean(axis=1)
    else:
        raise ValueError("bg method must be 'median' or 'mean'")
    return x.sub(bg, axis=0)

def _ema(x: pd.DataFrame, span: int) -> pd.DataFrame:
    return x.ewm(span=span, adjust=False, min_periods=span).mean()

def snr_continuous(
    prices: pd.DataFrame,
    direction: str = "rev",  # 'rev' or 'drift'
    vol_window: int = 20,
    bg_method: str = "median",
    smooth_span: int = 3,
    soft_k: float = 1.0,
) -> pd.DataFrame:
    """Continuous SNR factor (no hard threshold).

    x_t = standardized log return (close-close): logret / rolling_std(vol_window)
    x_bg = x_t - background_t  (cross-sectional median or mean)

    Optional smoothing: EMA over time to mimic matched-filter integration.

    soft gate: tanh(k * x_bg) as a soft nonlinearity (keeps continuity, reduces outliers)

    direction:
      - drift: +score
      - rev:   -score

    Returns DataFrame indexed by date, columns=asset.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    x = _std_logret(close, vol_window=vol_window)
    x = _bg_subtract(x, method=bg_method)

    # soft nonlinearity
    score = np.tanh(float(soft_k) * x)

    # integrate over short horizon (matched filter style)
    if smooth_span and int(smooth_span) > 1:
        score = _ema(score, span=int(smooth_span))

    if direction == "drift":
        return score
    if direction == "rev":
        return -score
    raise ValueError("direction must be 'rev' or 'drift'")
