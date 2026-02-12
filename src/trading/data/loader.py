import pandas as pd

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # si colonne time existe, on tente de la parser en datetime
    if "time" in df.columns:
        try:
            df["time"] = pd.to_datetime(df["time"])
            df = df.sort_values("time").reset_index(drop=True)
        except Exception:
            pass

    return df
