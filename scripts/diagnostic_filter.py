import pandas as pd

from trading.data.loader import load_csv
from trading.data.resample import resample_ohlcv
from trading.features.regime import add_trend_filter
from trading.features.align import align_context_to_execution

DATA = "data/raw/STEP200/M5.csv"
RULES = ["4h", "1h", "30min", "15min"]
MA = 10

def main():
    df = load_csv(DATA)
    print("M5 rows:", len(df))

    per_rule = {}
    aligned_map = {}

    for rule in RULES:
        ctx = resample_ohlcv(df, rule=rule)
        ctx = add_trend_filter(ctx, ma_window=MA)
        aligned = align_context_to_execution(df, ctx)
        aligned_map[rule] = aligned
        per_rule[rule] = float(aligned.mean())

    combined = None
    for rule in RULES:
        combined = aligned_map[rule] if combined is None else (combined & aligned_map[rule])

    print("\n=== % trend=1 (aligné sur M5) ===")
    for rule, pct in per_rule.items():
        print(f"{rule}: {pct:.3f}")

    print(f"\n=== combined AND (4/4) ===\ncombined: {float(combined.mean()):.3f}")

    # Majority 3/4 pour comparer
    votes = sum(aligned_map[r] for r in RULES)
    majority_3of4 = (votes >= 3).astype(int)
    print(f"\n=== majority 3/4 ===\nmajority_3of4: {float(majority_3of4.mean()):.3f}")

if __name__ == "__main__":
    main()
