from __future__ import annotations

from pathlib import Path
import pandas as pd
import akshare as ak

OFFLINE_UNIVERSE_TXT = Path("outputs/cache/hs300_universe.txt")
OFFLINE_UNIVERSE_CSV = Path("outputs/cache/hs300_universe.csv")

def _load_offline_universe() -> list[str] | None:
    """Load HS300 universe from local cache if present.

    This avoids network calls to csindex (which may be blocked by proxy/network).
    Accepted formats:
      - outputs/cache/hs300_universe.txt : one 6-digit code per line
      - outputs/cache/hs300_universe.csv : a column named '成分券代码' or 'code'
    """
    if OFFLINE_UNIVERSE_TXT.exists():
        codes = [ln.strip() for ln in OFFLINE_UNIVERSE_TXT.read_text(encoding="utf-8").splitlines() if ln.strip()]
        codes = [c.zfill(6) for c in codes]
        return sorted(list(dict.fromkeys(codes)))
    if OFFLINE_UNIVERSE_CSV.exists():
        df = pd.read_csv(OFFLINE_UNIVERSE_CSV)
        col = "成分券代码" if "成分券代码" in df.columns else ("code" if "code" in df.columns else None)
        if col is None:
            return None
        codes = df[col].astype(str).str.zfill(6).tolist()
        return sorted(list(dict.fromkeys(codes)))
    return None

def get_hs300_constituents(csindex_symbol: str = "000300") -> pd.DataFrame:
    """Return latest HS300 constituents from csindex via AkShare.

    If offline universe file exists, return a minimal DataFrame constructed from it.
    """
    offline = _load_offline_universe()
    if offline is not None and len(offline) > 0:
        return pd.DataFrame({"成分券代码": offline})

    df = ak.index_stock_cons_csindex(symbol=csindex_symbol)
    df["成分券代码"] = df["成分券代码"].astype(str).str.zfill(6)
    return df

def get_hs300_universe(csindex_symbol: str = "000300") -> list[str]:
    df = get_hs300_constituents(csindex_symbol)
    return df["成分券代码"].astype(str).tolist()
