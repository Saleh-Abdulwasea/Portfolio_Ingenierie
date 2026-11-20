"""Package d'analyse Box Office et détection d'anomalies ML."""

from .anomaly import detect_box_office_anomalies, export_anomalies
from .preprocessing import FEATURE_COLUMNS, load_and_clean_box_office, parse_rating

__all__ = [
    "FEATURE_COLUMNS",
    "detect_box_office_anomalies",
    "export_anomalies",
    "load_and_clean_box_office",
    "parse_rating",
]
