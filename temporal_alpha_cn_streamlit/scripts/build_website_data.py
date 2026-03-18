from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'website_data'
MAPPING = {
    'sf_amp_tau5_s20': 'sf_amp_tau5_s20',
    'sf_amp_tau10_s20': 'sf_amp_tau10_s20',
    'sf_amp_tau20_s20': 'sf_amp_tau20_s20',
    'uniq_knn': 'uniq_knn',
    'mom_20d': 'mom_20d',
    'rev_5d': 'rev_5d',
    'ma_golden_cross': 'mem_ma_gc',
}
PLOT_CANON = {
    'nav': 'nav.png', 'drawdown': 'drawdown.png', 'ic_ts': 'ic_ts.png', 'rankic_ts': 'rankic_ts.png', 'turnover': 'turnover.png', 'yearly_return': 'yearly_return.png', 'cost_sensitivity': 'cost_sensitivity.png', 'ic_rankic_dist': 'ic_rankic_dist.png', 'quantile_return': 'quantile_return.png',
}
PLOT_PREFIX = {
    'nav': 'nav_', 'drawdown': 'drawdown_', 'ic_ts': 'ic_', 'rankic_ts': 'rankic_', 'turnover': 'turnover_', 'yearly_return': 'yearly_return_', 'cost_sensitivity': 'cost_sensitivity_', 'ic_rankic_dist': 'ic_rankic_dist_', 'quantile_return': 'quantile_return_',
}

def safe_float(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None

def compute_metrics(factor_dir: Path):
    ic = pd.read_csv(factor_dir / 'tables' / 'ic.csv')
    rk = pd.read_csv(factor_dir / 'tables' / 'rank_ic.csv')
    pnl = pd.read_csv(factor_dir / 'tables' / 'pnl.csv')
    cost = pd.read_csv(factor_dir / 'tables' / 'cost_sensitivity.csv').sort_values('total_cost_bps').iloc[0]
    ic_s = pd.to_numeric(ic['ic'], errors='coerce').dropna()
    rk_s = pd.to_numeric(rk['rank_ic'], errors='coerce').dropna()
    r = pd.to_numeric(pnl['net_return'], errors='coerce').fillna(0)
    return {
        'ic_mean': safe_float(ic_s.mean()),
        'rankic_mean': safe_float(rk_s.mean()),
        'annual_return': safe_float(cost['ann_return']),
        'sharpe': safe_float(cost['sharpe']),
        'max_drawdown': safe_float(cost['max_dd']),
        'icir': safe_float(ic_s.mean() / ic_s.std()) if len(ic_s) > 1 and float(ic_s.std()) != 0 else None,
        'rankicir': safe_float(rk_s.mean() / rk_s.std()) if len(rk_s) > 1 and float(rk_s.std()) != 0 else None,
        'avg_turnover': safe_float(pd.to_numeric(pnl['turnover'], errors='coerce').dropna().mean()),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outputs', required=True)
    args = parser.parse_args()
    outputs = Path(args.outputs)
    rows = []
    for fid, src_name in MAPPING.items():
        src_dir = outputs / src_name
        if not src_dir.exists():
            continue
        plots_dst = DATA_DIR / 'plots' / fid
        tables_dst = DATA_DIR / 'tables' / fid
        plots_dst.mkdir(parents=True, exist_ok=True)
        tables_dst.mkdir(parents=True, exist_ok=True)
        for kind, filename in PLOT_CANON.items():
            src = src_dir / 'plots' / f'{PLOT_PREFIX[kind]}{src_name}.png'
            if src.exists():
                shutil.copy2(src, plots_dst / filename)
        for name in ['pnl.csv', 'ic.csv', 'rank_ic.csv', 'cost_sensitivity.csv']:
            src = src_dir / 'tables' / name
            if src.exists():
                shutil.copy2(src, tables_dst / name)
        detail_path = DATA_DIR / 'factors' / f'{fid}.json'
        if not detail_path.exists():
            continue
        detail = json.loads(detail_path.read_text(encoding='utf-8'))
        detail['metrics'] = compute_metrics(src_dir)
        detail['plots'] = {k: f'website_data/plots/{fid}/{v}' for k, v in PLOT_CANON.items()}
        detail['preview_plot'] = detail['plots']['nav']
        detail['detail_ready'] = True
        if fid == 'mom_20d':
            pnl = pd.read_csv(src_dir/'tables'/'pnl.csv')
            pnl['date'] = pd.to_datetime(pnl['date'])
            raw_r = pd.to_numeric(pnl['net_return'], errors='coerce').fillna(0)
            sign_r = -raw_r
            raw_nav = (1+raw_r).cumprod()
            sign_nav = (1+sign_r).cumprod()
            plt.figure(figsize=(10,5))
            plt.plot(pnl['date'], raw_nav, label='Raw 20-day momentum', linewidth=2)
            plt.plot(pnl['date'], sign_nav, label='Sign-checked (flipped) direction', linewidth=2)
            plt.title('20-day momentum sign-check diagnostic')
            plt.xlabel('Date'); plt.ylabel('NAV'); plt.legend(); plt.tight_layout()
            plt.savefig(plots_dst/'sign_check_nav.png', dpi=180); plt.close()
            detail['diagnostics']['plot'] = f'website_data/plots/{fid}/sign_check_nav.png'
        detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding='utf-8')
        rows.append({
            'factor_id': fid, 'factor_name_en': detail['factor_name_en'], 'factor_name_zh': detail['factor_name_zh'], 'family': detail['family'], 'status': detail['status'], 'short_desc_en': detail['short_desc_en'], 'short_desc_zh': detail['short_desc_zh'], 'annual_return': detail['metrics'].get('annual_return'), 'sharpe': detail['metrics'].get('sharpe'), 'ic_mean': detail['metrics'].get('ic_mean'), 'rankic_mean': detail['metrics'].get('rankic_mean'), 'max_drawdown': detail['metrics'].get('max_drawdown'), 'avg_turnover': detail['metrics'].get('avg_turnover'), 'detail_ready': True, 'preview_plot': detail['preview_plot']
        })
    if rows:
        pd.DataFrame(rows).to_csv(DATA_DIR / 'factor_summaries.csv', index=False)
    print('[OK] website_data rebuilt for selected factors')

if __name__ == '__main__':
    main()
