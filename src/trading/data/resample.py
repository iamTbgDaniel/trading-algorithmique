from __future__ import annotations
import pandas as pd


def resample_ohlcv(df: pd.DataFrame, rule: str, time_col: str = "time") -> pd.DataFrame:
    """
    Resample OHLCV basé sur datetime.
    Exemples rule : "4H", "1H", "30min", "15min"
    """

    if time_col not in df.columns:
        raise ValueError(f"Colonne '{time_col}' absente pour resample.")

    d = df.copy()
    d[time_col] = pd.to_datetime(d[time_col])
    d = d.set_index(time_col).sort_index()

    out = d.resample(rule).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )

    out = out.dropna().reset_index()
    return out
