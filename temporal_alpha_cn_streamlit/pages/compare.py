import streamlit as st
import pandas as pd
from components.compare_toolbar import render_compare_toolbar
from components.footer import render_footer
from utils.data_loader import load_factor_summaries, load_compare_presets, load_series_table
from utils.i18n import t
from utils.state import add_to_compare
from utils.formatters import fmt_metric

summary_df = load_factor_summaries().set_index('factor_id')
st.title(t('compare_title'))

with st.sidebar:
    render_compare_toolbar(st.session_state.get('compare_list', []))
    st.markdown(f"### {t('compare_pick_more')}")
    selectable = [fid for fid in summary_df.index if fid not in st.session_state.get('compare_list', [])]
    pick = st.selectbox(t('compare_pick_more'), [''] + selectable)
    if st.button(t('compare_add_button'), use_container_width=True, disabled=(pick == '')):
        add_to_compare(pick)
        st.rerun()
    st.markdown(f"### {t('compare_presets')}")
    for idx, preset in enumerate(load_compare_presets()):
        label = preset['label_zh'] if st.session_state.get('lang', 'zh') == 'zh' else preset['label_en']
        if st.button(label, key=f'preset_{idx}', use_container_width=True):
            st.session_state['compare_list'] = preset['factors'][:4]
            st.rerun()

compare_ids = st.session_state.get('compare_list', [])
if not compare_ids:
    st.info(t('compare_empty'))
    render_footer()
    st.stop()

rows = []
for fid in compare_ids:
    row = summary_df.loc[fid].to_dict()
    row['factor_id'] = fid
    rows.append(row)
metrics_df = pd.DataFrame(rows)[['factor_id', 'ic_mean', 'rankic_mean', 'annual_return', 'sharpe', 'max_drawdown', 'avg_turnover']]
st.dataframe(metrics_df, use_container_width=True)

def build_nav_frame(fids):
    out = pd.DataFrame()
    for fid in fids:
        pnl = load_series_table(fid, 'pnl.csv')
        if pnl is None:
            continue
        pnl['date'] = pd.to_datetime(pnl['date'])
        out[fid] = (1 + pd.to_numeric(pnl['net_return'], errors='coerce').fillna(0)).cumprod().values
        out.index = pnl['date']
    return out

def build_drawdown_frame(fids):
    out = pd.DataFrame()
    for fid in fids:
        pnl = load_series_table(fid, 'pnl.csv')
        if pnl is None:
            continue
        pnl['date'] = pd.to_datetime(pnl['date'])
        nav = (1 + pd.to_numeric(pnl['net_return'], errors='coerce').fillna(0)).cumprod()
        dd = nav / nav.cummax() - 1
        out[fid] = dd.values
        out.index = pnl['date']
    return out

def build_rankic_frame(fids):
    out = pd.DataFrame()
    for fid in fids:
        df = load_series_table(fid, 'rank_ic.csv')
        if df is None:
            continue
        df['date'] = pd.to_datetime(df['date'])
        out[fid] = pd.to_numeric(df['rank_ic'], errors='coerce').values
        out.index = df['date']
    return out

def build_cost_frame(fids):
    frames = []
    for fid in fids:
        df = load_series_table(fid, 'cost_sensitivity.csv')
        if df is None:
            continue
        tmp = df[['total_cost_bps', 'ann_return']].copy()
        tmp = tmp.rename(columns={'ann_return': fid})
        frames.append(tmp.set_index('total_cost_bps'))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, axis=1)
    out.index.name = 'total_cost_bps'
    return out

for title, frame in [
    ('NAV', build_nav_frame(compare_ids)),
    ('Drawdown', build_drawdown_frame(compare_ids)),
    ('RankIC', build_rankic_frame(compare_ids)),
    ('Cost Sensitivity (Annual Return)', build_cost_frame(compare_ids)),
]:
    st.markdown(f'## {title}')
    if frame.empty:
        st.info('No data available.')
    else:
        if title.startswith('Cost'):
            st.line_chart(frame)
        else:
            st.line_chart(frame)

render_footer()
