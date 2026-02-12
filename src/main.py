import matplotlib.pyplot as plt

from src.trading.utils.config import load_config
from src.trading.data.loader import load_csv

from src.trading.features.indicators import add_moving_average
from src.trading.features.volatility import add_atr

from src.trading.backtesting.engine import run_backtest_atr_sl_tp
from src.trading.evaluation.metrics import summarize
from src.trading.risk.manager import enforce_risk_limits

from src.trading.data.resample import resample_ohlcv
from src.trading.features.align import align_context_to_execution
from src.trading.features.regime import add_trend_filter


def main():
    cfg = load_config("configs/default.yaml")

    # 1) Charger données MT5 (M5)
    df = load_csv(cfg["data_path"])

    # 2) Features d’exécution sur M5
    exec_ma_window = cfg["features"]["ma_window"]
    df = add_moving_average(df, exec_ma_window)

    atr_window = cfg["execution"]["atr_window"]
    df = add_atr(df, atr_window)

    # 3) Multi-timeframe : H4 -> H1 -> M30 -> M15 (filtre), exécution M5
    context_filter = None
    if cfg.get("multi_tf", {}).get("enabled", False):
        rules = cfg["multi_tf"]["rules"]                 # ["4h","1h","30min","15min"]
        context_ma = cfg["multi_tf"]["context_ma_window"]

        combined = None
        for rule in rules:
            ctx = resample_ohlcv(df, rule=rule)
            ctx = add_trend_filter(ctx, ma_window=context_ma)
            aligned = align_context_to_execution(df, ctx)  # 0/1 sur M5
            combined = aligned if combined is None else (combined & aligned)

        context_filter = combined

    # Debug optionnel (tu peux enlever après)
    print("context_filter (10 premières):", None if context_filter is None else context_filter.head(10).tolist())
    if context_filter is not None:
        print("context_filter (10 dernières):", context_filter.tail(10).tolist())

    # 4) Backtest ATR SL/TP (1 position à la fois)
    df = run_backtest_atr_sl_tp(
        df,
        initial_capital=cfg["backtest"]["initial_capital"],
        commission_per_trade=cfg["backtest"]["commission_per_trade"],
        slippage_bps=cfg["backtest"]["slippage_bps"],
        spread_bps=cfg["backtest"]["spread_bps"],
        context_filter=context_filter,
        exec_ma_window=exec_ma_window,
        atr_window=atr_window,
        sl_atr=cfg["execution"]["sl_atr"],
        tp_atr=cfg["execution"]["tp_atr"],
        cooldown_bars=cfg["execution"]["cooldown_bars"],
    )

    print("Nombre de trades (proxy):", int(df["position"].diff().abs().fillna(0).sum()))
    print("Proportion context_ok=1:", float(df["context_ok"].mean()))

    # Debug cohérent (MA + ATR)
    ma_col = f"ma_{exec_ma_window}"
    atr_col = f"atr_{atr_window}"
    print(df[["close", ma_col, atr_col, "context_ok", "position"]].head(20))

    # 5) Stats
    stats = summarize(df)
    print("=== STATS BACKTEST ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    # 6) Risk
    risk = enforce_risk_limits(
        df,
        max_trades=cfg["risk"]["max_trades"],
        max_drawdown=cfg["risk"]["max_drawdown"],
    )
    print("\n=== RISK CHECK ===")
    for k, v in risk.items():
        print(f"{k}: {v}")

    # 7) Plot
    plt.plot(df["equity"])
    plt.title("Equity Curve (ATR SL/TP)")
    plt.show()


if __name__ == "__main__":
    main()
