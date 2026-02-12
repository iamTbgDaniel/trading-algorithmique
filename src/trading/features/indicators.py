import pandas as pd

def add_moving_average(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    df[f"ma_{window}"] = df["close"].rolling(window).mean()
    return df
