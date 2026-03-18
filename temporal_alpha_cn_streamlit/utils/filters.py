import pandas as pd


def apply_factor_filters(df: pd.DataFrame, search_text: str = '', families=None, statuses=None, detail_ready_only: bool = False, sort_by: str = 'sharpe') -> pd.DataFrame:
    out = df.copy()
    if search_text:
        text = search_text.strip().lower()
        out = out[
            out['factor_id'].str.lower().str.contains(text, na=False)
            | out['factor_name_en'].str.lower().str.contains(text, na=False)
            | out['factor_name_zh'].astype(str).str.contains(text, na=False)
        ]
    if families:
        out = out[out['family'].isin(families)]
    if statuses:
        out = out[out['status'].isin(statuses)]
    if detail_ready_only:
        out = out[out['detail_ready'] == True]
    ascending = sort_by in {'max_drawdown'}
    if sort_by in out.columns:
        out = out.sort_values(by=sort_by, ascending=ascending, na_position='last')
    return out.reset_index(drop=True)
