import matplotlib.pyplot as plt

from src.trading.data.loader import load_csv
from src.trading.features.indicators import add_moving_average
from src.trading.backtesting.engine import run_backtest

def main():
    df = load_csv("data/sample.csv")
    df = add_moving_average(df, 3)
    df = run_backtest(df)

    print(df)

    plt.plot(df["equity"])
    plt.title("Equity Curve")
    plt.show()

if __name__ == "__main__":
    main()
