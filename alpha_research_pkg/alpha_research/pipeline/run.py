from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Callable
import pandas as pd

from alpha_research.config.loader import load_config
from alpha_research.data.provider import AkshareDataProvider, DataProviderConfig
from alpha_research.preprocess.clean import preprocess_factor_cs
from alpha_research.portfolio.constructor import build_weights_for_date
from alpha_research.execution.simulator import backtest_daily, compute_open_to_open_returns
from alpha_research.evaluation.factor_stats import ic_series, rank_ic_series, ic_summary, rank_ic_summary
from alpha_research.evaluation.perf_stats import perf_summary
from alpha_research.evaluation.plots import (
    plot_cost_sensitivity,
    plot_drawdown,
    plot_ic_distributions,
    plot_ic_series,
    plot_nav,
    plot_quantile_returns,
    plot_rank_ic,
    plot_turnover,
    plot_yearly_returns,
)
from alpha_research.report.report_builder import write_report_md

from alpha_research.factors.rev_5d import compute_factor_panel as fac_rev_5d
from alpha_research.factors.ma_golden_cross import compute_factor_panel as fac_mem_ma_gc
from alpha_research.factors.mom_20d import compute_factor_panel as fac_mom_20d
from alpha_research.factors.graph_mom20 import compute_factor_panel as fac_graph_mom20
from alpha_research.factors.uniq_knn import compute_factor_panel as fac_uniq_knn
from alpha_research.factors.mf_rev_pos_l06 import compute_factor_panel as fac_mf_rev_pos_l06
from alpha_research.factors.mf_rev_pos_l08 import compute_factor_panel as fac_mf_rev_pos_l08
from alpha_research.factors.mf_rev_pos_l09 import compute_factor_panel as fac_mf_rev_pos_l09
from alpha_research.factors.mf_rev_neg_l06 import compute_factor_panel as fac_mf_rev_neg_l06
from alpha_research.factors.mf_rev_neg_l08 import compute_factor_panel as fac_mf_rev_neg_l08
from alpha_research.factors.mf_rev_neg_l09 import compute_factor_panel as fac_mf_rev_neg_l09
from alpha_research.factors.mf_imp_rev_bg_t10 import compute_factor_panel as fac_mf_imp_rev_bg_t10
from alpha_research.factors.mf_imp_rev_bg_t10_vol import compute_factor_panel as fac_mf_imp_rev_bg_t10_vol
from alpha_research.factors.mf_imp_rev_bg_t15 import compute_factor_panel as fac_mf_imp_rev_bg_t15
from alpha_research.factors.mf_imp_rev_bg_t15_vol import compute_factor_panel as fac_mf_imp_rev_bg_t15_vol
from alpha_research.factors.mf_imp_rev_bg_t20 import compute_factor_panel as fac_mf_imp_rev_bg_t20
from alpha_research.factors.mf_imp_rev_bg_t20_vol import compute_factor_panel as fac_mf_imp_rev_bg_t20_vol
from alpha_research.factors.mf_imp_drift_bg_t10 import compute_factor_panel as fac_mf_imp_drift_bg_t10
from alpha_research.factors.mf_imp_drift_bg_t10_vol import compute_factor_panel as fac_mf_imp_drift_bg_t10_vol
from alpha_research.factors.mf_imp_drift_bg_t15 import compute_factor_panel as fac_mf_imp_drift_bg_t15
from alpha_research.factors.mf_imp_drift_bg_t15_vol import compute_factor_panel as fac_mf_imp_drift_bg_t15_vol
from alpha_research.factors.mf_imp_drift_bg_t20 import compute_factor_panel as fac_mf_imp_drift_bg_t20
from alpha_research.factors.mf_imp_drift_bg_t20_vol import compute_factor_panel as fac_mf_imp_drift_bg_t20_vol
from alpha_research.factors.mf_snr_rev_bg_med_s1 import compute_factor_panel as fac_mf_snr_rev_bg_med_s1
from alpha_research.factors.mf_snr_rev_bg_med_s3 import compute_factor_panel as fac_mf_snr_rev_bg_med_s3
from alpha_research.factors.mf_snr_rev_bg_med_s5 import compute_factor_panel as fac_mf_snr_rev_bg_med_s5
from alpha_research.factors.mf_snr_drift_bg_med_s1 import compute_factor_panel as fac_mf_snr_drift_bg_med_s1
from alpha_research.factors.mf_snr_drift_bg_med_s3 import compute_factor_panel as fac_mf_snr_drift_bg_med_s3
from alpha_research.factors.mf_snr_drift_bg_med_s5 import compute_factor_panel as fac_mf_snr_drift_bg_med_s5
from alpha_research.factors.sf_amp_tau5_s20 import compute_factor_panel as fac_sf_amp_tau5_s20
from alpha_research.factors.sf_amp_tau10_s20 import compute_factor_panel as fac_sf_amp_tau10_s20
from alpha_research.factors.sf_amp_tau20_s20 import compute_factor_panel as fac_sf_amp_tau20_s20
from alpha_research.factors.sf_slope_2_5_10_20_s60 import compute_factor_panel as fac_sf_slope_2_5_10_20_s60
from alpha_research.factors.sf_slope_5_10_20_40_s60 import compute_factor_panel as fac_sf_slope_5_10_20_40_s60
from alpha_research.factors.sf_amp_tau5_s20_localbg_knn10 import compute_factor_panel as fac_sf_amp_tau5_s20_localbg_knn10
from alpha_research.factors.sf_amp_tau5_s20_localsnr_knn10 import compute_factor_panel as fac_sf_amp_tau5_s20_localsnr_knn10
from alpha_research.factors.sf_amp_tau10_s20_localbg_knn10 import compute_factor_panel as fac_sf_amp_tau10_s20_localbg_knn10
from alpha_research.factors.sf_amp_tau10_s20_localsnr_knn10 import compute_factor_panel as fac_sf_amp_tau10_s20_localsnr_knn10

BUILTIN_FACTORS = {
    "rev_5d": fac_rev_5d,
    "mem_ma_gc": fac_mem_ma_gc,
    "mom_20d": fac_mom_20d,
    "graph_mom20": fac_graph_mom20,
    "uniq_knn": fac_uniq_knn,
"mf_rev_pos_l06": fac_mf_rev_pos_l06,
"mf_rev_pos_l08": fac_mf_rev_pos_l08,
"mf_rev_pos_l09": fac_mf_rev_pos_l09,
"mf_rev_neg_l06": fac_mf_rev_neg_l06,
"mf_rev_neg_l08": fac_mf_rev_neg_l08,
"mf_rev_neg_l09": fac_mf_rev_neg_l09,
            "mf_imp_rev_bg_t10": fac_mf_imp_rev_bg_t10,
            "mf_imp_rev_bg_t10_vol": fac_mf_imp_rev_bg_t10_vol,
            "mf_imp_rev_bg_t15": fac_mf_imp_rev_bg_t15,
            "mf_imp_rev_bg_t15_vol": fac_mf_imp_rev_bg_t15_vol,
            "mf_imp_rev_bg_t20": fac_mf_imp_rev_bg_t20,
            "mf_imp_rev_bg_t20_vol": fac_mf_imp_rev_bg_t20_vol,
            "mf_imp_drift_bg_t10": fac_mf_imp_drift_bg_t10,
            "mf_imp_drift_bg_t10_vol": fac_mf_imp_drift_bg_t10_vol,
            "mf_imp_drift_bg_t15": fac_mf_imp_drift_bg_t15,
            "mf_imp_drift_bg_t15_vol": fac_mf_imp_drift_bg_t15_vol,
            "mf_imp_drift_bg_t20": fac_mf_imp_drift_bg_t20,
            "mf_imp_drift_bg_t20_vol": fac_mf_imp_drift_bg_t20_vol,
            "mf_snr_rev_bg_med_s1": fac_mf_snr_rev_bg_med_s1,
            "mf_snr_rev_bg_med_s3": fac_mf_snr_rev_bg_med_s3,
            "mf_snr_rev_bg_med_s5": fac_mf_snr_rev_bg_med_s5,
            "mf_snr_drift_bg_med_s1": fac_mf_snr_drift_bg_med_s1,
            "mf_snr_drift_bg_med_s3": fac_mf_snr_drift_bg_med_s3,
            "mf_snr_drift_bg_med_s5": fac_mf_snr_drift_bg_med_s5,
            "sf_amp_tau5_s20": fac_sf_amp_tau5_s20,
            "sf_amp_tau10_s20": fac_sf_amp_tau10_s20,
            "sf_amp_tau20_s20": fac_sf_amp_tau20_s20,
            "sf_slope_2_5_10_20_s60": fac_sf_slope_2_5_10_20_s60,
            "sf_slope_5_10_20_40_s60": fac_sf_slope_5_10_20_40_s60,
    "sf_amp_tau5_s20_localbg_knn10": fac_sf_amp_tau5_s20_localbg_knn10,
    "sf_amp_tau5_s20_localsnr_knn10": fac_sf_amp_tau5_s20_localsnr_knn10,
    "sf_amp_tau10_s20_localbg_knn10": fac_sf_amp_tau10_s20_localbg_knn10,
    "sf_amp_tau10_s20_localsnr_knn10": fac_sf_amp_tau10_s20_localsnr_knn10,
}

def load_user_factor_module(path: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    p = Path(path)
    spec = importlib.util.spec_from_file_location("user_factor_module", str(p))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load user factor from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    if not hasattr(mod, "compute_factor_panel"):
        raise AttributeError("User factor module must define compute_factor_panel(prices) -> DataFrame")
    return getattr(mod, "compute_factor_panel")

def combine_factors_zscore(factors: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # expects already preprocessed (roughly z-scored). Simple sum.
    mats = list(factors.values())
    base = mats[0].copy()
    for m in mats[1:]:
        base = base.add(m, fill_value=0.0)
    return base

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=str, required=True)
    ap.add_argument("--factor", type=str, nargs="+", required=True, help="rev_5d mem_ma_gc user_factor ...")
    ap.add_argument("--user-factor", type=str, default=None, help="Path to a python file defining compute_factor_panel(prices)")
    ap.add_argument("--max-assets", type=int, default=None, help="For quick debug, limit number of stocks from HS300")
    args = ap.parse_args()

    cfg = load_config(args.config)

    out_dir = Path(cfg["report"]["output_dir"])
    plots_dir = out_dir / "plots"
    tables_dir = out_dir / "tables"
    plots_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    # data provider
    dc = cfg["data"]
    dcfg = DataProviderConfig(
        adjust=str(dc.get("adjust", "qfq")),
        start_date=str(dc["start_date"]),
        end_date=str(dc["end_date"]),
        timeout_sec=int(dc.get("timeout_sec", 20)),
        throttle_sec=float(dc.get("throttle_sec", 0.15)),
        throttle_jitter_sec=float(dc.get("throttle_jitter_sec", 0.10)),
        max_retries=int(dc.get("max_retries", 3)),
        cache_dir=str(dc.get("cache_dir", "outputs/cache")),
    )
    universe_symbol = str(cfg["universe"].get("csindex_symbol", "000300"))
    provider = AkshareDataProvider(dcfg, universe_symbol=universe_symbol)

    universe = provider.get_universe()
    if args.max_assets:
        universe = universe[: args.max_assets]

    print(f"[run] universe size: {len(universe)}")
    prices = provider.build_prices_panel(universe=universe, fail_fast_retries=2)
    print(f"[run] prices panel: {prices.index.get_level_values(0).nunique()} dates, {prices.index.get_level_values(1).nunique()} assets")

    # build factor panels
    factor_panels: Dict[str, pd.DataFrame] = {}

    user_factor_func = None
    if args.user_factor:
        user_factor_func = load_user_factor_module(args.user_factor)

    for name in args.factor:
        if name == "user_factor":
            if user_factor_func is None:
                raise ValueError("You specified user_factor but did not pass --user-factor path/to/file.py")
            fp = user_factor_func(prices)
            factor_panels[name] = fp
        elif name in BUILTIN_FACTORS:
            fp = BUILTIN_FACTORS[name](prices)
            factor_panels[name] = fp
        else:
            raise ValueError(f"Unknown factor: {name}. Built-ins: {list(BUILTIN_FACTORS.keys())} plus user_factor.")

    # preprocess each factor per date (winsorize + zscore)
    pcfg = cfg["preprocess"]
    win = pcfg["winsorize"]
    processed: Dict[str, pd.DataFrame] = {}
    for k, fp in factor_panels.items():
        fp = fp.loc[(fp.index >= pd.to_datetime(dcfg.start_date)) & (fp.index <= pd.to_datetime(dcfg.end_date))]
        fp2 = preprocess_factor_cs(
            fp,
            winsorize_method=str(win.get("method", "mad")),
            k=float(win.get("k", 5)),
            p_low=float(win.get("p_low", 0.01)),
            p_high=float(win.get("p_high", 0.99)),
            standardize=str(pcfg.get("standardize", "zscore")),
            fillna=str(pcfg.get("fillna", "drop")),
        )
        processed[k] = fp2

    # single-factor by default; if multiple, we also run combined
    runs: List[tuple[str, pd.DataFrame]] = []
    if len(processed) == 1:
        k = list(processed.keys())[0]
        runs.append((k, processed[k]))
    else:
        # run each single factor
        for k, fp in processed.items():
            runs.append((k, fp))
        # run combined simple sum (optional)
        combo = combine_factors_zscore(processed)
        runs.append(("combined_sum_z", combo))

    # Forward returns for IC (aligned to factor date t)
    fwd1 = compute_open_to_open_returns(prices)

    bcfg = cfg["backtest"]
    ccfg = cfg["costs"]
    total_cost_bps = float(ccfg.get("commission_bps", 2)) + float(ccfg.get("slippage_bps", 3))
    sens_costs = [float(x) for x in ccfg.get("sensitivity_total_cost_bps", [5, 10, 20])]

    notes = []

    for run_name, fac in runs:
        print(f"\n[run] ===== factor run: {run_name} =====")
        run_dir = out_dir / run_name
        run_plots_dir = run_dir / "plots"
        run_plots_dir.mkdir(parents=True, exist_ok=True)
        # Backtest at default cost
        pnl = backtest_daily(
            factor=fac,
            prices=prices,
            weight_func=build_weights_for_date,
            total_cost_bps=total_cost_bps,
            quantiles=int(bcfg.get("quantiles", 5)),
            long_short=bool(bcfg.get("long_short", True)),
            gross_leverage=float(bcfg.get("gross_leverage", 1.0)),
            weighting=str(bcfg.get("weighting", "equal")),
            max_weight_per_name=float(bcfg.get("max_weight_per_name", 0.02)) if bcfg.get("max_weight_per_name", None) is not None else None,
        )

        # IC
        ic = ic_series(fac, fwd1, min_obs=50)
        rank_ic = rank_ic_series(fac, fwd1, min_obs=50)
        ic_sum = ic_summary(ic)
        rank_ic_sum = rank_ic_summary(rank_ic)
        perf = perf_summary(pnl["net_return"])

        # Save tables
        pnl.to_csv(tables_dir / f"pnl_{run_name}.csv")
        ic.to_csv(tables_dir / f"ic_{run_name}.csv")
        rank_ic.to_csv(tables_dir / f"rankic_{run_name}.csv")

        # Plots
        plot_paths = {}

        # Cost sensitivity: re-run pnl with different total cost (fast, no re-download)
        sens_rows = []
        for c in sens_costs:
            pnl_c = backtest_daily(
                factor=fac,
                prices=prices,
                weight_func=build_weights_for_date,
                total_cost_bps=float(c),
                quantiles=int(bcfg.get("quantiles", 5)),
                long_short=bool(bcfg.get("long_short", True)),
                gross_leverage=float(bcfg.get("gross_leverage", 1.0)),
                weighting=str(bcfg.get("weighting", "equal")),
                max_weight_per_name=float(bcfg.get("max_weight_per_name", 0.02)) if bcfg.get("max_weight_per_name", None) is not None else None,
            )
            ps = perf_summary(pnl_c["net_return"])
            sens_rows.append({"total_cost_bps": c, **ps})
        sens_df = pd.DataFrame(sens_rows)
        sens_df.to_csv(tables_dir / f"cost_sensitivity_{run_name}.csv", index=False)

        if cfg["report"].get("make_plots", True):
            nav_path = run_plots_dir / f"nav_{run_name}.png"
            dd_path = run_plots_dir / f"drawdown_{run_name}.png"
            ic_path = run_plots_dir / f"ic_{run_name}.png"
            rankic_path = run_plots_dir / f"rankic_{run_name}.png"
            to_path = run_plots_dir / f"turnover_{run_name}.png"
            yearly_path = run_plots_dir / f"yearly_return_{run_name}.png"
            cost_path = run_plots_dir / f"cost_sensitivity_{run_name}.png"
            dist_path = run_plots_dir / f"ic_rankic_dist_{run_name}.png"
            quantile_path = run_plots_dir / f"quantile_return_{run_name}.png"

            plot_nav(pnl["net_return"], nav_path, f"NAV (net) - {run_name}")
            plot_drawdown(pnl["net_return"], dd_path, f"Drawdown - {run_name}")
            plot_ic_series(ic, ic_path, f"IC - {run_name}", "IC (Pearson)")
            plot_rank_ic(rank_ic, rankic_path, f"RankIC - {run_name}")
            plot_turnover(pnl["turnover"], to_path, f"Turnover - {run_name}")
            plot_yearly_returns(pnl["net_return"], yearly_path, f"Yearly Net Return - {run_name}")
            plot_cost_sensitivity(sens_df, cost_path, f"Cost Sensitivity - {run_name}")
            plot_ic_distributions(ic, rank_ic, dist_path, f"IC / RankIC Distribution - {run_name}")
            plot_quantile_returns(
                factor=fac,
                fwd_ret=fwd1,
                outpath=quantile_path,
                title=f"Quantile Forward Returns - {run_name}",
                quantiles=int(bcfg.get("quantiles", 5)),
                min_obs=20,
            )

            plot_paths = {
                "净值曲线（net）": f"plots/{nav_path.name}",
                "回撤曲线": f"plots/{dd_path.name}",
                "IC 时间序列": f"plots/{ic_path.name}",
                "RankIC 时间序列": f"plots/{rankic_path.name}",
                "换手（单边）": f"plots/{to_path.name}",
                "年度收益柱状图": f"plots/{yearly_path.name}",
                "成本敏感性": f"plots/{cost_path.name}",
                "IC / RankIC 分布": f"plots/{dist_path.name}",
                "分组收益": f"plots/{quantile_path.name}",
            }

        notes2 = notes + [
            f"默认成本 total_cost_bps={total_cost_bps}（commission+slippage）",
            "股票池为沪深300最新成分（存在 survivorship bias）",
            "日频：t 收盘出信号，t+1 开盘成交；收益：open_{t+1} -> open_{t+2}",
        ]

        if cfg["report"].get("make_report_md", True):
            title = f"Factor Backtest Report - {run_name}"
            write_report_md(
                out_dir=out_dir / run_name,
                title=title,
                config=cfg,
                perf=perf,
                ic=ic_sum,
                rank_ic=rank_ic_sum,
                notes=notes2,
                plots=plot_paths,
            )
            # also dump sensitivity
            (out_dir / run_name / "tables").mkdir(parents=True, exist_ok=True)
            sens_df.to_csv(out_dir / run_name / "tables" / "cost_sensitivity.csv", index=False)
            pnl.to_csv(out_dir / run_name / "tables" / "pnl.csv")
            ic.to_csv(out_dir / run_name / "tables" / "ic.csv")
            rank_ic.to_csv(out_dir / run_name / "tables" / "rank_ic.csv")

        print(f"[run] perf: {perf}")
        print(f"[run] ic: {ic_sum}")
        print(f"[run] rank_ic: {rank_ic_sum}")

    print(f"\n[done] outputs written to: {out_dir.resolve()}")

if __name__ == "__main__":
    main()
