import streamlit as st
from utils.state import clear_compare, remove_from_compare
from utils.i18n import t


def render_compare_toolbar(compare_list):
    st.subheader(t('compare_selection'))
    if not compare_list:
        st.info(t('compare_empty'))
        return
    for fid in compare_list:
        c1, c2 = st.columns([4, 1])
        c1.write(fid)
        if c2.button(t('remove_button'), key=f'remove_{fid}'):
            remove_from_compare(fid)
            st.rerun()
    if st.button(t('clear_compare'), use_container_width=True):
        clear_compare()
        st.rerun()
