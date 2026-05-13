import numpy as np
import pandas as pd


def build_binary_next_bar_up_targets(
    df: pd.DataFrame, symbol_col: str, price_col: str
) -> pd.Series:
    """
    Computes a binary target: 1 if next bar's price > current bar's price, else 0.
    Handles cross-symbol leakage by grouping by symbol and shifting.
    Propagates NaNs for the last bar of each symbol.
    """
    next_close = df.groupby(symbol_col)[price_col].shift(-1)
    # Safe boolean comparison with NaN propagation
    target = np.where(next_close.isna(), np.nan, (next_close > df[price_col]).astype(float))
    return pd.Series(target, index=df.index, name="target")
