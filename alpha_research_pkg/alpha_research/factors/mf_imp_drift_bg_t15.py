from __future__ import annotations
import pandas as pd
from .mf_impulse import impulse_event_factor

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """mf_imp_drift_bg_t15: impulse event matched filter.

    direction='drift', threshold=1.5, bg_method='median',
    vol_window=20, use_volume=False
    """
    return impulse_event_factor(
        prices,
        direction="drift",
        threshold=1.5,
        vol_window=20,
        bg_method="median",
        use_volume=False,
        vol_spike_win=20,
        vol_beta=1.0,
    )
