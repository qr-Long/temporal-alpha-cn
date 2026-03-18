import streamlit as st
from components.footer import render_footer
from utils.i18n import t, pick_text

st.title(t('method_title'))

st.markdown(f"## {t('method_motivation')}")
st.write(pick_text(
    '这个项目的起点很直接：天文和量化都在处理高噪声时间序列，只是对象不同。天文里研究的是光变曲线和瞬变源，量化里研究的是价格路径和横截面收益。我的做法不是把天文学术语搬过来，而是把其中几步真正有用的分析流程迁到股票研究里。',
    'The starting point is straightforward. Astronomy and quantitative research both deal with noisy time series, even though the objects are different. Astronomy looks at light curves and transient sources. Quant research looks at price paths and cross-sectional returns. The goal here is not to borrow astronomy vocabulary. It is to borrow parts of the workflow that might still be useful in equity research.'
))

st.markdown(f"## {t('method_logic')}")
st.write(pick_text(
    '主线因子来自 Structure Function。先定义日对数收益 $r_t$，再在固定滞后 $\\tau$ 下观察收益差分平方是否持续偏大。以代表性版本为例，核心量可以写成：',
    'The main factor family comes from the Structure Function idea. Start with daily log return $r_t$, then ask whether squared return differences stay large at a fixed lag $\\tau$. For the headline version, the core quantity can be written as:'
))
st.markdown(r"""
$$
SF_t(\tau)=\frac{1}{20}\sum_{i=0}^{19}(r_{t-i}-r_{t-i-\tau})^2
$$
""")
st.write(pick_text(
    '这和普通波动率不一样。它更关心某个固定时间尺度上的结构化变异强度，所以更接近天文里看光变曲线在特定滞后上是否活跃的思路。',
    'This is not a plain volatility estimate. It is a fixed-lag variability measure, which is closer to the way astronomy asks whether a light curve is especially active at a specific timescale.'
))

st.markdown(f"## {t('method_eval')}")
st.write(pick_text(
    '所有因子都放在同一套日频框架下比较：t 日收盘形成信号，t+1 开盘成交，收益按 open-to-open 统计。页面里优先展示年化收益、Sharpe、IC、回撤，再补充换手、成本敏感性和分组收益。这样读者可以先看结果，再看这些结果是否经得住交易约束。',
    'All factors are compared under one daily setup: signal at the t close, execution at the t+1 open, and open-to-open return measurement. The site puts annual return, Sharpe, IC, and drawdown first, then adds turnover, cost sensitivity, and quantile plots. That way the reader can look at the result first and then ask whether it survives trading constraints.'
))

st.markdown(f"## {t('method_scope')}")
st.write(pick_text(
    '这次一共研究了 39 条因子或变体，但网站只保留 7 个主展示结果。其余方向没有被抹掉，而是放进 Exploration Log。这样做的目的很简单：主页面负责讲清楚最重要的发现，探索页负责交代筛选过程。',
    'In total, the project studied 39 factors or variants, but the website keeps only seven in the main showcase. The rest are not hidden; they are moved into the Exploration Log. The split is deliberate: the main pages focus on the clearest findings, and the exploration page records the selection process.'
))

render_footer()
