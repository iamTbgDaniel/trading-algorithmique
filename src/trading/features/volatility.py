from __future__ import annotations
import pandas as pd

def add_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    df = df.copy()

    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)

    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    df[f"atr_{window}"] = tr.rolling(window).mean()
    return df
