"""Chargement et nettoyage des données Box Office (2000-2024)."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd


FEATURE_COLUMNS: List[str] = [
    "$Worldwide",
    "$Domestic",
    "Domestic %",
    "$Foreign",
    "Foreign %",
    "Vote_Count",
    "Rating_Num",
]


def parse_rating(value: object) -> Optional[float]:
    """Extrait une note numérique depuis une chaîne de type '6.126/10'."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    try:
        return float(text)
    except ValueError:
        return None


def load_and_clean_box_office(csv_path: Path) -> pd.DataFrame:
    """Charge le CSV Box Office et prépare les colonnes numériques utiles."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Jeu de données introuvable : {path}")

    df = pd.read_csv(path)
    df["Rating_Num"] = df["Rating"].apply(parse_rating) if "Rating" in df.columns else None

    for col in FEATURE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = pd.NA

    return df
