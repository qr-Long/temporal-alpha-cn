import streamlit as st
from components.factor_card import render_factor_card
from components.footer import render_footer
from utils.data_loader import load_factor_summaries, load_manifest
from utils.filters import apply_factor_filters
from utils.i18n import t
from components.language_switcher import render_language_switcher

manifest = load_manifest()
df = load_factor_summaries()

st.title(t('factors_title'))

with st.sidebar:
    render_language_switcher(sidebar=True)
    search_text = st.text_input(t('search_label'), value=st.session_state.get('search_text', ''))
    families = st.multiselect(t('family_filter'), manifest['families'], default=st.session_state.get('family_filter', []))
    statuses = st.multiselect(t('status_filter'), manifest['statuses'], default=st.session_state.get('status_filter', []))
    sort_by = st.selectbox(t('sort_by'), ['sharpe', 'annual_return', 'rankic_mean', 'ic_mean', 'max_drawdown', 'avg_turnover'])
    ready_only = st.toggle(t('ready_only'), value=st.session_state.get('detail_ready_only', False))
    st.session_state['search_text'] = search_text
    st.session_state['family_filter'] = families
    st.session_state['status_filter'] = statuses
    st.session_state['sort_by'] = sort_by
    st.session_state['detail_ready_only'] = ready_only

filtered = apply_factor_filters(df, search_text, families, statuses, ready_only, sort_by)
if filtered.empty:
    st.info(t('no_factors'))
else:
    cols_per_row = 2
    for i in range(0, len(filtered), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j, (_, row) in enumerate(filtered.iloc[i:i+cols_per_row].iterrows()):
            with row_cols[j]:
                render_factor_card(row.to_dict(), key_prefix=f'factors_{i}_{j}')

render_footer()
