import numpy as np
import pandas as pd

def run_backtest(df: pd.DataFrame) -> pd.DataFrame:
    df["return"] = df["close"].pct_change()
    df["position"] = np.where(df["close"] > df["ma_3"], 1, 0)
    df["strategy_return"] = df["position"].shift(1) * df["return"]
    df["equity"] = (1 + df["strategy_return"].fillna(0)).cumprod()
    return df
