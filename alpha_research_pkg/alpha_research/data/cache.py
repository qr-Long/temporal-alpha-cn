from __future__ import annotations
from pathlib import Path
import pandas as pd

def cache_path(cache_dir: str | Path, symbol: str, adjust: str) -> Path:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    adj = adjust if adjust else "none"
    return cache_dir / f"{symbol}_{adj}.csv"

def load_cached(cache_dir: str | Path, symbol: str, adjust: str) -> pd.DataFrame | None:
    p = cache_path(cache_dir, symbol, adjust)
    if not p.exists():
        return None
    df = pd.read_csv(p)
    return df

def save_cached(cache_dir: str | Path, symbol: str, adjust: str, df: pd.DataFrame) -> None:
    p = cache_path(cache_dir, symbol, adjust)
    df.to_csv(p, index=False)
