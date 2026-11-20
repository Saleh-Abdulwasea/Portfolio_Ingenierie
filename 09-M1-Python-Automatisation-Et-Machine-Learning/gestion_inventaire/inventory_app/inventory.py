"""Lecture, analyse CSV et génération des rapports d'inventaire."""

from __future__ import annotations

import csv
import html
from pathlib import Path
from typing import Tuple

from .models import InventoryReport, Product, StockStatus


def load_inventory(csv_path: Path) -> InventoryReport:
    """Lit un fichier CSV d'inventaire et retourne un InventoryReport structuré."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Le fichier '{path}' est introuvable.")

    report = InventoryReport()

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if header is None:
            raise ValueError("Le fichier CSV est vide.")

        for line_num, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) < 3:
                report.errors.append(
                    f"Ligne {line_num} ignorée (colonnes manquantes) : {row}"
                )
                continue

            name = row[0].strip()
            if not name:
                report.errors.append(f"Ligne {line_num} ignorée (nom de produit vide).")
                continue

            try:
                quantity = int(row[1].strip())
                threshold = int(row[2].strip())
            except ValueError:
                report.errors.append(
                    f"Ligne {line_num} ignorée (valeurs numériques invalides) : {row}"
                )
                continue

            report.products.append(
                Product(name=name, quantity=quantity, threshold=threshold)
            )

    return report


def save_alerts_csv(report: InventoryReport, output_path: Path) -> Path:
    """Enregistre la liste des produits en alerte dans un fichier CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Produit", "Quantité", "Seuil Critique", "Statut"])
        for product in report.alerts:
            writer.writerow(
                [product.name, product.quantity, product.threshold, product.status.value]
            )
    return path


def format_text_report(report: InventoryReport) -> str:
    """Formate le rapport d'inventaire en texte brut lisible."""
    timestamp = report.generated_at.strftime("%d/%m/%Y à %H:%M")
    lines = [
        f"Rapport d'inventaire ({timestamp})",
        "=" * 42,
        f"Total produits : {len(report.products)} | "
        f"En stock : {len(report.in_stock)} | "
        f"En alerte : {len(report.alerts)} (dont {len(report.out_of_stock)} rupture(s))",
        "",
        "Produits en alerte :",
        "-" * 20,
    ]

    if report.alerts:
        for p in report.alerts:
            tag = "[RUPTURE]" if p.status == StockStatus.RUPTURE else "[ALERTE] "
            lines.append(
                f"- {tag} {p.name} : {p.quantity} unité(s) (Seuil : {p.threshold})"
            )
    else:
        lines.append("Aucun produit en alerte.")

    lines.extend(["", "Produits en stock :", "-" * 19])
    if report.in_stock:
        for p in report.in_stock:
            lines.append(f"- {p.name} : {p.quantity} unité(s) (Seuil : {p.threshold})")
    else:
        lines.append("Aucun produit au-dessus du seuil.")

    if report.errors:
        lines.extend(["", "Avertissements de lecture :", "-" * 27])
        lines.extend(f"- {err}" for err in report.errors)

    return "\n".join(lines) + "\n"


def format_html_report(report: InventoryReport) -> str:
    """Génère une version HTML soignée du rapport pour le corps de l'e-mail."""
    timestamp = report.generated_at.strftime("%d/%m/%Y à %H:%M")

    def row_html(product: Product) -> str:
        if product.status == StockStatus.RUPTURE:
            badge_bg, badge_fg = "#FEE2E2", "#991B1B"
        elif product.status == StockStatus.ALERTE:
            badge_bg, badge_fg = "#FEF3C7", "#92400E"
        else:
            badge_bg, badge_fg = "#DCFCE7", "#166534"

        return (
            "<tr>"
            f"<td style='padding:10px 12px;border-bottom:1px solid #E5E7EB;'>{html.escape(product.name)}</td>"
            f"<td style='padding:10px 12px;border-bottom:1px solid #E5E7EB;text-align:right;font-weight:600;'>{product.quantity}</td>"
            f"<td style='padding:10px 12px;border-bottom:1px solid #E5E7EB;text-align:right;'>{product.threshold}</td>"
            f"<td style='padding:10px 12px;border-bottom:1px solid #E5E7EB;text-align:center;'>"
            f"<span style='background:{badge_bg};color:{badge_fg};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;'>"
            f"{html.escape(product.status.value)}</span></td>"
            "</tr>"
        )

    rows = "\n".join(row_html(p) for p in report.products)
    return f"""<!DOCTYPE html>
<html lang="fr">
<body style="font-family:Arial,Helvetica,sans-serif;background:#F3F4F6;margin:0;padding:24px;color:#111827;">
  <div style="max-width:640px;margin:0 auto;background:#FFFFFF;border-radius:10px;overflow:hidden;border:1px solid #E5E7EB;">
    <div style="background:#1E293B;color:#FFFFFF;padding:20px 24px;">
      <h2 style="margin:0;font-size:20px;">Rapport d'inventaire</h2>
      <p style="margin:6px 0 0;color:#CBD5E1;font-size:13px;">Généré le {html.escape(timestamp)}</p>
    </div>
    <div style="padding:20px 24px;">
      <p style="margin:0 0 16px;font-size:14px;color:#374151;">
        <strong>{len(report.products)}</strong> produit(s) analysé(s) —
        <span style="color:#B45309;font-weight:600;">{len(report.alerts)} alerte(s)</span>
        (dont <span style="color:#B91C1C;font-weight:600;">{len(report.out_of_stock)} rupture(s)</span>).
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead>
          <tr style="background:#F8FAFC;text-align:left;">
            <th style="padding:10px 12px;border-bottom:2px solid #E5E7EB;">Produit</th>
            <th style="padding:10px 12px;border-bottom:2px solid #E5E7EB;text-align:right;">Quantité</th>
            <th style="padding:10px 12px;border-bottom:2px solid #E5E7EB;text-align:right;">Seuil</th>
            <th style="padding:10px 12px;border-bottom:2px solid #E5E7EB;text-align:center;">Statut</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
      <p style="margin:20px 0 0;font-size:12px;color:#6B7280;">
        Les fichiers détaillés (<code>rapport.txt</code> et <code>produits_alertes.csv</code>) sont joints à cet e-mail.
      </p>
    </div>
  </div>
</body>
</html>
"""


def save_text_report(report: InventoryReport, rapport_path: Path) -> Path:
    """Écrit le rapport texte sur le disque."""
    path = Path(rapport_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_text_report(report), encoding="utf-8")
    return path


def analyze_inventory(csv_path: Path) -> InventoryReport:
    """Alias explicite pour charger et analyser un fichier d'inventaire."""
    return load_inventory(csv_path)


def generate_reports(
    csv_path: Path,
    alerts_csv_path: Path,
    rapport_txt_path: Path,
) -> Tuple[InventoryReport, Path, Path]:
    """Charge l'inventaire et génère les deux fichiers de sortie."""
    report = load_inventory(csv_path)
    alerts_path = save_alerts_csv(report, alerts_csv_path)
    txt_path = save_text_report(report, rapport_txt_path)
    return report, alerts_path, txt_path
