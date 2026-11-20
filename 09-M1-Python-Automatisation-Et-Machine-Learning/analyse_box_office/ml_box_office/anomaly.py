"""Détection d'anomalies sur le Box Office avec Pipeline Scikit-Learn."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .preprocessing import FEATURE_COLUMNS


@dataclass(frozen=True)
class AnomalySummary:
    """Résumé chiffré de la détection d'anomalies."""

    total_movies: int
    anomaly_count: int
    normal_count: int
    contamination: float


def detect_box_office_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.05,
    n_estimators: int = 200,
    random_state: int = 42,
    features: List[str] = FEATURE_COLUMNS,
) -> Tuple[pd.DataFrame, pd.DataFrame, AnomalySummary]:
    """Applique SimpleImputer + StandardScaler + IsolationForest sur les métriques Box Office."""
    if not (0.0 < contamination <= 0.5):
        raise ValueError("Le taux de contamination doit être compris entre 0 et 0.5.")

    X = df[features]

    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "model",
                IsolationForest(
                    n_estimators=n_estimators,
                    contamination=contamination,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    labels = pipeline.fit_predict(X)
    scores = pipeline.decision_function(X)

    result = df.copy()
    result["anomaly_label"] = labels
    result["is_anomaly"] = labels == -1
    result["anomaly_score"] = scores

    anomalies = result[result["is_anomaly"]].sort_values("anomaly_score", ascending=True)
    summary = AnomalySummary(
        total_movies=len(result),
        anomaly_count=len(anomalies),
        normal_count=len(result) - len(anomalies),
        contamination=contamination,
    )
    return result, anomalies, summary


def export_anomalies(anomalies: pd.DataFrame, output_csv: Path) -> Path:
    """Exporte les films atypiques triés par score d'anomalie."""
    path = Path(output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)

    preferred_cols = [
        "Rank",
        "Release Group",
        "Year",
        "Genres",
        "$Worldwide",
        "$Domestic",
        "$Foreign",
        "Vote_Count",
        "Rating",
        "anomaly_score",
    ]
    cols = [c for c in preferred_cols if c in anomalies.columns]
    anomalies[cols].to_csv(path, index=False, encoding="utf-8")
    return path
