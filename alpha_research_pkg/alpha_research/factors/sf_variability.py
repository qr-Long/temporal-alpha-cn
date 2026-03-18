from __future__ import annotations

import numpy as np
import pandas as pd
from .base import require_columns

def _logret(close: pd.DataFrame) -> pd.DataFrame:
    return np.log(close / close.shift(1)).replace([np.inf, -np.inf], np.nan)

def sf_tau_panel(logret: pd.DataFrame, tau: int) -> pd.DataFrame:
    """Structure function proxy at lag tau using returns.

    SF_tau(t) = mean_{k=0..tau-1} (r_{t-k} - r_{t-k-tau})^2  (approx)
    Here we use a simple squared difference: (r_t - r_{t-tau})^2,
    then optionally smooth later in wrappers.
    """
    d = logret - logret.shift(tau)
    return (d * d)

def compute_sf_amp(
    prices: pd.DataFrame,
    tau: int = 5,
    smooth: int = 20,
) -> pd.DataFrame:
    """SF amplitude factor: rolling mean of squared return differences at lag tau.

    Feature: amp_tau = rolling_mean((r_t - r_{t-tau})^2, smooth)
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    r = _logret(close)
    sf = sf_tau_panel(r, tau=tau)
    amp = sf.rolling(smooth, min_periods=smooth).mean()
    return amp

def compute_sf_slope(
    prices: pd.DataFrame,
    taus: list[int] | tuple[int, ...] = (2, 5, 10, 20),
    smooth: int = 60,
) -> pd.DataFrame:
    """SF slope factor across multiple lags.

    For each date t and asset i:
      - compute SF amplitude at each tau: A_tau(t) = rolling_mean((r_t - r_{t-tau})^2, smooth)
      - fit log(A_tau) = a + b * log(tau) using OLS; return b as slope

    This is a common variability descriptor in time-domain astronomy.
    """
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()
    r = _logret(close)

    taus = list(taus)
    taus = [int(x) for x in taus if int(x) >= 1]
    if len(taus) < 2:
        raise ValueError("need at least 2 taus for slope")

    amps = []
    for tau in taus:
        sf = sf_tau_panel(r, tau=tau)
        amp = sf.rolling(smooth, min_periods=smooth).mean()
        amps.append(amp)

    # stack: shape (T, N, K)
    # We'll compute slope per (t, asset) by closed-form regression on log-space.
    X = np.log(np.array(taus, dtype=float))
    Xc = X - X.mean()
    denom = float(np.sum(Xc * Xc))
    if denom == 0:
        denom = 1.0

    # log amps
    logs = []
    for amp in amps:
        logs.append(np.log(amp.replace(0, np.nan)))
    # logs is list of DataFrame (T,N); compute slope:
    # b = sum_k (Xc_k * (Y_k - Ymean)) / denom
    Y_stack = np.stack([df.to_numpy(dtype=float) for df in logs], axis=2)  # T,N,K
    Y_mean = np.nanmean(Y_stack, axis=2, keepdims=True)
    num = np.nansum((Y_stack - Y_mean) * Xc.reshape(1, 1, -1), axis=2)
    b = num / denom
    out = pd.DataFrame(b, index=close.index, columns=close.columns)
    return out
