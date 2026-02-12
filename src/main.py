import matplotlib.pyplot as plt

from src.trading.utils.config import load_config
from src.trading.data.loader import load_csv
from src.trading.features.indicators import add_moving_average
from src.trading.backtesting.engine import run_backtest
from src.trading.evaluation.metrics import summarize
from src.trading.risk.manager import enforce_risk_limits
from src.trading.data.resample import aggregate_ohlcv
from src.trading.features.regime import add_trend_filter


def main():
    cfg = load_config("configs/default.yaml")

    df = load_csv(cfg["data_path"])
    df = add_moving_average(df, cfg["features"]["ma_window"])
    context_filter = None

    if cfg.get("multi_tf", {}).get("enabled", False):
        n = cfg["multi_tf"]["context_agg_n"]
        context = aggregate_ohlcv(df, n=n)
        context = add_trend_filter(context, ma_window=cfg["multi_tf"]["context_ma_window"])

        # On projette le trend contexte sur l'exécution en répétant chaque valeur n fois
        context_filter = context["trend"].repeat(n).reset_index(drop=True)
    
    print("context_filter (10 premières):", None if context_filter is None else context_filter.head(10).tolist())
    df = run_backtest(
        df,
        initial_capital=cfg["backtest"]["initial_capital"],
        commission_per_trade=cfg["backtest"]["commission_per_trade"],
        slippage_bps=cfg["backtest"]["slippage_bps"],
        spread_bps=cfg["backtest"]["spread_bps"],
        context_filter=context_filter,
    )
    print(df[["close", "ma_3", "context_ok", "position"]].head(10))

    # 1) Stats de performance
    stats = summarize(df)
    print("=== STATS BACKTEST ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    # 2) Contrôle de risque
    risk = enforce_risk_limits(
        df,
        max_trades=cfg["risk"]["max_trades"],
        max_drawdown=cfg["risk"]["max_drawdown"],
    )
    print("\n=== RISK CHECK ===")
    for k, v in risk.items():
        print(f"{k}: {v}")

    # 3) Plot
    plt.plot(df["equity"])
    plt.title("Equity Curve")
    plt.show()


if __name__ == "__main__":
    main()
