from datetime import datetime, timedelta, timezone
import os

import MetaTrader5 as mt5

from trading.ingestion.mt5_fetch import MT5Config, mt5_connect, mt5_shutdown, fetch_rates

# 1) Réglages
SYMBOL = "Step Index 200"  # ⚠️ peut varier (on va vérifier juste après)
TF = mt5.TIMEFRAME_M5
DAYS = 365  # récupère 365 jours d'historique M5

OUT_DIR = "data/raw/STEP200"
OUT_FILE = os.path.join(OUT_DIR, "M5.csv")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 2) Connexion
    mt5_connect(MT5Config())  # utilise la session MT5 ouverte

    # 3) Fenêtre temps
    end_utc = datetime.now(timezone.utc)
    start_utc = end_utc - timedelta(days=DAYS)

    # 4) Fetch
    df = fetch_rates(SYMBOL, TF, start_utc, end_utc)
    df.to_csv(OUT_FILE, index=False)

    print(f"✅ Export OK: {OUT_FILE}")
    print(df.head())
    print(df.tail())

    mt5_shutdown()

if __name__ == "__main__":
    main()
