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

def _vol_spike(volume: pd.DataFrame, win: int = 20) -> pd.DataFrame:
    # log(volume / rolling_mean(volume))
    mv = volume.rolling(win, min_periods=win).mean()
    s = np.log(volume / mv)
    return s.replace([np.inf, -np.inf], np.nan)

def impulse_event_factor(
    prices: pd.DataFrame,
    direction: str = "rev",  # 'rev' or 'drift'
    threshold: float = 1.5,
    vol_window: int = 20,
    bg_method: str = "median",
    use_volume: bool = False,
    vol_spike_win: int = 20,
    vol_beta: float = 1.0,
) -> pd.DataFrame:
    """Impulse matched-filter family (event-triggered).

    x_t = standardized log return (close-close): logret / rolling_std(vol_window)
    x_bg = x_t - background_t  (cross-sectional median or mean)
    trigger = 1(|x_bg| >= threshold)
    base signal:
      - drift:  +x_bg * trigger
      - rev:    -x_bg * trigger
    optional volume weighting:
      v = 1 + vol_beta * clip(vol_spike, 0, +inf)
      signal *= v

    Returns DataFrame indexed by date, columns=asset.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    x = _std_logret(close, vol_window=vol_window)
    x = _bg_subtract(x, method=bg_method)

    trig = (x.abs() >= float(threshold)).astype(float)

    if direction == "drift":
        sig = x * trig
    elif direction == "rev":
        sig = -x * trig
    else:
        raise ValueError("direction must be 'rev' or 'drift'")

    if use_volume:
        require_columns(prices, ["volume"])
        vol = prices["volume"].unstack("asset").sort_index()
        vs = _vol_spike(vol, win=vol_spike_win)
        vs_pos = vs.clip(lower=0.0)
        w = 1.0 + float(vol_beta) * vs_pos
        sig = sig * w

    return sig
