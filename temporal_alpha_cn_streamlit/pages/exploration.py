import streamlit as st
from components.footer import render_footer
from utils.i18n import pick_text

st.title(pick_text('探索记录', 'Exploration Log'))
st.write(pick_text(
    '这一页不是把没选上的因子堆在一起，而是把筛选过程留档。项目里确实试过不少更复杂的想法，但最后留下来的结果说明，最有效的信号还是来自比较简单的短尺度 SF amplitude。',
    'This page is not just a pile of discarded factors. It records the selection process. The project did test several more elaborate ideas, but the final takeaway is that the strongest signal still comes from a relatively simple short-horizon SF amplitude core.'
))

sections = [
    (
        pick_text('Graph momentum 及其变体', 'Graph momentum and its variants'),
        pick_text(
            'graph_mom20 及其变体主要测试图扩散和邻域平滑能不能让常规动量更稳定。结果说明这条线在解释上有意思，但没有形成足够稳的可交易结果，所以没有进入主展示区。',
            'graph_mom20 and its variants mainly tested whether graph diffusion or neighborhood smoothing could stabilize a standard momentum signal. The idea is interesting, but the results were not stable enough to justify a place in the main showcase.'
        )
    ),
    (
        pick_text('Matched filter 家族', 'Matched filter family'),
        pick_text(
            'matched filter 这一组尝试把脉冲、漂移和反转模式做成模板，再去匹配股票时间序列。最后看下来，这条路线没有形成足够清楚也足够稳的 alpha 画像，所以这里只保留结论，不再单独展开。',
            'The matched-filter family tried to turn impulse, drift, and reversal motifs into templates and then match them against stock time series. In the end, the route did not produce a profile that was both clear and stable enough, so the site keeps only the conclusion rather than full pages for each variant.'
        )
    ),
    (
        pick_text('SF 形状扩展与局部增强', 'SF shape variants and local enhancements'),
        pick_text(
            'slope、ratio、curvature、asymmetry、local background 和 local significance 这些方向都让结构函数的解释更丰富，但交易结果没有超过 amplitude 主线。它们最大的作用，是帮助确认主结果其实来自 SF amplitude 的核心结构，而不是来自更复杂的修饰。',
            'Slope, ratio, curvature, asymmetry, local background, and local significance all made the Structure Function story richer, but none beat the amplitude core in trading terms. Their main value is diagnostic: they help confirm that the result is really coming from the SF amplitude structure itself rather than from extra decoration.'
        )
    ),
]

for title, body in sections:
    st.markdown(f'## {title}')
    st.write(body)

st.info(pick_text(
    '最终主展示区只保留最能代表研究结论的 7 个因子：3 个基线、2 个主结果、1 个时间尺度扩展，以及 1 条独立的邻域结构路线。',
    'The final showcase keeps seven factors that best represent the research conclusion: three baselines, two headline results, one scale extension, and one independent neighborhood-structure route.'
))

render_footer()
