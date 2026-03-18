import math


def fmt_metric(value, pct: bool = False, digits: int = 3):
    if value is None:
        return '—'
    try:
        if isinstance(value, float) and math.isnan(value):
            return '—'
        if pct:
            return f'{value:.{digits}f}%'
        return f'{value:.{digits}f}'
    except Exception:
        return '—'
