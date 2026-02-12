import os
import pandas as pd

from trading.data.resample import resample_ohlcv

IN_FILE = "data/raw/STEP200/M5.csv"
OUT_DIR = "data/processed/STEP200"

RULES = {
    "M15": "15min",
    "M30": "30min",
    "H1": "1h",
    "H4": "4h",
}

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(IN_FILE)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.sort_values("time").reset_index(drop=True)

    for name, rule in RULES.items():
        out = resample_ohlcv(df, rule=rule)
        path = os.path.join(OUT_DIR, f"{name}.csv")
        out.to_csv(path, index=False)
        print(f"✅ {name} -> {path}  ({len(out)} bougies)")

if __name__ == "__main__":
    main()
