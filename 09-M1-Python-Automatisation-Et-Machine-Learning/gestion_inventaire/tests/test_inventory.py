"""Tests unitaires pour le module d'inventaire, le mailer et le planificateur."""

from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from inventory_app.inventory import format_html_report, format_text_report, generate_reports, load_inventory
from inventory_app.mailer import SmtpConfig, build_inventory_email
from inventory_app.models import StockStatus
from inventory_app.scheduler import compute_next_run, parse_hhmm


class InventoryTests(unittest.TestCase):
    def test_load_inventory_and_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_file = Path(tmp) / "inv.csv"
            csv_file.write_text(
                "Produit,Quantité,Seuil_Critique\n"
                "Ordinateur,20,5\n"
                "Écran,0,1\n"
                "Disque Dur,3,5\n"
                "\n"
                "LigneInvalide,abc,2\n"
                "Incomplete,10\n",
                encoding="utf-8",
            )
            report = load_inventory(csv_file)

            self.assertEqual(len(report.products), 3)
            self.assertEqual(len(report.alerts), 2)
            self.assertEqual(len(report.out_of_stock), 1)
            self.assertEqual(len(report.in_stock), 1)
            self.assertEqual(len(report.errors), 2)
            self.assertEqual(report.products[1].status, StockStatus.RUPTURE)
            self.assertEqual(report.products[2].status, StockStatus.ALERTE)

    def test_generate_reports_and_email_building(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            csv_file = tmp_dir / "inv.csv"
            csv_file.write_text(
                "Produit,Quantité,Seuil_Critique\nSouris,10,2\nClavier,1,2\n",
                encoding="utf-8",
            )
            alerts_csv = tmp_dir / "alertes.csv"
            rapport_txt = tmp_dir / "rapport.txt"

            report, out_csv, out_txt = generate_reports(csv_file, alerts_csv, rapport_txt)
            self.assertTrue(out_csv.is_file())
            self.assertTrue(out_txt.is_file())
            self.assertIn("Clavier", format_text_report(report))
            self.assertIn("Clavier", format_html_report(report))

            msg = build_inventory_email(
                config=SmtpConfig(sender="a@gmail.com", recipient="b@gmail.com", password="secret"),
                report=report,
                attachments=[out_txt, out_csv],
            )
            self.assertEqual(msg["From"], "a@gmail.com")
            self.assertEqual(msg["To"], "b@gmail.com")
            self.assertIn("1 alerte(s)", msg["Subject"])
            attachments = [part.get_filename() for part in msg.iter_attachments()]
            self.assertEqual(attachments, ["rapport.txt", "alertes.csv"])

    def test_scheduler_time_calculation(self) -> None:
        self.assertEqual(parse_hhmm("08:30"), (8, 30))
        ref = datetime(2026, 11, 19, 10, 0)
        self.assertEqual(compute_next_run("14:15", now=ref), datetime(2026, 11, 19, 14, 15))
        self.assertEqual(compute_next_run("08:00", now=ref), datetime(2026, 11, 20, 8, 0))


if __name__ == "__main__":
    unittest.main()
