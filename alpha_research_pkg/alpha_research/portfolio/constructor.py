from __future__ import annotations

import numpy as np
import pandas as pd


def build_weights_for_date(
    factor_row: pd.Series,
    quantiles: int = 5,
    long_short: bool = True,
    gross_leverage: float = 1.0,
    weighting: str = "equal",
    max_weight_per_name: float | None = 0.02,
) -> pd.Series:
    """Given a cross-section factor row (indexed by asset), output target weights for next open.
    NaNs are ignored.

    long_short:
      - if True: long top quantile, short bottom quantile, net ~0, gross ~gross_leverage
      - if False: long top quantile only, net=1
    """
    s = factor_row.dropna().astype(float)
    if len(s) == 0:
        return pd.Series(dtype=float)

    # Use qcut on ranks to guarantee both bottom and top bins exist.
    bins = pd.qcut(s.rank(method="first"), q=quantiles, labels=False, duplicates="drop")
    longs = s.index[bins == bins.max()]
    shorts = s.index[bins == bins.min()]

    w = pd.Series(0.0, index=s.index)

    if long_short:
        if len(longs) == 0 or len(shorts) == 0:
            return pd.Series(dtype=float)
        long_gross = gross_leverage / 2.0
        short_gross = gross_leverage / 2.0

        w.loc[longs] = long_gross / len(longs)
        w.loc[shorts] = -short_gross / len(shorts)
    else:
        if len(longs) == 0:
            return pd.Series(dtype=float)
        w.loc[longs] = 1.0 / len(longs)

    # apply max weight cap if set
    if max_weight_per_name is not None:
        cap = float(max_weight_per_name)
        w = w.clip(lower=-cap, upper=cap)

        # renormalize to keep gross/net roughly
        if long_short:
            pos = w[w > 0]
            neg = w[w < 0]
            if len(pos) and pos.sum() != 0:
                w.loc[pos.index] = pos / pos.sum() * (gross_leverage / 2.0)
            if len(neg) and neg.abs().sum() != 0:
                # IMPORTANT: neg is already negative -> this stays negative
                w.loc[neg.index] = neg / neg.abs().sum() * (gross_leverage / 2.0)
        else:
            pos = w[w > 0]
            if len(pos) and pos.sum() != 0:
                w.loc[pos.index] = pos / pos.sum()

    return w
