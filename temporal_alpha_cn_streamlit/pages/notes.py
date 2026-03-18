import streamlit as st
from components.footer import render_footer
from utils.i18n import t, pick_text

st.title(t('notes_title'))

sections = [
    (t('notes_data'), pick_text('网站当前读取的是你提供的 exp_001 输出，并且只保留 7 个主展示因子。这样处理不是为了省事，而是因为网站更适合讲清楚主线；更完整的尝试过程仍然保留在 Exploration Log。', 'The site reads from your exp_001 outputs and keeps only seven showcase factors. That choice is about clarity rather than convenience. The homepage is meant to show the main line clearly, while the broader search process remains available in the Exploration Log.')),
    (t('notes_rebalance'), pick_text('当前统一采用 t 日收盘出信号、t+1 开盘成交、open-to-open 收益口径。这个时序规则会直接影响天文时域想法能否转成可交易结果，所以所有候选因子都必须放在同一规则下比较。', 'The current convention is t-close signal formation, t+1-open execution, and open-to-open return measurement. That timing choice directly affects whether a time-domain idea turns into a tradable result, so every candidate factor has to be judged under the same rule.')),
    (t('notes_cost'), pick_text('网站默认展示最低成本档位下的 headline 结果，但每个主因子都保留完整的成本敏感性图。这样读者既能先看到主结果，也能判断它对成本有多敏感。', 'The site shows headline results at the lowest cost setting by default, but each main factor still keeps a full cost-sensitivity plot. That lets the reader see the main result first and then judge how fragile it is to trading costs.')),
    (t('notes_limits'), pick_text('这是研究展示层，不是生产级回测系统。股票池使用的是当前处理版本下的沪深 300 成分，因此存在 survivorship bias；数据接口、样本边界和实现细节仍然应以研究包和原始结果文件为准。', 'This is a research presentation layer, not a production backtesting system. The stock universe uses the current HS300 constituent treatment, so survivorship-bias risk remains. Data boundaries and implementation details should still be taken from the research package and the raw result files.')),
    (t('notes_interpret'), pick_text('这个网站不只保留正结果，也保留负结果和方向检查。对量化研究来说，知道某条路线为什么没进主展示区，和知道最后哪条路线有效，一样重要。', 'The site keeps negative results and direction checks alongside positive ones. In this kind of research, it matters just as much to know why a route did not make the final showcase as it does to know which route worked.')),
]
for title, body in sections:
    st.markdown(f"## {title}")
    st.write(body)

render_footer()
