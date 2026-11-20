"""Point d'entrée principal de l'application d'inventaire (GUI ou CLI)."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import time

from inventory_app.inventory import format_text_report, generate_reports
from inventory_app.mailer import SmtpConfig, send_inventory_email
from inventory_app.scheduler import DailyScheduler
from inventory_app.ui import launch_gui


BASE_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gestion d'inventaire, génération de rapports et envoi Gmail/SMTP."
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Exécute l'analyse CSV en ligne de commande sans ouvrir l'interface.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=BASE_DIR / "inventaire.csv",
        help="Chemin vers le fichier CSV d'inventaire.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Envoie le rapport par e-mail (utilise EMAIL_EXPEDITEUR, EMAIL_DESTINATAIRE, EMAIL_PASSWORD).",
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default=None,
        help="Planifie un envoi quotidien en mode CLI (format HH:MM, ex: 08:00).",
    )
    return parser.parse_args()


def run_cli_once(csv_path: Path, send: bool) -> None:
    alerts_path = BASE_DIR / "produits_alertes.csv"
    rapport_path = BASE_DIR / "rapport.txt"
    report, _, _ = generate_reports(csv_path, alerts_path, rapport_path)
    print(format_text_report(report))

    if send:
        config = SmtpConfig(
            sender=os.environ.get("EMAIL_EXPEDITEUR", ""),
            recipient=os.environ.get("EMAIL_DESTINATAIRE", ""),
            password=os.environ.get("EMAIL_PASSWORD", ""),
            host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
            port=int(os.environ.get("SMTP_PORT", "587")),
        )
        send_inventory_email(
            config=config,
            report=report,
            attachments=[rapport_path, alerts_path],
        )
        print(f"E-mail envoyé avec succès à {config.recipient}.")


def main() -> None:
    args = parse_args()
    if args.schedule:
        scheduler = DailyScheduler(lambda: run_cli_once(args.csv, send=True))
        next_run = scheduler.start(args.schedule)
        print(f"Planificateur actif. Prochain envoi : {next_run:%d/%m/%Y %H:%M}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nArrêt du planificateur.")
    elif args.cli or args.send:
        run_cli_once(args.csv, send=args.send)
    else:
        launch_gui(BASE_DIR)


if __name__ == "__main__":
    main()
