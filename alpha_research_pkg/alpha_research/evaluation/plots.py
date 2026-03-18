from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .perf_stats import cumulative_nav, drawdown_series, yearly_returns


FIG_DPI = 150


def _prepare_outpath(outpath: str | Path) -> Path:
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    return outpath



def _finalize_plot(outpath: str | Path):
    plt.tight_layout()
    plt.savefig(outpath, dpi=FIG_DPI)
    plt.close()



def plot_nav(net_returns: pd.Series, outpath: str | Path, title: str):
    outpath = _prepare_outpath(outpath)
    nav = cumulative_nav(net_returns)
    plt.figure(figsize=(9, 4.8))
    plt.plot(nav.index, nav.values)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Net Asset Value")
    plt.grid(alpha=0.25)
    _finalize_plot(outpath)



def plot_drawdown(net_returns: pd.Series, outpath: str | Path, title: str):
    outpath = _prepare_outpath(outpath)
    dd = drawdown_series(cumulative_nav(net_returns))
    plt.figure(figsize=(9, 4.8))
    plt.plot(dd.index, dd.values)
    plt.axhline(0.0)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.grid(alpha=0.25)
    _finalize_plot(outpath)



def plot_ic_series(ic: pd.Series, outpath: str | Path, title: str, ylabel: str):
    outpath = _prepare_outpath(outpath)
    s = ic.sort_index()
    plt.figure(figsize=(9, 4.8))
    plt.plot(s.index, s.values)
    plt.axhline(0.0)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.grid(alpha=0.25)
    _finalize_plot(outpath)



def plot_rank_ic(rank_ic: pd.Series, outpath: str | Path, title: str):
    plot_ic_series(rank_ic, outpath, title, "RankIC (Spearman)")



def plot_turnover(turnover: pd.Series, outpath: str | Path, title: str):
    outpath = _prepare_outpath(outpath)
    s = turnover.sort_index()
    plt.figure(figsize=(9, 4.8))
    plt.plot(s.index, s.values)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("One-way Turnover")
    plt.grid(alpha=0.25)
    _finalize_plot(outpath)



def plot_yearly_returns(net_returns: pd.Series, outpath: str | Path, title: str):
    outpath = _prepare_outpath(outpath)
    yr = yearly_returns(net_returns)
    labels = [str(int(x)) for x in yr.index] if len(yr) else []
    plt.figure(figsize=(9, 4.8))
    plt.bar(labels, yr.values)
    plt.axhline(0.0)
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("Net Return")
    plt.grid(axis="y", alpha=0.25)
    _finalize_plot(outpath)



def plot_cost_sensitivity(sens_df: pd.DataFrame, outpath: str | Path, title: str):
    outpath = _prepare_outpath(outpath)
    df = sens_df.sort_values("total_cost_bps")
    plt.figure(figsize=(9, 4.8))
    plt.plot(df["total_cost_bps"], df["ann_return"], marker="o")
    plt.axhline(0.0)
    plt.title(title)
    plt.xlabel("Total Cost (bps)")
    plt.ylabel("Annual Return")
    plt.grid(alpha=0.25)
    _finalize_plot(outpath)



def plot_ic_distributions(ic: pd.Series, rank_ic: pd.Series, outpath: str | Path, title: str):
    outpath = _prepare_outpath(outpath)
    ic = ic.dropna()
    rank_ic = rank_ic.dropna()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].hist(ic.values, bins=30)
    axes[0].axvline(0.0)
    axes[0].set_title("IC Distribution")
    axes[0].set_xlabel("IC")
    axes[0].set_ylabel("Frequency")
    axes[0].grid(alpha=0.25)

    axes[1].hist(rank_ic.values, bins=30)
    axes[1].axvline(0.0)
    axes[1].set_title("RankIC Distribution")
    axes[1].set_xlabel("RankIC")
    axes[1].set_ylabel("Frequency")
    axes[1].grid(alpha=0.25)

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=FIG_DPI)
    plt.close(fig)



def compute_quantile_return_summary(
    factor: pd.DataFrame,
    fwd_ret: pd.DataFrame,
    quantiles: int = 5,
    min_obs: int = 20,
) -> pd.Series:
    common_dates = factor.index.intersection(fwd_ret.index)
    daily_rows = []
    labels = [f"Q{i}" for i in range(1, quantiles + 1)]

    for dt in common_dates:
        x = factor.loc[dt]
        y = fwd_ret.loc[dt]
        df = pd.concat([x, y], axis=1, keys=["x", "y"]).dropna()
        if len(df) < min_obs:
            continue
        try:
            bins = pd.qcut(
                df["x"].rank(method="first"),
                q=quantiles,
                labels=False,
                duplicates="drop",
            )
        except ValueError:
            continue

        row = {}
        for q in range(int(bins.min()), int(bins.max()) + 1):
            grp = df.loc[bins == q, "y"]
            row[f"Q{q + 1}"] = float(grp.mean()) if len(grp) else np.nan
        daily_rows.append(pd.Series(row, name=dt))

    if not daily_rows:
        out = pd.Series(index=labels, dtype=float)
        out.loc[:] = np.nan
        return out

    panel = pd.DataFrame(daily_rows).reindex(columns=labels)
    return panel.mean(axis=0)



def plot_quantile_returns(
    factor: pd.DataFrame,
    fwd_ret: pd.DataFrame,
    outpath: str | Path,
    title: str,
    quantiles: int = 5,
    min_obs: int = 20,
):
    outpath = _prepare_outpath(outpath)
    qret = compute_quantile_return_summary(
        factor=factor,
        fwd_ret=fwd_ret,
        quantiles=quantiles,
        min_obs=min_obs,
    )
    labels = list(qret.index)
    values = qret.values.astype(float)
    spread = float(values[-1] - values[0]) if len(values) >= 2 and not np.isnan(values[[0, -1]]).any() else float("nan")

    plt.figure(figsize=(9, 4.8))
    plt.bar(labels, values)
    plt.axhline(0.0)
    if not np.isnan(spread):
        plt.title(f"{title} (Top-Bottom={spread:.4f})")
    else:
        plt.title(title)
    plt.xlabel("Quantile")
    plt.ylabel("Average Forward Return")
    plt.grid(axis="y", alpha=0.25)
    _finalize_plot(outpath)
