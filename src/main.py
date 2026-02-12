import matplotlib.pyplot as plt

from src.trading.utils.config import load_config
from src.trading.data.loader import load_csv
from src.trading.features.indicators import add_moving_average
from src.trading.backtesting.engine import run_backtest
from src.trading.evaluation.metrics import summarize


def main():
    cfg = load_config("configs/default.yaml")

    df = load_csv(cfg["data_path"])
    df = add_moving_average(df, cfg["features"]["ma_window"])
    df = run_backtest(df)

    stats = summarize(df)
    print("=== STATS BACKTEST ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    plt.plot(df["equity"])
    plt.title("Equity Curve")
    plt.show()


if __name__ == "__main__":
    main()
