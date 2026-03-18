import streamlit as st
from utils.formatters import fmt_metric
from utils.i18n import t


def render_metric_grid(metrics: dict):
    items = [
        ('ic_mean', t('ic_mean'), False, 4),
        ('rankic_mean', t('rankic_mean'), False, 4),
        ('annual_return', t('annual_return'), True, 2),
        ('sharpe', t('sharpe'), False, 3),
        ('max_drawdown', t('max_drawdown'), True, 2),
        ('icir', t('icir'), False, 3),
        ('rankicir', t('rankicir'), False, 3),
        ('avg_turnover', t('avg_turnover'), True, 2),
    ]
    cols = st.columns(4)
    for idx, (k, label, pct, digits) in enumerate(items):
        with cols[idx % 4]:
            st.metric(label, fmt_metric(metrics.get(k), pct=pct, digits=digits))
