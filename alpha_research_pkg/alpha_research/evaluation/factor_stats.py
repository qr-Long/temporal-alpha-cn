from __future__ import annotations
import pandas as pd
import numpy as np

def _pearson_corr(a: pd.Series, b: pd.Series) -> float:
    corr = a.corr(b, method="pearson")
    return float(corr) if corr is not None else float("nan")

def _spearman_corr(a: pd.Series, b: pd.Series) -> float:
    # Spearman = Pearson correlation of rank-transformed variables
    ar = a.rank(method="average")
    br = b.rank(method="average")
    corr = ar.corr(br, method="pearson")
    return float(corr) if corr is not None else float("nan")

def ic_series(factor: pd.DataFrame, fwd_ret: pd.DataFrame, min_obs: int = 50) -> pd.Series:
    """Daily Pearson IC between factor(t) and forward returns aligned to date t."""
    common_dates = factor.index.intersection(fwd_ret.index)
    ics = []
    for dt in common_dates:
        x = factor.loc[dt]
        y = fwd_ret.loc[dt]
        df = pd.concat([x, y], axis=1, keys=["x", "y"]).dropna()
        if len(df) < min_obs:
            ics.append(np.nan)
            continue
        ics.append(_pearson_corr(df["x"], df["y"]))
    return pd.Series(ics, index=common_dates, name="ic")

def rank_ic_series(factor: pd.DataFrame, fwd_ret: pd.DataFrame, min_obs: int = 50) -> pd.Series:
    """Daily Spearman RankIC between factor(t) and forward returns aligned to date t."""
    common_dates = factor.index.intersection(fwd_ret.index)
    ics = []
    for dt in common_dates:
        x = factor.loc[dt]
        y = fwd_ret.loc[dt]
        df = pd.concat([x, y], axis=1, keys=["x", "y"]).dropna()
        if len(df) < min_obs:
            ics.append(np.nan)
            continue
        ics.append(_spearman_corr(df["x"], df["y"]))
    return pd.Series(ics, index=common_dates, name="rank_ic")

def corr_summary(s: pd.Series) -> dict:
    s = s.dropna()
    if len(s) == 0:
        return {"mean": float("nan"), "std": float("nan"), "icir": float("nan"), "n": 0}
    mean = float(s.mean())
    std = float(s.std(ddof=0))
    icir = float(mean / std) if std != 0 else float("nan")
    return {"mean": mean, "std": std, "icir": icir, "n": int(len(s))}

def ic_summary(ic: pd.Series) -> dict:
    return corr_summary(ic)

def rank_ic_summary(rank_ic: pd.Series) -> dict:
    return corr_summary(rank_ic)
