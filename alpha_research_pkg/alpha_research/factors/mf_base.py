from __future__ import annotations

import numpy as np
import pandas as pd
from .base import require_columns

def _make_template_shock_reversal(window: int, decay: float, direction: str) -> np.ndarray:
    """Template: shock at k=0 then opposite-sign exponential tail.

    direction:
      - 'pos': +shock then negative tail (reversal / mean reversion)
      - 'neg': -shock then positive tail (reversal / rebound)
    """
    if window < 2:
        raise ValueError("window must be >= 2")
    if not (0 < decay < 1):
        raise ValueError("decay must be in (0,1)")
    h = np.zeros(window, dtype=float)
    h[0] = 1.0
    for k in range(1, window):
        h[k] = -(decay ** k)
    if direction == "neg":
        h = -h
    elif direction != "pos":
        raise ValueError("direction must be 'pos' or 'neg'")
    # normalize to unit norm for comparability across decay
    n = float(np.linalg.norm(h))
    if n > 0:
        h = h / n
    return h

def matched_filter_score(prices: pd.DataFrame, template: np.ndarray, vol_window: int = 20) -> pd.DataFrame:
    """Matched-filter score on standardized log returns.

    x_t = log(close_t/close_{t-1}) / rolling_std(logret, vol_window)
    score_t = sum_{k=0..W-1} h_k * x_{t-k}
    Returns a DataFrame indexed by date with columns=asset.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    logret = np.log(close / close.shift(1))
    vol = logret.rolling(vol_window, min_periods=vol_window).std()
    x = logret / vol
    x = x.replace([np.inf, -np.inf], np.nan)

    W = int(len(template))
    score = 0.0
    for k in range(W):
        score = score + float(template[k]) * x.shift(k)
    return score

def mf_shock_reversal_panel(
    prices: pd.DataFrame,
    window: int = 10,
    decay: float = 0.8,
    direction: str = "pos",
    vol_window: int = 20,
) -> pd.DataFrame:
    """Convenience wrapper for shock-reversal matched filter."""
    h = _make_template_shock_reversal(window=window, decay=decay, direction=direction)
    return matched_filter_score(prices, template=h, vol_window=vol_window)
