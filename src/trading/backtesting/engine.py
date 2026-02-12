from __future__ import annotations
import numpy as np
import pandas as pd


def _apply_costs(
    strategy_return: pd.Series,
    position_change: pd.Series,
    commission_per_trade: float,
    slippage_bps: float,
    spread_bps: float,
) -> pd.Series:
    slippage = slippage_bps * 0.0001
    spread = spread_bps * 0.0001
    trade_event = (position_change.abs() > 0).astype(float)
    total_cost = trade_event * (commission_per_trade + slippage + spread)
    return strategy_return - total_cost


def run_backtest(
    df: pd.DataFrame,
    initial_capital: float = 1.0,
    commission_per_trade: float = 0.0,
    slippage_bps: float = 0.0,
    spread_bps: float = 0.0,
    context_filter: pd.Series | None = None,
    exec_ma_window: int = 20,
) -> pd.DataFrame:
    """
    Backtest simple long-only:
    position = 1 si close > MA (et context_ok si fourni), sinon 0.
    """
    df = df.copy()

    df["return"] = df["close"].pct_change()

    ma_col = f"ma_{exec_ma_window}"
    if ma_col not in df.columns:
        raise ValueError(
            f"Colonne {ma_col} absente. Appelle add_moving_average(df, {exec_ma_window}) avant le backtest."
        )

    exec_signal = np.where(df["close"] > df[ma_col], 1, 0)

    if context_filter is not None:
        context_filter = pd.Series(context_filter).reset_index(drop=True)
        m = min(len(df), len(context_filter))
        df = df.iloc[:m].copy()
        context_filter = context_filter.iloc[:m].copy()

        df["context_ok"] = (context_filter == 1).astype(int)
        df["position"] = exec_signal[:m] * df["context_ok"]
    else:
        df["context_ok"] = 1
        df["position"] = exec_signal

    df["strategy_return_raw"] = df["position"].shift(1) * df["return"]
    df["position_change"] = df["position"].diff().fillna(0)

    df["strategy_return"] = _apply_costs(
        df["strategy_return_raw"].fillna(0),
        df["position_change"],
        commission_per_trade=commission_per_trade,
        slippage_bps=slippage_bps,
        spread_bps=spread_bps,
    )

    df["equity"] = initial_capital * (1 + df["strategy_return"]).cumprod()
    return df


def run_backtest_atr_sl_tp(
    df: pd.DataFrame,
    initial_capital: float = 1.0,
    commission_per_trade: float = 0.0,
    slippage_bps: float = 0.0,
    spread_bps: float = 0.0,
    context_filter: pd.Series | None = None,
    exec_ma_window: int = 20,
    atr_window: int = 14,
    sl_atr: float = 1.5,
    tp_atr: float = 2.0,
    cooldown_bars: int = 3,
) -> pd.DataFrame:
    """
    Backtest long-only avec ATR StopLoss/TakeProfit.
    - 1 position à la fois
    - Entrée: context_ok=1 ET close > MA et cooldown==0
    - Sortie: SL/TP touché via low/high (réaliste intra-bougie)
    - Cooldown: attendre X bougies après une sortie
    """
    df = df.copy()
    df["return"] = df["close"].pct_change().fillna(0)

    ma_col = f"ma_{exec_ma_window}"
    atr_col = f"atr_{atr_window}"

    if ma_col not in df.columns:
        raise ValueError(f"{ma_col} absent. Appelle add_moving_average(df, {exec_ma_window}).")
    if atr_col not in df.columns:
        raise ValueError(f"{atr_col} absent. Appelle add_atr(df, {atr_window}).")

    # Contexte
    if context_filter is not None:
        context_filter = pd.Series(context_filter).reset_index(drop=True)
        m = min(len(df), len(context_filter))
        df = df.iloc[:m].copy()
        context_filter = context_filter.iloc[:m].copy()
        df["context_ok"] = (context_filter == 1).astype(int)
    else:
        df["context_ok"] = 1

    # Simulation d'une position unique
    position = 0
    entry = 0.0
    sl = 0.0
    tp = 0.0
    cooldown = 0

    df["position"] = 0
    df["strategy_return_raw"] = 0.0

    for i in range(1, len(df)):
        close = float(df.loc[i, "close"])
        high = float(df.loc[i, "high"])
        low = float(df.loc[i, "low"])
        atr = df.loc[i, atr_col]

        if cooldown > 0:
            cooldown -=1

        # ATR pas prêt => on ne trade pas
        if pd.isna(atr):
            df.loc[i, "position"] = position
            continue

        atr = float(atr)

        #Sortie(si en position)
        if position == 1:
            hit_sl = low <= sl
            hit_tp = high >= tp
            if hit_sl or hit_tp:
                position = 0
                cooldown = cooldown_bars

        # Entrée (si flat)
        if position == 0 and cooldown ==0 :
            ok = (df.loc[i, "context_ok"] == 1) and (close > float(df.loc[i, ma_col]))
            if ok:
                position = 1
                entry = close
                sl = entry - sl_atr * atr
                tp = entry + tp_atr * atr


        df.loc[i, "position"] = position
        df.loc[i, "strategy_return_raw"] = df.loc[i, "position"] * df.loc[i, "return"]

    df["position_change"] = df["position"].diff().fillna(0)

    df["strategy_return"] = _apply_costs(
        df["strategy_return_raw"],
        df["position_change"],
        commission_per_trade=commission_per_trade,
        slippage_bps=slippage_bps,
        spread_bps=spread_bps,
    )

    df["equity"] = initial_capital * (1 + df["strategy_return"]).cumprod()
    return df
