# Astronomy-Inspired Alpha Research

This repo is a small research project on daily cross-sectional alpha factors for the CSI 300 universe.

The main idea is simple: I tried to bring some time-domain astronomy intuition into factor research, especially the **Structure Function (SF)** idea for measuring short-horizon variability. I also tested a few other directions along the way (matched filter style signals, SF shape/asymmetry, local background adjustment, KNN-based local significance), but the most useful signal in this project ended up being the plain short-horizon SF amplitude factor.

## What this project does

- builds a lightweight daily backtest pipeline for A-shares
- uses **t close -> t+1 open** execution logic
- evaluates factors with:
  - annual return
  - volatility
  - Sharpe
  - max drawdown
  - IC (Pearson)
  - RankIC (Spearman)
  - turnover
  - cost sensitivity

## Main result

The best factor in this repo is a short-horizon Structure Function variability factor:

- research name: **Short-Horizon Structure Function Variability**
- implementation name: `sf_amp_tau5_s20`

On the CSI 300 universe, in a daily market-neutral long-short setup, it achieved roughly:

- **Annual return:** 18.1%
- **Sharpe:** 1.20
- **Max drawdown:** -17.7%

A nearby variant, `sf_amp_tau10_s20`, also worked reasonably well and was used as a robustness check.

## Why the astronomy angle matters

In time-domain astronomy, Structure Functions are often used to describe variability across different time lags. I used the same idea on stock return series to measure short-term structured variability, instead of using a standard momentum or volatility definition directly.

A lot of the more "astronomy-heavy" ideas I tried were interesting but not always useful in backtests. That was part of the point of this project too: not just to find a good factor, but to test which scientific intuitions actually survive trading constraints.

## Data and setup

- universe: **CSI 300**
- frequency: **daily**
- signal time: **t close**
- execution time: **t+1 open**
- holding period: **open-to-open, 1 day**
- default data source: **AkShare / Tencent daily history interface**

## Install

```bash
pip install -r requirements.txt
```

## Run examples

Run the main SF factors:

```bash
python -m alpha_research.pipeline.run --config alpha_research/config/default.yaml --factor sf_amp_tau5_s20
python -m alpha_research.pipeline.run --config alpha_research/config/default.yaml --factor sf_amp_tau10_s20
```

Run a baseline factor:

```bash
python -m alpha_research.pipeline.run --config alpha_research/config/default.yaml --factor rev_5d
```

Run multiple factors together:

```bash
python -m alpha_research.pipeline.run --config alpha_research/config/default.yaml --factor rev_5d sf_amp_tau5_s20
```

## Output

By default, results are written to:

```text
outputs/exp_001/
```

Typical outputs include:

- `report.md`
- `tables/`
- `plots/`
- `cache/`

## Notes

- The CSI 300 membership is based on the latest constituent list, so there is **survivorship bias**.
- This project is meant for fast factor research and presentation, not for production trading.
- Some factor ideas in the repo are negative results. I kept them because they are part of the research process.

## Repo structure

```text
alpha_research/
├── config/
├── data/
├── evaluation/
├── execution/
├── factors/
├── pipeline/
├── portfolio/
├── preprocess/
└── report/
```

## Personal note

I built this project as a way to connect my own background in astronomy / physics / machine learning with quantitative research. The code is intentionally lightweight, but the goal was to keep the research logic clear and reproducible.
