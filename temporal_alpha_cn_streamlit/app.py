import streamlit as st
from pathlib import Path

from components.header import render_top_toolbar
from utils.state import init_state

st.set_page_config(
    page_title='Temporal Alpha CN',
    page_icon='📈',
    layout='wide',
    initial_sidebar_state='expanded',
)

init_state()

css_path = Path(__file__).parent / 'assets' / 'style.css'
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

pages = {
    'Navigation': [
        st.Page('pages/home.py', title='Home / 首页', icon='🏠', default=True),
        st.Page('pages/factors.py', title='Factors / 因子库', icon='🧩'),
        st.Page('pages/factor_detail.py', title='Factor Detail / 因子详情', icon='📄'),
        st.Page('pages/compare.py', title='Compare / 对比', icon='📊'),
        st.Page('pages/exploration.py', title='Exploration Log / 探索记录', icon='🧪'),
        st.Page('pages/method.py', title='Method / 方法', icon='🧠'),
        st.Page('pages/notes.py', title='Notes / 说明', icon='📝'),
    ]
}

render_top_toolbar()
pg = st.navigation(pages, position='top')
pg.run()
