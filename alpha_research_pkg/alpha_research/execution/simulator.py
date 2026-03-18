from __future__ import annotations

import numpy as np
import pandas as pd

from .cost import trade_notional, turnover_oneway, cost_from_trade_notional


def compute_open_to_open_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute per-asset open->open forward returns aligned to factor date t.

    For factor date t:
      - enter at open_{t+1}
      - exit at open_{t+2}
      => fwd_ret(t) = open_{t+2} / open_{t+1} - 1

    Tencent data may contain missing/0 opens; we sanitize:
      - any non-positive open prices -> NaN
      - inf/-inf -> NaN
    """
    open_px = prices["open"].unstack("asset").sort_index()

    den = open_px.shift(-1)  # open_{t+1}
    num = open_px.shift(-2)  # open_{t+2}
    ret = num / den - 1.0

    ret = ret.where((den > 0) & (num > 0))
    ret = ret.replace([np.inf, -np.inf], np.nan)
    return ret


def backtest_daily(
    factor: pd.DataFrame,
    prices: pd.DataFrame,
    weight_func,
    total_cost_bps: float,
    quantiles: int,
    long_short: bool,
    gross_leverage: float,
    weighting: str,
    max_weight_per_name: float | None,
) -> pd.DataFrame:
    """Daily rebalance backtest with t signal -> t+1 open trade, open->open returns.

    We label PnL by signal date t (the day factor is computed).
    Returns are realized from open_{t+1} -> open_{t+2}.
    """
    f = factor.sort_index()
    fwd = compute_open_to_open_returns(prices).reindex(f.index)

    dates = f.index
    w_prev = pd.Series(dtype=float)
    records = []

    for t in dates:
        fac_row = f.loc[t]
        w_tgt = weight_func(
            fac_row,
            quantiles=quantiles,
            long_short=long_short,
            gross_leverage=gross_leverage,
            weighting=weighting,
            max_weight_per_name=max_weight_per_name,
        )

        # No signal / no positions
        if w_tgt is None or len(w_tgt) == 0:
            records.append({
                "date": t,
                "gross_return": 0.0,
                "cost": 0.0,
                "net_return": 0.0,
                "turnover": 0.0,
                "n_positions": 0,
                "n_long": 0,
                "n_short": 0,
                "net_exposure": 0.0,
                "gross_exposure": 0.0,
            })
            w_prev = pd.Series(dtype=float)
            continue

        r = fwd.loc[t].reindex(w_tgt.index)
        r = r.replace([np.inf, -np.inf], np.nan)
        valid = r.dropna().index

        if len(valid) == 0:
            records.append({
                "date": t,
                "gross_return": 0.0,
                "cost": 0.0,
                "net_return": 0.0,
                "turnover": 0.0,
                "n_positions": 0,
                "n_long": 0,
                "n_short": 0,
                "net_exposure": 0.0,
                "gross_exposure": 0.0,
            })
            w_prev = pd.Series(dtype=float)
            continue

        w_exec = w_tgt.reindex(valid).fillna(0.0)
        if (w_exec != 0).sum() == 0:
            records.append({
                "date": t,
                "gross_return": 0.0,
                "cost": 0.0,
                "net_return": 0.0,
                "turnover": 0.0,
                "n_positions": 0,
                "n_long": 0,
                "n_short": 0,
                "net_exposure": 0.0,
                "gross_exposure": 0.0,
            })
            w_prev = pd.Series(dtype=float)
            continue

        traded = trade_notional(w_prev, w_exec)
        cost = cost_from_trade_notional(traded, total_cost_bps)
        turn = turnover_oneway(w_prev, w_exec)

        gross = float((w_exec * r.loc[valid]).sum())
        net = gross - cost

        net_exposure = float(w_exec.sum())
        gross_exposure = float(w_exec.abs().sum())
        n_long = int((w_exec > 0).sum())
        n_short = int((w_exec < 0).sum())

        records.append({
            "date": t,
            "gross_return": gross,
            "cost": cost,
            "net_return": net,
            "turnover": turn,
            "n_positions": int((w_exec != 0).sum()),
            "n_long": n_long,
            "n_short": n_short,
            "net_exposure": net_exposure,
            "gross_exposure": gross_exposure,
        })

        w_prev = w_exec

    out = pd.DataFrame(records).set_index("date").sort_index()
    return out
