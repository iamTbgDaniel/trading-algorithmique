from __future__ import annotations
import pandas as pd

def align_context_to_execution(exec_df: pd.DataFrame, context_df: pd.DataFrame, time_col: str = "time") -> pd.Series:
    """
    Pour chaque bougie d'exécution (M5), on récupère le dernier signal 'trend'
    du contexte (H4/H1/M30/M15) connu à ce moment (<= time).
    """
    if time_col not in exec_df.columns:
        raise ValueError(f"'{time_col}' absent de exec_df")
    if time_col not in context_df.columns:
        raise ValueError(f"'{time_col}' absent de context_df")
    if "trend" not in context_df.columns:
        raise ValueError("'trend' absent de context_df (appelle add_trend_filter avant)")

    e = exec_df[[time_col]].copy()
    c = context_df[[time_col, "trend"]].copy()

    e[time_col] = pd.to_datetime(e[time_col], utc=True, errors="coerce")
    c[time_col] = pd.to_datetime(c[time_col], utc=True, errors="coerce")

    e = e.dropna().sort_values(time_col)
    c = c.dropna().sort_values(time_col)

    merged = pd.merge_asof(e, c, on=time_col, direction="backward")
    return merged["trend"].fillna(0).astype(int)
