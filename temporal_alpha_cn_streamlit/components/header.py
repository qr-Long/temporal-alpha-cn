import streamlit as st
from utils.state import set_language
from utils.i18n import t
from utils.data_loader import load_manifest


def render_top_toolbar():
    manifest = load_manifest()
    c1, c2, c3 = st.columns([6, 2, 1])
    with c1:
        st.markdown("<div class='site-title'>Temporal Alpha CN</div>", unsafe_allow_html=True)
    with c2:
        lang = st.selectbox(
            t('language_label'),
            options=['zh', 'en'],
            index=0 if st.session_state.get('lang', 'zh') == 'zh' else 1,
            format_func=lambda x: '中文' if x == 'zh' else 'English',
            key='top_lang_select',
        )
        if lang != st.session_state.get('lang'):
            set_language(lang)
            st.rerun()
    with c3:
        st.link_button(t('github_button'), manifest.get('github_url', '#'))
    st.divider()
