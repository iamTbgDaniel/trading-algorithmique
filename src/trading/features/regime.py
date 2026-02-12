from __future__ import annotations
import numpy as np
import pandas as pd

def add_trend_filter(df: pd.DataFrame, ma_window: int = 3, col_close: str = "close") -> pd.DataFrame:
    """
    Ajoute un filtre de tendance simple:
    trend = 1 si close > MA, sinon 0
    """
    df = df.copy()
    ma = df[col_close].rolling(ma_window).mean()
    df["trend"] = np.where(df[col_close] > ma, 1, 0)
    return df

def forward_fill_to_execution(exec_df: pd.DataFrame, context_df: pd.DataFrame) -> pd.Series:
    """
    Projette un signal de contexte sur l'exécution en 'forward fill'.
    Ici on fait simple: on répète chaque valeur de context sur n bougies d'exec.
    (On gère n dans main, pour rester explicite)
    """
    # Cette fonction reste volontairement simple; on utilisera un vrai alignement temporel avec dates plus tard.
    return context_df["trend"]
