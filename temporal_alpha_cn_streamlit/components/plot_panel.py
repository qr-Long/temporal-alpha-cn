from pathlib import Path
import streamlit as st
from utils.i18n import t


def render_plot(title: str, image_path: str | None, caption: str | None = None):
    st.markdown(f"#### {title}")
    if image_path and Path(image_path).exists():
        st.image(image_path, use_container_width=True)
        if caption:
            st.caption(caption)
    else:
        st.info(t('plot_missing'))
