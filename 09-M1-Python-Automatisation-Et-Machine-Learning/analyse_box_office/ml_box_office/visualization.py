"""Génération des graphiques d'analyse (anomalies Box Office & frontières SVM)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .classification import SvmBenchmarkResult


def plot_box_office_anomalies(
    df: pd.DataFrame,
    output_path: Path,
    show: bool = True,
) -> Path:
    """Crée une figure à 2 panneaux : nuage de points log/linéaire + distribution des scores."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    normales = df[~df["is_anomaly"]]
    anomalies = df[df["is_anomaly"]].sort_values("anomaly_score", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8))

    # Panneau 1 : Recettes mondiales vs Nombre de votes
    ax1 = axes[0]
    ax1.scatter(
        normales["$Worldwide"],
        normales["Vote_Count"],
        alpha=0.45,
        s=18,
        c="#2563EB",
        label=f"Normaux ({len(normales)})",
    )
    ax1.scatter(
        anomalies["$Worldwide"],
        anomalies["Vote_Count"],
        alpha=0.85,
        s=32,
        c="#DC2626",
        label=f"Anomalies ({len(anomalies)})",
    )

    offsets = [(8, 8), (-95, 14), (-110, -14), (8, -12), (-95, -26)]
    for idx, (_, row) in enumerate(anomalies.head(5).iterrows()):
        title = str(row.get("Release Group", ""))[:22]
        dx, dy = offsets[idx % len(offsets)]
        ax1.annotate(
            title,
            (row["$Worldwide"], row["Vote_Count"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8,
            color="#991B1B",
            arrowprops={"arrowstyle": "-", "color": "#991B1B", "alpha": 0.5, "lw": 0.8},
        )

    ax1.set_xscale("symlog", linthresh=1e5)
    ax1.set_yscale("symlog", linthresh=10)
    ax1.set_xlabel("Recettes mondiales ($Worldwide, échelle symlog)")
    ax1.set_ylabel("Nombre de votes (Vote_Count, échelle symlog)")
    ax1.set_title("Détection d'anomalies Box Office (Isolation Forest)")
    ax1.legend()
    ax1.grid(alpha=0.25)

    # Panneau 2 : Distribution du score d'anomalie
    ax2 = axes[1]
    ax2.hist(normales["anomaly_score"], bins=35, alpha=0.75, color="#2563EB", label="Normaux")
    ax2.hist(anomalies["anomaly_score"], bins=20, alpha=0.85, color="#DC2626", label="Anomalies")
    ax2.axvline(0.0, color="#0F172A", linestyle="--", linewidth=1.3, label="Seuil (0.0)")
    ax2.set_xlabel("Score d'anomalie (decision_function)")
    ax2.set_ylabel("Nombre de films")
    ax2.set_title("Distribution des scores d'anomalie")
    ax2.legend()
    ax2.grid(alpha=0.25)

    plt.tight_layout()
    fig.savefig(path, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    return path


def plot_svm_comparison(
    X: np.ndarray,
    y: np.ndarray,
    results: Dict[str, SvmBenchmarkResult],
    output_path: Path,
    show: bool = True,
) -> Path:
    """Trace côte à côte les frontières de décision SVM linéaire et RBF."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    xx, yy = np.meshgrid(
        np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 160),
        np.linspace(X[:, 1].min() - 0.5, X[:, 1].max() + 0.5, 160),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]

    fig, axes = plt.subplots(1, len(results), figsize=(12, 5))
    if len(results) == 1:
        axes = [axes]

    for ax, (kernel, res) in zip(axes, results.items()):
        Z = res.pipeline.predict(grid).reshape(xx.shape)
        ax.contourf(xx, yy, Z, alpha=0.35, levels=[-0.5, 0.5, 1.5], colors=["#93C5FD", "#FCA5A5"])
        ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1D4ED8", s=22, label="Classe 0")
        ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#B91C1C", s=22, label="Classe 1")
        ax.set_title(f"SVC (kernel='{kernel}') — Précision : {res.accuracy:.1%}")
        ax.set_xlabel("Feature 1")
        ax.set_ylabel("Feature 2")
        ax.legend()
        ax.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(path, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    return path
