"""Comparaison de classifieurs SVM (linéaire vs RBF) avec Pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


@dataclass
class SvmBenchmarkResult:
    """Résultats d'entraînement et d'évaluation pour un noyau SVM."""

    kernel: str
    accuracy: float
    report: str
    pipeline: Pipeline


def run_svm_comparison(
    n_samples: int = 300,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, SvmBenchmarkResult]]:
    """Entraîne et compare SVC(linear) et SVC(rbf) avec normalisation StandardScaler."""
    X, y = make_classification(
        n_samples=n_samples,
        n_features=2,
        n_informative=2,
        n_redundant=0,
        n_classes=2,
        random_state=random_state,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    results: Dict[str, SvmBenchmarkResult] = {}
    for kernel in ("linear", "rbf"):
        pipe = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("svm", SVC(kernel=kernel, random_state=random_state)),
            ]
        )
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        results[kernel] = SvmBenchmarkResult(
            kernel=kernel,
            accuracy=float(accuracy_score(y_test, y_pred)),
            report=classification_report(y_test, y_pred),
            pipeline=pipe,
        )

    return X, y, results
