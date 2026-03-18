"""你的特色因子模板

你只需要实现 compute_factor_panel(prices) -> DataFrame(index=date, columns=asset)。

- prices: MultiIndex (date, asset), columns 至少包含 open/high/low/close/volume/amount/turnover（按你需求使用）
- 返回：每个交易日的横截面因子值（用于排序）
"""
from __future__ import annotations
import pandas as pd

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    # 示例：用 20日波动率当因子（你要替换成自己的）
    close = prices["close"].unstack("asset").sort_index()
    ret = close.pct_change(1)
    vol20 = ret.rolling(20, min_periods=20).std()
    vol20.name = "user_factor"
    return vol20
