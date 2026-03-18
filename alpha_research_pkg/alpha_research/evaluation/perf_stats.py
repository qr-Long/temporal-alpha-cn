from __future__ import annotations
import numpy as np
import pandas as pd


def cumulative_nav(r: pd.Series) -> pd.Series:
    return (1.0 + r.fillna(0.0)).cumprod()



def drawdown_series(nav: pd.Series) -> pd.Series:
    peak = nav.cummax()
    return nav / peak - 1.0



def max_drawdown(nav: pd.Series) -> float:
    dd = drawdown_series(nav)
    return float(dd.min())



def yearly_returns(net_returns: pd.Series) -> pd.Series:
    r = net_returns.dropna().copy()
    if len(r) == 0:
        return pd.Series(dtype=float, name="yearly_return")
    idx = pd.to_datetime(r.index)
    grouped = (1.0 + r).groupby(idx.year).prod() - 1.0
    grouped.name = "yearly_return"
    return grouped



def perf_summary(net_returns: pd.Series, freq: int = 252) -> dict:
    r = net_returns.dropna()
    if len(r) == 0:
        return {
            "n_days": 0,
            "ann_return": float("nan"),
            "ann_vol": float("nan"),
            "sharpe": float("nan"),
            "max_dd": float("nan"),
        }
    nav = cumulative_nav(r)
    ann_return = float(nav.iloc[-1] ** (freq / len(r)) - 1.0)
    ann_vol = float(r.std(ddof=0) * np.sqrt(freq))
    sharpe = float((r.mean() / r.std(ddof=0)) * np.sqrt(freq)) if r.std(ddof=0) != 0 else float("nan")
    mdd = max_drawdown(nav)
    return {
        "n_days": int(len(r)),
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_dd": mdd,
    }
