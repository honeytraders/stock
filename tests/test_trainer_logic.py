import pandas as pd
from trainer.labeling import build_binary_next_bar_up_targets


def test_per_symbol_labeling_no_leakage():
    data = pd.DataFrame(
        {"symbol": ["AAPL", "AAPL", "TSLA", "TSLA"], "close": [100.0, 105.0, 200.0, 190.0]}
    )

    # Use the shared labeling function
    data["target"] = build_binary_next_bar_up_targets(data, "symbol", "close")

    # Check intermediate state: indices 1 and 3 should be NaN in 'target'
    assert pd.isna(data.loc[1, "target"])
    assert pd.isna(data.loc[3, "target"])

    cleaned = data.dropna(subset=["target"])

    # After dropna, only indices 0 and 2 should remain
    assert len(cleaned) == 2
    assert cleaned.loc[0, "symbol"] == "AAPL"
    assert cleaned.loc[0, "target"] == 1.0
    assert cleaned.loc[2, "symbol"] == "TSLA"
    assert cleaned.loc[2, "target"] == 0.0
