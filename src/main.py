import matplotlib.pyplot as plt

from src.trading.utils.config import load_config
from src.trading.data.loader import load_csv
from src.trading.features.indicators import add_moving_average
from src.trading.backtesting.engine import run_backtest
from src.trading.evaluation.metrics import summarize
from src.trading.risk.manager import enforce_risk_limits


def main():
    cfg = load_config("configs/default.yaml")

    df = load_csv(cfg["data_path"])
    df = add_moving_average(df, cfg["features"]["ma_window"])

    df = run_backtest(
        df,
        initial_capital=cfg["backtest"]["initial_capital"],
        commission_per_trade=cfg["backtest"]["commission_per_trade"],
        slippage_bps=cfg["backtest"]["slippage_bps"],
        spread_bps=cfg["backtest"]["spread_bps"],
    )

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
