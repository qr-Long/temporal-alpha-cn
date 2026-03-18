# Temporal Alpha CN

A Streamlit showcase for astronomy-inspired equity alpha research.

## Included factors
- Representative: `sf_amp_tau5_s20`, `sf_amp_tau10_s20`
- Additional selected factors: `sf_amp_tau20_s20`, `uniq_knn`
- Baselines: `mom_20d`, `rev_5d`, `ma_golden_cross`

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Refresh website data from a new output directory
```bash
python scripts/build_website_data.py --outputs /path/to/exp_001
```
