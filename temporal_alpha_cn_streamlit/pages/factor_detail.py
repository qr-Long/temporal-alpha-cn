import streamlit as st
import pandas as pd
from components.footer import render_footer
from components.metric_grid import render_metric_grid
from components.plot_panel import render_plot
from components.factor_card import render_factor_card
from utils.data_loader import load_factor_detail, data_path, load_factor_summaries
from utils.i18n import t, pick_text
from utils.state import add_to_compare, set_selected_factor
from utils.constants import PLOT_LABELS
from utils.formatters import fmt_metric

factor_id = st.session_state.get('selected_factor', 'sf_amp_tau5_s20')
try:
    detail = load_factor_detail(factor_id)
except FileNotFoundError:
    factor_id = 'sf_amp_tau5_s20'
    set_selected_factor(factor_id)
    detail = load_factor_detail(factor_id)
metrics = detail.get('metrics', {})

st.title(t('factor_detail'))
head1, head2 = st.columns([5, 2])
with head1:
    st.markdown(f"# {pick_text(detail['factor_name_zh'], detail['factor_name_en'])}")
    st.caption(f"{detail['family']} · {detail['status']}")
    st.write(pick_text(detail['short_desc_zh'], detail['short_desc_en']))
    st.caption(f"{t('implementation_label')}: {detail['factor_id']}")
with head2:
    if st.button(t('compare_add_button'), use_container_width=True):
        add_to_compare(factor_id)
        st.toast(t('added_to_compare'))
    if st.button(t('back_to_factors'), use_container_width=True):
        st.switch_page('pages/factors.py')

render_metric_grid(metrics)

st.markdown(f"## {t('motivation')}")
st.markdown(pick_text(detail['description'].get('motivation_zh'), detail['description'].get('motivation_en')))
st.markdown(f"## {t('construction')}")
st.markdown(pick_text(detail['description'].get('construction_zh'), detail['description'].get('construction_en')))
st.markdown(f"## {t('interpretation')}")
st.markdown(pick_text(detail['description'].get('interpretation_zh'), detail['description'].get('interpretation_en')))

plot_order = ['nav', 'drawdown', 'ic_ts', 'rankic_ts', 'turnover', 'yearly_return', 'cost_sensitivity']
for idx in range(0, len(plot_order), 2):
    cols = st.columns(2)
    for col, key in zip(cols, plot_order[idx:idx+2]):
        with col:
            render_plot(PLOT_LABELS[key][st.session_state.get('lang', 'zh')], data_path(detail['plots'].get(key)))
with st.expander(t('more_analysis')):
    cols = st.columns(2)
    for col, key in zip(cols, ['ic_rankic_dist', 'quantile_return']):
        with col:
            render_plot(PLOT_LABELS[key][st.session_state.get('lang', 'zh')], data_path(detail['plots'].get(key)))

if detail.get('diagnostics'):
    diag = detail['diagnostics']
    st.markdown(f"## {pick_text(diag.get('title_zh'), diag.get('title_en'))}")
    st.write(pick_text(diag.get('body_zh'), diag.get('body_en')))
    c1, c2 = st.columns([3, 2])
    with c1:
        render_plot(pick_text('方向检查净值对比', 'Sign-check NAV comparison'), data_path(diag.get('plot')))
    with c2:
        dmetrics = diag.get('metrics', {})
        table = pd.DataFrame([
            {'Profile': pick_text('原始 20 日动量', 'Raw 20-day momentum'), 'Annual Return': fmt_metric(dmetrics.get('raw_annual_return'), pct=True), 'Sharpe': fmt_metric(dmetrics.get('raw_sharpe'), digits=3), 'Max Drawdown': fmt_metric(dmetrics.get('raw_max_drawdown'), pct=True), 'IC Mean': fmt_metric(dmetrics.get('raw_ic_mean'), digits=4)},
            {'Profile': pick_text('方向检查后（翻转）', 'Sign-checked (flipped)'), 'Annual Return': fmt_metric(dmetrics.get('sign_checked_annual_return'), pct=True), 'Sharpe': fmt_metric(dmetrics.get('sign_checked_sharpe'), digits=3), 'Max Drawdown': fmt_metric(dmetrics.get('sign_checked_max_drawdown'), pct=True), 'IC Mean': fmt_metric(dmetrics.get('sign_checked_ic_mean'), digits=4)},
        ])
        st.dataframe(table, use_container_width=True, hide_index=True)

st.markdown(f"## {t('analysis_note')}")
st.markdown(pick_text(detail.get('analysis_note_zh'), detail.get('analysis_note_en')))

st.markdown(f"## {t('related_factors')}")
summary_df = load_factor_summaries().set_index('factor_id')
related = [fid for fid in detail.get('related_factors', []) if fid in summary_df.index]
if related:
    cols = st.columns(min(3, len(related)))
    for col, fid in zip(cols, related):
        with col:
            row_dict = summary_df.loc[fid].to_dict()
            row_dict['factor_id'] = fid
            render_factor_card(row_dict, key_prefix=f'related_{fid}')

render_footer()
