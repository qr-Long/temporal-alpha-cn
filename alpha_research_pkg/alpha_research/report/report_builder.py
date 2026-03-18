from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

def _fmt(x, nd=4):
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)

def write_report_md(
    out_dir: str | Path,
    title: str,
    config: dict,
    perf: dict,
    ic: dict,
    rank_ic: dict,
    notes: list[str],
    tables: dict[str, pd.DataFrame] | None = None,
    plots: dict[str, str] | None = None,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"

    lines = []
    lines.append(f"# {title}\n")
    lines.append("## 关键结论\n")
    lines.append(f"- 年化收益: {_fmt(perf.get('ann_return'))}")
    lines.append(f"- 年化波动: {_fmt(perf.get('ann_vol'))}")
    lines.append(f"- Sharpe: {_fmt(perf.get('sharpe'), 3)}")
    lines.append(f"- 最大回撤: {_fmt(perf.get('max_dd'))}")
    lines.append("")
    lines.append("### IC（Pearson）")
    lines.append(f"- IC均值: {_fmt(ic.get('mean'))}")
    lines.append(f"- IC标准差: {_fmt(ic.get('std'))}")
    lines.append(f"- ICIR: {_fmt(ic.get('icir'), 3)}")
    lines.append(f"- 有效天数: {ic.get('n')}")
    lines.append("")
    lines.append("### RankIC（Spearman）")
    lines.append(f"- RankIC均值: {_fmt(rank_ic.get('mean'))}")
    lines.append(f"- RankIC标准差: {_fmt(rank_ic.get('std'))}")
    lines.append(f"- RankICIR: {_fmt(rank_ic.get('icir'), 3)}")
    lines.append(f"- 有效天数: {rank_ic.get('n')}")
    lines.append("")

    lines.append("## 重要口径（请在简历/面试里强调）\n")
    lines.append("- 股票池：沪深300（**最新成分**，存在 survivorship bias；用于一日项目快速闭环）")
    lines.append("- 执行：t 日收盘出信号，t+1 开盘成交；收益口径为 open_{t+1} -> open_{t+2}")
    lines.append("- 成本：按 traded_notional = sum(|Δw|) 计费；total_cost_bps=commission+slippage")
    lines.append("")

    if notes:
        lines.append("## 备注\n")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")

    if plots:
        lines.append("## 图表\n")
        for name, rel in plots.items():
            lines.append(f"### {name}\n")
            lines.append(f"![{name}]({rel})\n")

    (out_dir / "config_snapshot.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
