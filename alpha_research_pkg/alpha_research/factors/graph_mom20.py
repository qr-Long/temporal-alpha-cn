from __future__ import annotations

import numpy as np
import pandas as pd
from .base import require_columns

def _build_corr_graph(ret_window: pd.DataFrame, k: int = 10) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Sparse Top-K positive-correlation neighbor graph."""
    assets = ret_window.columns.to_list()
    corr = ret_window.corr()

    graph: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    asset_to_idx = {a: i for i, a in enumerate(assets)}

    for i, a in enumerate(assets):
        row = corr.iloc[i].copy()
        row.loc[a] = np.nan
        row = row[row > 0].dropna()
        if row.empty:
            graph[a] = (np.array([], dtype=int), np.array([], dtype=float))
            continue
        top = row.sort_values(ascending=False).head(k)
        neigh_assets = top.index.to_list()
        w = top.values.astype(float)
        s = w.sum()
        if not np.isfinite(s) or s <= 0:
            graph[a] = (np.array([], dtype=int), np.array([], dtype=float))
            continue
        w = w / s
        neigh_idx = np.array([asset_to_idx[na] for na in neigh_assets], dtype=int)
        graph[a] = (neigh_idx, w)
    return graph

def compute_factor_panel(
    prices: pd.DataFrame,
    mom_lookback: int = 20,
    corr_lookback: int = 60,
    top_k: int = 10,
    alpha: float = 0.5,
    update_freq: int = 5,
    min_corr_obs_ratio: float = 0.7,
) -> pd.DataFrame:
    """Graph Diffusion Momentum Factor (20d momentum diffused on correlation graph)."""
    require_columns(prices, ["close"])
    close = prices["close"].unstack("asset").sort_index()

    mom = close.pct_change(mom_lookback, fill_method=None)
    ret = close.pct_change(1, fill_method=None)

    dates = mom.index
    assets = mom.columns.to_list()

    out = pd.DataFrame(index=dates, columns=assets, dtype=float)

    graph_cache: dict[str, tuple[np.ndarray, np.ndarray]] | None = None
    keep_assets: list[str] = []

    for t_idx, _t in enumerate(dates):
        if t_idx < max(mom_lookback, corr_lookback) + 2:
            continue

        if graph_cache is None or (t_idx % update_freq == 0):
            win = ret.iloc[t_idx - corr_lookback + 1 : t_idx + 1]
            min_obs = int(np.ceil(corr_lookback * min_corr_obs_ratio))
            good = win.count(axis=0)
            keep_assets = good[good >= min_obs].index.to_list()
            win2 = win[keep_assets]
            graph_cache = _build_corr_graph(win2, k=top_k)

        m_row = mom.iloc[t_idx]
        # if no graph, fallback to self mom
        if not graph_cache or not keep_assets:
            out.iloc[t_idx] = m_row
            continue

        m_sub = m_row.reindex(keep_assets).to_numpy(dtype=float)
        agg = np.full(len(keep_assets), np.nan, dtype=float)

        for i, a in enumerate(keep_assets):
            neigh_idx, w = graph_cache.get(a, (np.array([], dtype=int), np.array([], dtype=float)))
            if neigh_idx.size == 0:
                continue
            neigh_vals = m_sub[neigh_idx]
            mask = np.isfinite(neigh_vals) & np.isfinite(w)
            if mask.sum() == 0:
                continue
            w2 = w[mask]
            s = w2.sum()
            if s <= 0:
                continue
            w2 = w2 / s
            agg[i] = float(np.dot(w2, neigh_vals[mask]))

        m_sub_s = pd.Series(m_sub, index=keep_assets)
        agg_s = pd.Series(agg, index=keep_assets)
        f_sub = alpha * m_sub_s + (1.0 - alpha) * agg_s
        f_sub = f_sub.where(np.isfinite(f_sub), m_sub_s)

        f_row = pd.Series(index=assets, dtype=float)
        f_row.loc[keep_assets] = f_sub
        missing = [a for a in assets if a not in keep_assets]
        if missing:
            f_row.loc[missing] = m_row.reindex(missing)

        out.iloc[t_idx] = f_row

    out.name = "graph_mom20"
    return out
