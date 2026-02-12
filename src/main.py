import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data/sample.csv")

df["return"] = df["close"].pct_change()
df["ma3"] = df["close"].rolling(3).mean()

df["position"] = np.where(df["close"] > df["ma3"], 1, 0)
df["strategy_return"] = df["position"].shift(1) * df["return"]

df["equity"] = (1 + df["strategy_return"]).cumprod()

print(df)

plt.plot(df["equity"])
plt.title("Equity Curve")
plt.show()
