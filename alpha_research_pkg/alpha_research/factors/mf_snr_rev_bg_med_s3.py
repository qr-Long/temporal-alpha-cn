from __future__ import annotations
import pandas as pd
from .mf_snr import snr_continuous

def compute_factor_panel(prices: pd.DataFrame) -> pd.DataFrame:
    """mf_snr_rev_bg_med_s3: continuous SNR factor.

    direction='rev', bg_method='median', vol_window=20, smooth_span=3, soft_k=1.0
    """
    return snr_continuous(
        prices,
        direction="rev",
        vol_window=20,
        bg_method="median",
        smooth_span=3,
        soft_k=1.0,
    )
