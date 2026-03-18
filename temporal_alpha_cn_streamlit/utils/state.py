import streamlit as st


def init_state():
    defaults = {
        'lang': 'zh',
        'selected_factor': 'sf_amp_tau5_s20',
        'compare_list': [],
        'family_filter': [],
        'status_filter': [],
        'sort_by': 'sharpe',
        'search_text': '',
        'detail_ready_only': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_language(lang: str):
    st.session_state['lang'] = lang


def set_selected_factor(factor_id: str):
    st.session_state['selected_factor'] = factor_id


def add_to_compare(factor_id: str):
    compare = st.session_state.get('compare_list', [])
    if factor_id not in compare and len(compare) < 4:
        compare.append(factor_id)
        st.session_state['compare_list'] = compare


def remove_from_compare(factor_id: str):
    st.session_state['compare_list'] = [x for x in st.session_state.get('compare_list', []) if x != factor_id]


def clear_compare():
    st.session_state['compare_list'] = []
