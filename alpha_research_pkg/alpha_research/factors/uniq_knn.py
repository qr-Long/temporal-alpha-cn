from __future__ import annotations

import numpy as np
import pandas as pd
from .base import require_columns

def _zscore_cs(x: np.ndarray) -> np.ndarray:
    mu = np.nanmean(x, axis=0, keepdims=True)
    sd = np.nanstd(x, axis=0, keepdims=True)
    sd = np.where(sd == 0, 1.0, sd)
    return (x - mu) / sd

def compute_factor_panel(
    prices: pd.DataFrame,
    lookback_long: int = 60,
    lookback_short: int = 20,
    top_k: int = 5,
    update_freq: int = 5,
    min_obs_ratio: float = 0.8,
) -> pd.DataFrame:
    """Uniqueness (KNN-substitutability) factor.

    Feature vector z_i(t) (4-dim):
      - mom_20 = close(t)/close(t-20) - 1
      - mom_60 = close(t)/close(t-60) - 1
      - vol_20 = std(ret_1d, 20)
      - vol_60 = std(ret_1d, 60)

    For each update date t (every update_freq trading days):
      1) build cross-sectional standardized features
      2) compute cosine similarity matrix
      3) substitutability_i = mean(top_k positive similarities)
      4) uniq_knn_i = -substitutability_i  (higher = more unique / less substitutable)

    Between update dates, factor is held constant (forward-filled).

    Returns:
      DataFrame index=date, columns=asset with factor values.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    ret = close.pct_change(1, fill_method=None)

    mom20 = close.pct_change(lookback_short, fill_method=None)
    mom60 = close.pct_change(lookback_long, fill_method=None)
    vol20 = ret.rolling(lookback_short, min_periods=lookback_short).std()
    vol60 = ret.rolling(lookback_long, min_periods=lookback_long).std()

    dates = close.index
    assets = close.columns.to_list()
    out = pd.DataFrame(index=dates, columns=assets, dtype=float)

    last_row = None

    min_obs = int(np.ceil(lookback_long * min_obs_ratio))

    for t_idx, t in enumerate(dates):
        # Need enough history for long lookback
        if t_idx < lookback_long + 2:
            continue

        if (t_idx % update_freq != 0) and (last_row is not None):
            out.iloc[t_idx] = last_row
            continue

        # Build feature matrix for this date
        f = pd.DataFrame({
            "mom20": mom20.iloc[t_idx],
            "mom60": mom60.iloc[t_idx],
            "vol20": vol20.iloc[t_idx],
            "vol60": vol60.iloc[t_idx],
        })

        # Keep assets with finite features
        valid = f.replace([np.inf, -np.inf], np.nan).dropna()
        if len(valid) < (top_k + 5):
            # too few assets to form neighbors
            last_row = mom60.iloc[t_idx] * 0.0
            out.iloc[t_idx] = last_row
            continue

        X = valid.values.astype(float)

        # Cross-sectional standardization
        X = _zscore_cs(X)

        # Cosine normalization
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        Xn = X / norms

        sim = Xn @ Xn.T
        np.fill_diagonal(sim, -np.inf)

        # Keep only positive similarity for substitutability
        sim_pos = np.maximum(sim, 0.0)

        # Compute mean top-k positive similarities per row
        # Use partial sort for efficiency
        k = min(top_k, sim_pos.shape[1] - 1)
        if k <= 0:
            sub = np.zeros(sim_pos.shape[0], dtype=float)
        else:
            part = np.partition(sim_pos, -k, axis=1)[:, -k:]
            sub = np.nanmean(part, axis=1)

        uniq = -sub  # higher -> more unique

        row = pd.Series(index=assets, dtype=float)
        row.loc[valid.index] = uniq
        # others remain NaN; let downstream preprocessing handle

        last_row = row
        out.iloc[t_idx] = row

    return out
