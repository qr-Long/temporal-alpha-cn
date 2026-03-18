from __future__ import annotations
import pandas as pd

def require_columns(panel: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing required columns in prices panel: {missing}")
