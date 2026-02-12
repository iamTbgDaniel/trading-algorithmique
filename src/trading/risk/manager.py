from __future__ import annotations
import pandas as pd

def check_max_trades(df: pd.DataFrame, max_trades: int) -> bool:
    # proxy: nombre de changements de position
    trades = int(df["position"].diff().abs().fillna(0).sum())
    return trades <= max_trades

def check_max_drawdown(df: pd.DataFrame, max_drawdown: float) -> bool:
    equity = df["equity"]
    peak = equity.cummax()
    dd = (equity / peak) - 1.0
    return float(dd.min()) >= max_drawdown

def enforce_risk_limits(df: pd.DataFrame, max_trades: int, max_drawdown: float) -> dict:
    ok_trades = check_max_trades(df, max_trades)
    ok_dd = check_max_drawdown(df, max_drawdown)

    return {
        "ok_max_trades": ok_trades,
        "ok_max_drawdown": ok_dd,
        "risk_passed": bool(ok_trades and ok_dd),
    }
