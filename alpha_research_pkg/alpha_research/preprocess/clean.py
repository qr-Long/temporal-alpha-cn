from __future__ import annotations
import numpy as np
import pandas as pd

def winsorize_mad(x: pd.Series, k: float = 5.0) -> pd.Series:
    x = x.astype(float)
    med = x.median()
    mad = (x - med).abs().median()
    if pd.isna(mad) or mad == 0:
        return x
    # 1.4826 * MAD ~ std for normal
    scale = 1.4826 * mad
    lo, hi = med - k * scale, med + k * scale
    return x.clip(lo, hi)

def winsorize_percentile(x: pd.Series, p_low: float = 0.01, p_high: float = 0.99) -> pd.Series:
    lo = x.quantile(p_low)
    hi = x.quantile(p_high)
    return x.clip(lo, hi)

def zscore(x: pd.Series) -> pd.Series:
    mu = x.mean()
    sd = x.std(ddof=0)
    if pd.isna(sd) or sd == 0:
        return x * 0.0
    return (x - mu) / sd

def preprocess_factor_cs(
    factor: pd.DataFrame,
    winsorize_method: str = "mad",
    k: float = 5.0,
    p_low: float = 0.01,
    p_high: float = 0.99,
    standardize: str = "zscore",
    fillna: str = "drop",
) -> pd.DataFrame:
    """Cross-sectional preprocessing per date."""
    out = []
    for dt, row in factor.iterrows():
        s = row.copy()
        if fillna == "median":
            s = s.fillna(s.median())
        else:
            # drop handled later by leaving NaN
            pass

        if winsorize_method == "mad":
            s = winsorize_mad(s, k=k)
        elif winsorize_method == "percentile":
            s = winsorize_percentile(s, p_low=p_low, p_high=p_high)
        elif winsorize_method == "none":
            pass
        else:
            raise ValueError(f"Unknown winsorize method: {winsorize_method}")

        if standardize == "zscore":
            s = zscore(s)
        elif standardize == "none":
            pass
        else:
            raise ValueError(f"Unknown standardize: {standardize}")

        out.append(s)

    out_df = pd.DataFrame(out, index=factor.index, columns=factor.columns)
    return out_df
