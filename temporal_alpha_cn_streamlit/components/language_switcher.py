import streamlit as st
from utils.state import set_language
from utils.i18n import t


def render_language_switcher(sidebar: bool = False):
    container = st.sidebar if sidebar else st
    lang = container.radio(
        t('language_label'),
        options=['zh', 'en'],
        index=0 if st.session_state.get('lang', 'zh') == 'zh' else 1,
        format_func=lambda x: '中文' if x == 'zh' else 'English',
        key='sidebar_lang_select' if sidebar else 'inline_lang_select'
    )
    if lang != st.session_state.get('lang'):
        set_language(lang)
        st.rerun()
