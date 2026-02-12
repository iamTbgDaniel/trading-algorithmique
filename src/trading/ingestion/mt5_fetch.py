from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import MetaTrader5 as mt5


@dataclass
class MT5Config:
    login: Optional[int] = None
    password: Optional[str] = None
    server: Optional[str] = None


def mt5_connect(cfg: MT5Config) -> None:
    """Connexion MT5. Si cfg vide, tente d'utiliser la session MT5 déjà ouverte."""
    if mt5.initialize():
        # si login fourni, on tente login explicite
        if cfg.login and cfg.password and cfg.server:
            ok = mt5.login(cfg.login, password=cfg.password, server=cfg.server)
            if not ok:
                err = mt5.last_error()
                mt5.shutdown()
                raise RuntimeError(f"Échec login MT5: {err}")
        return

    err = mt5.last_error()
    raise RuntimeError(f"Impossible d'initialiser MT5. Détails: {err}")


def mt5_shutdown() -> None:
    mt5.shutdown()


def fetch_rates(symbol: str, timeframe: int, start_utc: datetime, end_utc: datetime) -> pd.DataFrame:
    """
    Récupère OHLCV sur [start_utc, end_utc] en UTC.
    """
    if start_utc.tzinfo is None:
        start_utc = start_utc.replace(tzinfo=timezone.utc)
    if end_utc.tzinfo is None:
        end_utc = end_utc.replace(tzinfo=timezone.utc)

    rates = mt5.copy_rates_range(symbol, timeframe, start_utc, end_utc)
    if rates is None:
        raise RuntimeError(f"Aucune donnée retournée (symbol={symbol}). Erreur: {mt5.last_error()}")
    if len(rates) == 0:
        raise RuntimeError(f"0 bougie retournée (symbol={symbol}). Vérifie le symbole/TF.")

    df = pd.DataFrame(rates)
    # MT5 renvoie 'time' en seconds epoch
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.rename(columns={"tick_volume": "volume"})
    # garder colonnes cohérentes avec ton pipeline
    keep = ["time", "open", "high", "low", "close", "volume", "spread", "real_volume"]
    df = df[[c for c in keep if c in df.columns]]
    df = df.sort_values("time").reset_index(drop=True)
    return df


def list_symbols() -> list[str]:
    syms = mt5.symbols_get()
    return [s.name for s in syms] if syms else []
