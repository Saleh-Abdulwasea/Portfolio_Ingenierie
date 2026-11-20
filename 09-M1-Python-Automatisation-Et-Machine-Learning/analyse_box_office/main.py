"""Point d'entrée principal du projet d'analyse Box Office & ML (GUI ou CLI)."""

from __future__ import annotations

import argparse
from pathlib import Path

from ml_box_office.anomaly import detect_box_office_anomalies, export_anomalies
from ml_box_office.classification import run_svm_comparison
from ml_box_office.preprocessing import load_and_clean_box_office
from ml_box_office.visualization import plot_box_office_anomalies, plot_svm_comparison


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = BASE_DIR / "data" / "box_office_2000_2024.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyse d'anomalies Box Office (Isolation Forest) et comparaison SVM."
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Exécute l'analyse en ligne de commande sans ouvrir l'interface graphique.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Chemin vers le CSV Box Office.",
    )
    parser.add_argument(
        "--contamination",
        type=float,
        default=0.05,
        help="Proportion estimée d'anomalies (défaut: 0.05).",
    )
    parser.add_argument(
        "--svm",
        action="store_true",
        help="Exécute aussi la comparaison SVM (linear vs rbf) en mode CLI.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Enregistre les graphiques sans ouvrir de fenêtre matplotlib (mode CLI).",
    )
    return parser.parse_args()


def run_cli(args: argparse.Namespace) -> None:
    show_plots = not args.no_show
    df = load_and_clean_box_office(args.csv)
    result_df, anomalies, summary = detect_box_office_anomalies(
        df, contamination=args.contamination
    )

    csv_out = export_anomalies(anomalies, OUTPUT_DIR / "anomalies_box_office.csv")
    img_out = plot_box_office_anomalies(
        result_df, OUTPUT_DIR / "box_office_anomalies.png", show=show_plots
    )

    print(
        f"Analyse terminée : {summary.total_movies} films | "
        f"{summary.anomaly_count} anomalies ({summary.contamination:.1%}) | "
        f"{summary.normal_count} normaux"
    )
    print("\nTop 10 des films les plus atypiques :")
    cols = [
        c
        for c in ("Release Group", "Year", "$Worldwide", "Vote_Count", "Rating", "anomaly_score")
        if c in anomalies.columns
    ]
    print(anomalies[cols].head(10).to_string(index=False))
    print(f"\nFichiers générés :\n- {csv_out}\n- {img_out}")

    if args.svm:
        X, y, svm_results = run_svm_comparison()
        for kernel, res in svm_results.items():
            print(f"\n--- SVM ({kernel}) — Précision : {res.accuracy:.2%} ---")
            print(res.report)
        svm_img = plot_svm_comparison(
            X, y, svm_results, OUTPUT_DIR / "svm_comparison.png", show=show_plots
        )
        print(f"- {svm_img}")


def main() -> None:
    args = parse_args()
    if args.cli or args.svm or args.no_show:
        run_cli(args)
    else:
        from ml_box_office.ui import launch_gui

        launch_gui(BASE_DIR)


if __name__ == "__main__":
    main()
