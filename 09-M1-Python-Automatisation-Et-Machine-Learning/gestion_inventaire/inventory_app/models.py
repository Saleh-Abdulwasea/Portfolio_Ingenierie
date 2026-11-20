"""Modèles de données pour la gestion d'inventaire."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class StockStatus(str, Enum):
    """État du stock d'un produit."""

    RUPTURE = "Rupture"
    ALERTE = "Alerte"
    OK = "En stock"


@dataclass(frozen=True)
class Product:
    """Représente un produit de l'inventaire."""

    name: str
    quantity: int
    threshold: int

    @property
    def status(self) -> StockStatus:
        """Retourne l'état du stock par rapport au seuil critique."""
        if self.quantity <= 0:
            return StockStatus.RUPTURE
        if self.quantity <= self.threshold:
            return StockStatus.ALERTE
        return StockStatus.OK

    @property
    def is_alert(self) -> bool:
        """Indique si le produit nécessite une surveillance."""
        return self.quantity <= self.threshold


@dataclass
class InventoryReport:
    """Résultat complet de l'analyse d'un fichier d'inventaire."""

    products: List[Product] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def alerts(self) -> List[Product]:
        """Produits en rupture ou sous le seuil critique."""
        return [p for p in self.products if p.is_alert]

    @property
    def in_stock(self) -> List[Product]:
        """Produits dont la quantité est supérieure au seuil critique."""
        return [p for p in self.products if not p.is_alert]

    @property
    def out_of_stock(self) -> List[Product]:
        """Produits en rupture totale (quantité <= 0)."""
        return [p for p in self.products if p.status == StockStatus.RUPTURE]
