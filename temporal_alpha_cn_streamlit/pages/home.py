import streamlit as st
from components.footer import render_footer
from utils.data_loader import load_manifest, load_factor_detail, load_factor_summaries, data_path
from utils.i18n import t, pick_text
from utils.state import set_selected_factor, add_to_compare
from utils.formatters import fmt_metric

manifest = load_manifest()
summaries = load_factor_summaries()
rep_ids = manifest['representative_factors']
rep_details = [load_factor_detail(fid) for fid in rep_ids]
selected_ids = manifest.get('selected_extension_factors', [])
selected_details = [load_factor_detail(fid) for fid in selected_ids]


def _jump_with_filters(families=None, statuses=None, ready_only=False):
    st.session_state['family_filter'] = families or []
    st.session_state['status_filter'] = statuses or []
    st.session_state['detail_ready_only'] = ready_only
    st.session_state['search_text'] = ''
    st.switch_page('pages/factors.py')


def render_showcase_card(detail: dict, key_prefix: str):
    with st.container(border=True):
        st.markdown(f"### {pick_text(detail['factor_name_zh'], detail['factor_name_en'])}")
        st.caption(f"{detail['family']} · {detail['status']}")
        if detail.get('preview_plot'):
            st.image(data_path(detail.get('preview_plot')), use_container_width=True)
        st.write(pick_text(detail['short_desc_zh'], detail['short_desc_en']))
        m1, m2 = st.columns(2)
        metrics = detail.get('metrics', {})
        with m1:
            st.metric(t('annual_return'), fmt_metric(metrics.get('annual_return'), pct=True))
            st.metric(t('ic_mean'), fmt_metric(metrics.get('ic_mean'), digits=4))
        with m2:
            st.metric(t('sharpe'), fmt_metric(metrics.get('sharpe'), digits=3))
            st.metric(t('max_drawdown'), fmt_metric(metrics.get('max_drawdown'), pct=True))
        b1, b2 = st.columns(2)
        with b1:
            if st.button(t('details_button'), key=f'{key_prefix}_detail', use_container_width=True):
                set_selected_factor(detail['factor_id'])
                st.switch_page('pages/factor_detail.py')
        with b2:
            if st.button(t('compare_add_button'), key=f'{key_prefix}_compare', use_container_width=True):
                add_to_compare(detail['factor_id'])
                st.toast(t('added_to_compare'))


def build_nav_frame(fids):
    import pandas as pd
    from utils.data_loader import load_series_table

    out = pd.DataFrame()
    for fid in fids:
        pnl = load_series_table(fid, 'pnl.csv')
        if pnl is None:
            continue
        pnl['date'] = pd.to_datetime(pnl['date'])
        out[fid] = (1 + pd.to_numeric(pnl['net_return'], errors='coerce').fillna(0)).cumprod().values
        out.index = pnl['date']
    return out


st.title('Temporal Alpha CN')
st.subheader(t('home_subtitle'))

c1, c2 = st.columns([1, 1])
with c1:
    if st.button(t('explore_factors'), use_container_width=True):
        st.switch_page('pages/factors.py')
with c2:
    if st.button(t('compare_factors'), use_container_width=True):
        st.switch_page('pages/compare.py')

cards = st.columns(len(rep_details))
for col, detail in zip(cards, rep_details):
    with col:
        with st.container(border=True):
            st.markdown(f"### {pick_text(detail['factor_name_zh'], detail['factor_name_en'])}")
            st.caption(f"{detail['family']} · {detail['status']}")
            st.metric(t('ic_mean'), fmt_metric(detail['metrics'].get('ic_mean'), digits=4))
            st.metric(t('sharpe'), fmt_metric(detail['metrics'].get('sharpe'), digits=3))
            st.metric(t('annual_return'), fmt_metric(detail['metrics'].get('annual_return'), pct=True))
            b1, b2 = st.columns(2)
            with b1:
                if st.button(t('details_button'), key=f'home_detail_{detail["factor_id"]}', use_container_width=True):
                    set_selected_factor(detail['factor_id'])
                    st.switch_page('pages/factor_detail.py')
            with b2:
                if st.button(t('compare_add_button'), key=f'home_compare_{detail["factor_id"]}', use_container_width=True):
                    add_to_compare(detail['factor_id'])
                    st.toast(t('added_to_compare'))

st.markdown('## NAV Comparison')
nav_frame = build_nav_frame(rep_ids)
if nav_frame.empty:
    if manifest.get('home_compare_image'):
        st.image(data_path(manifest.get('home_compare_image')), use_container_width=True)
else:
    st.line_chart(nav_frame, use_container_width=True)

st.markdown(f"## {t('project_overview')}")
st.write(t('project_overview_body'))

st.markdown(f"## {t('research_scope')}")
metric_cols = st.columns(4)
metric_cols[0].metric(t('factor_count'), int(manifest.get('total_researched_factors', len(summaries))))
metric_cols[1].metric(t('showcase_count'), int(len(summaries)))
metric_cols[2].metric(t('baseline_count'), int((summaries['status'] == 'Baseline').sum()))
metric_cols[3].metric(t('custom_count'), int((summaries['status'] != 'Baseline').sum()))

baseline_rows = summaries[summaries['status'] == 'Baseline']

st.markdown(f"## {t('baseline_section_title')}")
st.write(t('baseline_section_body'))
if st.button(t('view_all_baselines'), use_container_width=False):
    _jump_with_filters(['Baseline'], ['Baseline'], False)
baseline_details = [load_factor_detail(fid) for fid in baseline_rows['factor_id'].tolist()]
cols = st.columns(min(3, len(baseline_details)))
for col, detail in zip(cols, baseline_details):
    with col:
        render_showcase_card(detail, key_prefix=f'baseline_home_{detail["factor_id"]}')

st.markdown(f"## {t('selected_section_title')}")
st.write(t('selected_section_body'))
if st.button(t('view_selected_extensions'), use_container_width=False):
    _jump_with_filters([], ['Exploratory'], False)
cols = st.columns(min(2, len(selected_details)))
for col, detail in zip(cols, selected_details):
    with col:
        render_showcase_card(detail, key_prefix=f'selected_home_{detail["factor_id"]}')

st.markdown(f"## {t('exploration_log_title')}")
st.write(t('exploration_log_teaser'))
if st.button(t('open_exploration_log'), use_container_width=False):
    st.switch_page('pages/exploration.py')

st.info(t('home_notes'))
render_footer()
