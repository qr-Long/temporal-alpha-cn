import streamlit as st

TEXT = {
    'language_label': {'zh': '语言', 'en': 'Language'},
    'github_button': {'zh': 'GitHub', 'en': 'GitHub'},
    'footer_note': {'zh': '研究展示网站，不构成投资建议。', 'en': 'Research showcase only. Not investment advice.'},
    'details_button': {'zh': '查看详情', 'en': 'Details'},
    'compare_add_button': {'zh': '加入对比', 'en': 'Add to Compare'},
    'added_to_compare': {'zh': '已加入对比列表', 'en': 'Added to compare list'},
    'annual_return': {'zh': '年化收益', 'en': 'Annual Return'},
    'sharpe': {'zh': 'Sharpe', 'en': 'Sharpe'},
    'rankic_mean': {'zh': 'RankIC 均值', 'en': 'RankIC Mean'},
    'max_drawdown': {'zh': '最大回撤', 'en': 'Max Drawdown'},
    'ic_mean': {'zh': 'IC 均值', 'en': 'IC Mean'},
    'icir': {'zh': 'ICIR', 'en': 'ICIR'},
    'rankicir': {'zh': 'RankICIR', 'en': 'RankICIR'},
    'avg_turnover': {'zh': '平均换手', 'en': 'Avg Turnover'},
    'plot_missing': {'zh': '当前没有可展示的图像。', 'en': 'No plot is available yet.'},
    'home_subtitle': {
        'zh': '把天文时域分析里的变异性测量、背景判断和方向检查迁到 A 股横截面因子研究里，再用同一套回测框架筛出真正能落地的结果。',
        'en': 'A research showcase for astronomy-inspired equity alpha factors, built by moving variability measurement, background checking, and direction diagnostics from astronomical time-domain analysis into one equity-factor workflow.'
    },
    'explore_factors': {'zh': '浏览因子库', 'en': 'Explore Factors'},
    'compare_factors': {'zh': '进入对比页', 'en': 'Compare Factors'},
    'project_overview': {'zh': '项目概览', 'en': 'Project Overview'},
    'project_overview_body': {
        'zh': '这个网站展示的是一个很具体的迁移过程：把天文时域分析里处理光变曲线的思路，搬到股票横截面研究里。重点不是照搬术语，而是借用其中几步真正有用的流程——先测固定滞后下的变异强度，再看不同时间尺度是否一致，最后用交易成本和负结果把不够稳的想法筛掉。首页保留的 7 个因子，就是这套流程里最值得讲清楚的结果。',
        'en': 'This site shows a fairly concrete transfer: ideas that were originally used to study light-curve variability are moved into cross-sectional equity factor research. The point is not to borrow astronomical vocabulary. The point is to borrow a useful workflow: measure variability at a fixed lag, check whether the pattern survives across nearby scales, and then filter it with trading costs and negative results. The seven factors on the site are the ones that best capture that process.'
    },
    'research_scope': {'zh': '研究规模', 'en': 'Research Scope'},
    'factor_count': {'zh': '总研究因子数', 'en': 'Total Factors Studied'},
    'showcase_count': {'zh': '网站展示因子数', 'en': 'Factors Shown on Site'},
    'baseline_count': {'zh': '基线因子数', 'en': 'Baseline Count'},
    'custom_count': {'zh': '自定义因子数', 'en': 'Custom Factor Count'},
    'zoom_hint': {'zh': '这张图可以拖拽、滚轮缩放，双击可重置。', 'en': 'You can zoom with the scroll wheel, drag to pan, and double-click to reset.'},
    'home_notes': {
        'zh': '主展示区只放 7 个因子，目的是把结果讲清楚，而不是把所有尝试过的方向堆在首页。graph momentum、matched filter、SF 形状扩展以及局部增强版本都还保留在 Exploration Log 里，用来说明筛选过程和负结果。',
        'en': 'The homepage keeps only seven factors so the story stays clear. Graph momentum, matched filters, SF shape variants, and local-enhancement ideas are still preserved in the Exploration Log, where they serve as part of the selection record rather than as headline results.'
    },
    'baseline_section_title': {'zh': 'Baseline 基线区', 'en': 'Baseline Benchmarks'},
    'baseline_section_body': {
        'zh': '这里保留 3 个标准基线，用来回答最基本的问题：在同一套回测口径下，天文启发因子到底有没有超过常见的动量、反转和均线规则。20 日动量还额外保留了方向检查模块，用来解释为什么原始版本会是负的。',
        'en': 'The three baseline factors answer the first basic question: under the same backtest rules, do the astronomy-inspired signals actually beat common momentum, reversal, and moving-average heuristics? The 20-day momentum page also keeps a sign-check module to explain why the naive version turns out negative.'
    },
    'view_all_baselines': {'zh': '查看全部 Baseline', 'en': 'View All Baselines'},
    'selected_section_title': {'zh': '补充展示因子', 'en': 'Additional Selected Factors'},
    'selected_section_body': {
        'zh': '这一区只放两个补充因子。tau=20 说明 Structure Function 这条线不是只在一个参数点上有效；uniq_knn 则代表另一条更接近相似度和邻域结构的路线，让整个项目不至于只剩下单一家族的故事。',
        'en': 'This section keeps only two extension factors. Tau=20 shows that the Structure Function line does not live on a single lucky parameter, while uniq_knn adds a second route built around similarity and neighborhood structure so the project does not read like a one-family story.'
    },
    'view_selected_extensions': {'zh': '查看补充因子', 'en': 'View Additional Factors'},
    'exploration_log_title': {'zh': '探索记录', 'en': 'Exploration Log'},
    'exploration_log_teaser': {
        'zh': '除了主展示区里的 7 个因子，我还系统试过图扩散、matched filter、SF 形状扩展，以及局部背景和局部显著性版本。它们没有白做，因为这些负结果正好说明：最有效的信号还是短尺度 SF amplitude 本身。',
        'en': 'Beyond the seven factors shown on the site, the project also tested graph diffusion, matched filters, SF shape variants, and local background or local-significance versions. Those trials still matter because the negative results help pin down a simpler conclusion: the strongest signal still comes from the short-horizon SF amplitude core.'
    },
    'open_exploration_log': {'zh': '打开探索记录', 'en': 'Open Exploration Log'},
    'factors_title': {'zh': '因子库', 'en': 'Factor Gallery'},
    'search_label': {'zh': '搜索因子', 'en': 'Search Factors'},
    'family_filter': {'zh': '家族筛选', 'en': 'Family Filter'},
    'status_filter': {'zh': '状态筛选', 'en': 'Status Filter'},
    'sort_by': {'zh': '排序方式', 'en': 'Sort By'},
    'ready_only': {'zh': '只看完整详情', 'en': 'Full detail only'},
    'no_factors': {'zh': '没有匹配到因子。', 'en': 'No factors match the current filters.'},
    'factor_detail': {'zh': '因子详情', 'en': 'Factor Detail'},
    'back_to_factors': {'zh': '返回因子库', 'en': 'Back to Factors'},
    'motivation': {'zh': '设计动机', 'en': 'Motivation'},
    'construction': {'zh': '构造方法', 'en': 'Construction'},
    'interpretation': {'zh': '结果解释', 'en': 'Interpretation'},
    'more_analysis': {'zh': '查看更多分析', 'en': 'More Analysis'},
    'analysis_note': {'zh': '结果解读', 'en': 'Analysis Note'},
    'related_factors': {'zh': '相关因子', 'en': 'Related Factors'},
    'preview_mode_expanded': {'zh': '当前因子仍处于简版预览模式。', 'en': 'This factor is still in preview mode.'},
    'preview_metrics_status': {'zh': '结果指标', 'en': 'Result Metrics'},
    'preview_plot_status': {'zh': '预览图', 'en': 'Preview Plot'},
    'preview_method_status': {'zh': '方法说明', 'en': 'Method Notes'},
    'preview_pending': {'zh': '待补充', 'en': 'Pending'},
    'preview_available': {'zh': '已提供', 'en': 'Available'},
    'compare_title': {'zh': '多因子对比', 'en': 'Factor Comparison'},
    'compare_selection': {'zh': '当前对比列表', 'en': 'Current Compare List'},
    'compare_empty': {'zh': '还没有选择任何因子。', 'en': 'No factors have been selected for comparison yet.'},
    'remove_button': {'zh': '移除', 'en': 'Remove'},
    'clear_compare': {'zh': '清空对比', 'en': 'Clear Compare'},
    'compare_pick_more': {'zh': '继续添加因子', 'en': 'Add More Factors'},
    'compare_presets': {'zh': '快捷预设', 'en': 'Quick Presets'},
    'method_title': {'zh': '方法说明', 'en': 'Method'},
    'method_motivation': {'zh': '项目动机', 'en': 'Project Motivation'},
    'method_logic': {'zh': '因子设计逻辑', 'en': 'Factor Design Logic'},
    'method_eval': {'zh': '评估框架', 'en': 'Evaluation Pipeline'},
    'method_scope': {'zh': '研究范围', 'en': 'Research Scope'},
    'notes_title': {'zh': '说明与边界', 'en': 'Notes'},
    'notes_data': {'zh': '数据范围', 'en': 'Data Scope'},
    'notes_rebalance': {'zh': '调仓假设', 'en': 'Rebalancing Assumptions'},
    'notes_cost': {'zh': '成本假设', 'en': 'Transaction Costs'},
    'notes_limits': {'zh': '回测局限', 'en': 'Backtest Limitations'},
    'notes_interpret': {'zh': '解读提醒', 'en': 'Interpretation Notes'},
    'implementation_label': {'zh': '实现名', 'en': 'Implementation ID'},
}


def get_lang() -> str:
    return st.session_state.get('lang', 'zh')


def t(key: str) -> str:
    lang = get_lang()
    return TEXT.get(key, {}).get(lang, key)


def pick_text(zh: str | None, en: str | None) -> str:
    return zh if get_lang() == 'zh' and zh else (en or zh or '')
