from __future__ import annotations

import time
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import pandas as pd
import akshare as ak

from .cache import load_cached, save_cached
from .universe import get_hs300_universe

# Standard internal columns we want downstream
KEEP_COLS = ["date", "asset", "open", "high", "low", "close", "volume", "amount", "turnover", "涨跌幅", "涨跌额", "振幅"]

def _to_keep_cols(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in KEEP_COLS if c in df.columns]
    return df[cols].copy()

def code_to_tx_symbol(code6: str) -> str:
    """Convert 6-digit A-share code into Tencent symbol with market prefix.

    Tencent expects e.g. 'sz000001', 'sh600000', 'bj430047'.
    Reference examples show symbol='sz000001'.

    """
    c = str(code6).zfill(6)
    if c.startswith(("60", "68", "69", "90")) or c[0] == "6":
        return "sh" + c
    if c.startswith(("00", "30")) or c[0] in ("0", "3"):
        return "sz" + c
    if c[0] in ("4", "8"):
        return "bj" + c
    # fallback
    return "sz" + c

@dataclass
class DataProviderConfig:
    adjust: str
    start_date: str
    end_date: str
    timeout_sec: int = 20
    throttle_sec: float = 0.50
    throttle_jitter_sec: float = 0.40
    max_retries: int = 3
    cache_dir: str = "outputs/cache"
    primary_source: str = "tx"   # tx (Tencent) | em (Eastmoney)

class AkshareDataProvider:
    """AkShare data provider (daily bars) with caching + throttling + retries.

    v4.2 default: use Tencent source stock_zh_a_hist_tx.
    Note: Tencent interface requires market-prefixed symbols (sz/sh/bj).
    """

    def __init__(self, cfg: DataProviderConfig, universe_symbol: str = "000300"):
        self.cfg = cfg
        self.universe_symbol = universe_symbol

    def get_universe(self) -> List[str]:
        return get_hs300_universe(self.universe_symbol)

    def _sleep(self, extra: float = 0.0):
        base = float(self.cfg.throttle_sec)
        jit = float(self.cfg.throttle_jitter_sec)
        time.sleep(max(0.0, base + random.random() * jit + extra))

    def _fetch_tx(self, code6: str) -> pd.DataFrame:
        """Tencent daily history via AkShare: stock_zh_a_hist_tx.

        Output columns from AkShare (per docs/examples): date, open, close, high, low, amount (unit: hands).
        We'll map amount -> volume for our internal use.
        """
        start = self.cfg.start_date.replace("-", "")
        end = self.cfg.end_date.replace("-", "")
        tx_symbol = code_to_tx_symbol(code6)
        df = ak.stock_zh_a_hist_tx(
            symbol=tx_symbol,
            start_date=start,
            end_date=end,
            adjust=self.cfg.adjust if self.cfg.adjust else "",
        )
        if df is None or len(df) == 0:
            raise RuntimeError(f"Empty TX data for {code6} ({tx_symbol})")
        # normalize
        df = df.copy()
        # ensure date column name
        if "date" not in df.columns:
            raise RuntimeError(f"Unexpected TX columns for {tx_symbol}: {list(df.columns)}")
        df = df.rename(columns={"amount": "volume"})  # amount is hands; treat as volume proxy
        df["asset"] = str(code6).zfill(6)
        # ensure canonical column names exist
        for c in ["open", "high", "low", "close", "volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])
        df = df.rename(columns={"date": "date"})
        return _to_keep_cols(df)

    def _fetch_em(self, code6: str) -> pd.DataFrame:
        """Eastmoney daily history via AkShare: stock_zh_a_hist."""
        start = self.cfg.start_date.replace("-", "")
        end = self.cfg.end_date.replace("-", "")
        df = ak.stock_zh_a_hist(
            symbol=str(code6).zfill(6),
            period="daily",
            start_date=start,
            end_date=end,
            adjust=self.cfg.adjust,
            timeout=int(self.cfg.timeout_sec),
        )
        if df is None or len(df) == 0:
            raise RuntimeError(f"Empty EM data for {code6}")
        # normalize Chinese headers -> canonical
        col_map = {
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "换手率": "turnover",
        }
        df = df.rename(columns=col_map).copy()
        df["asset"] = str(code6).zfill(6)
        df["date"] = pd.to_datetime(df["date"])
        for c in ["open", "high", "low", "close", "volume", "amount", "turnover"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return _to_keep_cols(df)

    def fetch_stock_hist(self, symbol: str, max_retries: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetch one stock daily history, with caching and retries."""
        code6 = str(symbol).zfill(6)

        cached = load_cached(self.cfg.cache_dir, code6, self.cfg.adjust)
        if cached is not None and len(cached) > 0:
            # cached 'date' might be string; normalize lazily downstream
            return cached

        retries = int(max_retries) if max_retries is not None else int(self.cfg.max_retries)
        last_err: Optional[Exception] = None

        for attempt in range(1, retries + 1):
            try:
                self._sleep()
                if str(self.cfg.primary_source).lower() == "tx":
                    df = self._fetch_tx(code6)
                else:
                    df = self._fetch_em(code6)

                # cache as csv (date as ISO string)
                df2 = df.copy()
                df2["date"] = df2["date"].dt.strftime("%Y-%m-%d")
                save_cached(self.cfg.cache_dir, code6, self.cfg.adjust, df2)
                return df2

            except Exception as e:
                last_err = e
                backoff = min(12.0, 0.8 * (2 ** (attempt - 1)) + random.random() * 0.8)
                print(f"[data][warn] fetch {code6} attempt {attempt}/{retries} failed: {repr(e)}; sleep {backoff:.1f}s")
                self._sleep(extra=backoff)

        print(f"[data][error] give up {code6}. last error: {repr(last_err)}")
        return None

    def build_prices_panel(
        self,
        universe: List[str] | None = None,
        max_assets: int | None = None,
        fail_fast_retries: int = 2,
    ) -> pd.DataFrame:
        """Return long-form panel with MultiIndex (date, asset). Skips failed symbols."""
        if universe is None:
            universe = self.get_universe()
        if max_assets is not None:
            universe = universe[: int(max_assets)]

        rows: list[pd.DataFrame] = []
        failed: list[str] = []
        total = len(universe)

        for i, sym in enumerate(universe, 1):
            df = self.fetch_stock_hist(sym, max_retries=fail_fast_retries)
            if df is None or len(df) == 0:
                failed.append(str(sym).zfill(6))
            else:
                rows.append(df)

            if i % 25 == 0 or i == total:
                print(f"[data] processed {i}/{total}; ok={len(rows)}; failed={len(failed)}")

        if len(rows) == 0:
            raise RuntimeError("All symbols failed to download. Check network and akshare availability.")

        all_df = pd.concat(rows, ignore_index=True)
        # normalize date and index
        all_df["date"] = pd.to_datetime(all_df["date"])
        all_df["asset"] = all_df["asset"].astype(str).str.zfill(6)
        panel = all_df.set_index(["date", "asset"]).sort_index()

        if failed:
            log_dir = Path("outputs/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "failed_symbols.txt").write_text("\n".join(failed), encoding="utf-8")
            print(f"[data][warn] {len(failed)} symbols failed; written to outputs/logs/failed_symbols.txt")

        return panel
