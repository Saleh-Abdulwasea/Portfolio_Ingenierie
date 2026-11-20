"""Envoi d'e-mails SMTP (Gmail par défaut, Unistra ou serveur personnalisé)."""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
import smtplib
from typing import Dict, Iterable, Optional, Tuple

from .inventory import format_html_report, format_text_report
from .models import InventoryReport


SMTP_PRESETS: Dict[str, Tuple[str, int]] = {
    "Gmail (smtp.gmail.com)": ("smtp.gmail.com", 587),
    "Unistra (partage.unistra.fr)": ("partage.unistra.fr", 587),
    "Personnalisé": ("", 587),
}


@dataclass(frozen=True)
class SmtpConfig:
    """Configuration d'envoi SMTP."""

    sender: str
    recipient: str
    password: str
    host: str = "smtp.gmail.com"
    port: int = 587
    use_ssl: bool = False
    timeout: int = 20


def build_inventory_email(
    config: SmtpConfig,
    report: Optional[InventoryReport] = None,
    attachments: Iterable[Path] = (),
    subject: Optional[str] = None,
) -> EmailMessage:
    """Construit un EmailMessage avec corps texte/HTML et pièces jointes."""
    msg = EmailMessage()
    alert_count = len(report.alerts) if report is not None else 0
    default_subject = (
        f"Rapport d'inventaire — {alert_count} alerte(s)"
        if report is not None
        else "Rapport d'inventaire"
    )
    msg["Subject"] = subject or default_subject
    msg["From"] = config.sender
    msg["To"] = config.recipient

    if report is not None:
        text_body = (
            "Bonjour,\n\n"
            "Veuillez trouver ci-dessous et en pièce jointe le rapport d'inventaire mis à jour.\n\n"
            f"{format_text_report(report)}\n"
            "Cordialement,\nL'équipe M1-MESI"
        )
        msg.set_content(text_body)
        msg.add_alternative(format_html_report(report), subtype="html")
    else:
        msg.set_content(
            "Bonjour,\n\n"
            "Vous trouverez ci-joint le rapport d'inventaire mis à jour.\n\n"
            "Cordialement,\nL'équipe M1-MESI"
        )

    for file_path in attachments:
        path = Path(file_path)
        if not path.is_file():
            continue
        maintype, subtype = (
            ("text", "csv")
            if path.suffix.lower() == ".csv"
            else ("text", "plain")
            if path.suffix.lower() == ".txt"
            else ("application", "octet-stream")
        )
        msg.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    return msg


def send_inventory_email(
    config: SmtpConfig,
    report: Optional[InventoryReport] = None,
    attachments: Iterable[Path] = (),
    subject: Optional[str] = None,
) -> None:
    """Envoie l'e-mail via SMTP avec gestion claire des erreurs."""
    if not config.sender or not config.recipient or not config.password:
        raise ValueError("Expéditeur, destinataire et mot de passe sont obligatoires.")
    if not config.host:
        raise ValueError("L'adresse du serveur SMTP est obligatoire.")

    msg = build_inventory_email(
        config=config,
        report=report,
        attachments=attachments,
        subject=subject,
    )

    try:
        if config.use_ssl or config.port == 465:
            with smtplib.SMTP_SSL(config.host, config.port, timeout=config.timeout) as smtp:
                smtp.login(config.sender, config.password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(config.host, config.port, timeout=config.timeout) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(config.sender, config.password)
                smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        if "gmail" in config.host.lower():
            raise RuntimeError(
                "Échec d'authentification Gmail. Utilisez un « Mot de passe d'application » "
                "Google (Compte Google > Sécurité > Validation en 2 étapes > Mots de passe des applications), "
                "et non votre mot de passe habituel."
            ) from exc
        raise RuntimeError(f"Échec d'authentification SMTP : {exc}") from exc
