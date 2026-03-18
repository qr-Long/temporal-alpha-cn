import streamlit as st
from utils.data_loader import load_manifest
from utils.i18n import t


def render_footer():
    manifest = load_manifest()
    st.divider()
    cols = st.columns([4, 1])
    with cols[0]:
        st.caption(t('footer_note'))
    with cols[1]:
        st.link_button(t('github_button'), manifest.get('github_url', '#'))
