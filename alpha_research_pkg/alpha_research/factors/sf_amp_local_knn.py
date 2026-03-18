from __future__ import annotations

import numpy as np
import pandas as pd
from .base import require_columns

EPS = 1e-12


def _close_panel(prices: pd.DataFrame) -> pd.DataFrame:
    require_columns(prices, ["close"])
    return prices["close"].unstack("asset").sort_index()


def _logret(close: pd.DataFrame) -> pd.DataFrame:
    return np.log(close / close.shift(1)).replace([np.inf, -np.inf], np.nan)


def sf_amp_core(prices: pd.DataFrame, tau: int = 5, smooth: int = 20) -> pd.DataFrame:
    close = _close_panel(prices)
    r = _logret(close)
    d = r - r.shift(tau)
    sf = d * d
    return sf.rolling(smooth, min_periods=smooth).mean()


def _feature_panels(close: pd.DataFrame) -> list[pd.DataFrame]:
    r = _logret(close)
    mom20 = close.pct_change(20, fill_method=None)
    mom60 = close.pct_change(60, fill_method=None)
    vol20 = r.rolling(20, min_periods=20).std()
    vol60 = r.rolling(60, min_periods=60).std()
    return [mom20, mom60, vol20, vol60]


def _knn_local_bg_one_day(
    source_row: pd.Series,
    feat_rows: list[pd.Series],
    k: int = 10,
    mode: str = "bg",
) -> pd.Series:
    df = pd.DataFrame({"source": source_row})
    for i, s in enumerate(feat_rows):
        df[f"x{i}"] = s

    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    if len(df) < max(k + 2, 20):
        return pd.Series(index=source_row.index, dtype=float)

    X = df[[c for c in df.columns if c.startswith("x")]].to_numpy(dtype=float)
    mu = np.nanmean(X, axis=0, keepdims=True)
    sd = np.nanstd(X, axis=0, keepdims=True)
    sd = np.where(sd == 0, 1.0, sd)
    X = (X - mu) / sd

    G = X @ X.T
    H = np.sum(X * X, axis=1, keepdims=True)
    D = H + H.T - 2.0 * G
    D = np.maximum(D, 0.0)
    np.fill_diagonal(D, np.inf)

    src = df["source"].to_numpy(dtype=float)
    out = np.full(len(df), np.nan, dtype=float)
    kk = min(k, len(df) - 1)

    for i in range(len(df)):
        nbr_idx = np.argpartition(D[i], kk)[:kk]
        nbr_vals = src[nbr_idx]
        bg = np.nanmedian(nbr_vals)
        if mode == "bg":
            out[i] = src[i] - bg
        elif mode == "snr":
            mad = np.nanmedian(np.abs(nbr_vals - bg))
            out[i] = (src[i] - bg) / (mad + EPS)
        else:
            raise ValueError("mode must be 'bg' or 'snr'")

    result = pd.Series(index=source_row.index, dtype=float)
    result.loc[df.index] = out
    return result


def sf_amp_localbg_knn(prices: pd.DataFrame, tau: int = 5, smooth: int = 20, k: int = 10) -> pd.DataFrame:
    close = _close_panel(prices)
    amp = sf_amp_core(prices, tau=tau, smooth=smooth)
    feats = _feature_panels(close)

    out = pd.DataFrame(index=amp.index, columns=amp.columns, dtype=float)
    for dt in amp.index:
        source_row = amp.loc[dt]
        feat_rows = [f.loc[dt] for f in feats]
        out.loc[dt] = _knn_local_bg_one_day(source_row, feat_rows, k=k, mode="bg")
    return out


def sf_amp_localsnr_knn(prices: pd.DataFrame, tau: int = 5, smooth: int = 20, k: int = 10) -> pd.DataFrame:
    close = _close_panel(prices)
    amp = sf_amp_core(prices, tau=tau, smooth=smooth)
    feats = _feature_panels(close)

    out = pd.DataFrame(index=amp.index, columns=amp.columns, dtype=float)
    for dt in amp.index:
        source_row = amp.loc[dt]
        feat_rows = [f.loc[dt] for f in feats]
        out.loc[dt] = _knn_local_bg_one_day(source_row, feat_rows, k=k, mode="snr")
    return out
