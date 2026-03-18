from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'website_data'


@st.cache_data
def load_manifest():
    return json.loads((DATA_DIR / 'manifest.json').read_text(encoding='utf-8'))


@st.cache_data
def load_factor_summaries() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / 'factor_summaries.csv')


@st.cache_data
def load_factor_detail(factor_id: str) -> dict:
    path = DATA_DIR / 'factors' / f'{factor_id}.json'
    return json.loads(path.read_text(encoding='utf-8'))


@st.cache_data
def load_compare_presets() -> list[dict]:
    return json.loads((DATA_DIR / 'compare_presets.json').read_text(encoding='utf-8'))


def data_path(relative_path: str | None):
    if not relative_path:
        return None
    return str((ROOT / relative_path).resolve())


def load_series_table(factor_id: str, table_name: str) -> pd.DataFrame | None:
    path = DATA_DIR / 'tables' / factor_id / table_name
    if not path.exists():
        return None
    return pd.read_csv(path)
