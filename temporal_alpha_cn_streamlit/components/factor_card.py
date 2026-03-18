import streamlit as st
from utils.formatters import fmt_metric
from utils.i18n import t, pick_text
from utils.state import add_to_compare, set_selected_factor


def render_factor_card(row, key_prefix='card'):
    factor_id = row.get("factor_id")
    with st.container(border=True):
        st.markdown(f"### {pick_text(row['factor_name_zh'], row['factor_name_en'])}")
        st.caption(f"{row['family']} · {row['status']}")
        st.write(pick_text(row['short_desc_zh'], row['short_desc_en']))

        m1, m2 = st.columns(2)
        with m1:
            st.metric(t('annual_return'), fmt_metric(row.get('annual_return'), pct=True))
            st.metric(t('ic_mean'), fmt_metric(row.get('ic_mean'), digits=4))
        with m2:
            st.metric(t('sharpe'), fmt_metric(row.get('sharpe'), digits=3))
            st.metric(t('max_drawdown'), fmt_metric(row.get('max_drawdown'), pct=True))

        b1, b2 = st.columns(2)
        with b1:
            if st.button(
                t('details_button'),
                key=f'{key_prefix}_detail_{factor_id or key_prefix}',
                use_container_width=True
            ):
                if factor_id:
                    set_selected_factor(factor_id)
                    st.switch_page('pages/factor_detail.py')
        with b2:
            if st.button(
                t('compare_add_button'),
                key=f'{key_prefix}_compare_{factor_id or key_prefix}',
                use_container_width=True
            ):
                if factor_id:
                    add_to_compare(factor_id)
                    st.toast(t('added_to_compare'))
