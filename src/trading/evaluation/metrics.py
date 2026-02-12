from __future__ import annotations
import pandas as pd

def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity / peak) - 1.0
    return float(dd.min())

def win_rate(strategy_returns: pd.Series) -> float:
    r = strategy_returns.dropna()
    if len(r) == 0:
        return 0.0
    return float((r > 0).mean())

def profit_factor(strategy_returns: pd.Series) -> float:
    r = strategy_returns.dropna()
    gains = r[r > 0].sum()
    losses = -r[r < 0].sum()
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return float(gains / losses)

def summarize(df: pd.DataFrame) -> dict:
    equity = df["equity"]
    r = df["strategy_return"]

    return {
        "max_drawdown": max_drawdown(equity),
        "win_rate": win_rate(r),
        "profit_factor": profit_factor(r),
        "final_equity": float(equity.iloc[-1]) if len(equity) else 1.0,
        "n_trades_proxy": int(df["position"].diff().abs().fillna(0).sum()) if "position" in df else 0,
    }
