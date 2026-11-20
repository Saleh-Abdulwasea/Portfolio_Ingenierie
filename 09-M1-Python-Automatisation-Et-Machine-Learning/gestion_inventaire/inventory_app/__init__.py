"""Package de gestion d'inventaire, génération de rapports et envoi d'e-mails."""

from .models import InventoryReport, Product, StockStatus
from .inventory import analyze_inventory, generate_reports
from .mailer import SMTP_PRESETS, SmtpConfig, send_inventory_email
from .scheduler import DailyScheduler

__all__ = [
    "DailyScheduler",
    "InventoryReport",
    "Product",
    "SMTP_PRESETS",
    "SmtpConfig",
    "StockStatus",
    "analyze_inventory",
    "generate_reports",
    "send_inventory_email",
]
