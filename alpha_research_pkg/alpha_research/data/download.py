from __future__ import annotations

import argparse
from pathlib import Path

from alpha_research.config.loader import load_config
from alpha_research.data.provider import AkshareDataProvider, DataProviderConfig

def main():
    ap = argparse.ArgumentParser(description="Download/cache HS300 daily data to local disk with resume.")
    ap.add_argument("--config", required=True, type=str)
    ap.add_argument("--max-assets", type=int, default=None)
    ap.add_argument("--retries", type=int, default=8, help="Max retries per symbol during downloader (strong).")
    args = ap.parse_args()

    cfg = load_config(args.config)
    dc = cfg["data"]
    dcfg = DataProviderConfig(
        adjust=str(dc.get("adjust", "qfq")),
        start_date=str(dc["start_date"]),
        end_date=str(dc["end_date"]),
        timeout_sec=int(dc.get("timeout_sec", 20)),
        throttle_sec=float(dc.get("throttle_sec", 0.80)),
        throttle_jitter_sec=float(dc.get("throttle_jitter_sec", 0.60)),
        max_retries=int(args.retries),
        cache_dir=str(dc.get("cache_dir", "outputs/cache")),
        primary_source="tx",
    )
    universe_symbol = str(cfg["universe"].get("csindex_symbol", "000300"))
    provider = AkshareDataProvider(dcfg, universe_symbol=universe_symbol)

    universe = provider.get_universe()
    if args.max_assets:
        universe = universe[: args.max_assets]

    ok, failed = 0, 0
    fail_list = []
    for i, sym in enumerate(universe, 1):
        df = provider.fetch_stock_hist(sym, max_retries=dcfg.max_retries)
        if df is None or len(df) == 0:
            failed += 1
            fail_list.append(str(sym).zfill(6))
        else:
            ok += 1
        if i % 25 == 0 or i == len(universe):
            print(f"[download] processed {i}/{len(universe)}; ok={ok}; failed={failed}")

    if fail_list:
        log_dir = Path("outputs/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "failed_symbols_download.txt").write_text("\n".join(fail_list), encoding="utf-8")
        print("[download][warn] failures written to outputs/logs/failed_symbols_download.txt")

    print(f"[download][done] cache dir: {dcfg.cache_dir}")

if __name__ == "__main__":
    main()
