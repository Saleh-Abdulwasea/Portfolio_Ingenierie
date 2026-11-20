"""Tests unitaires pour le projet d'analyse Box Office."""

import importlib.util
from pathlib import Path
import unittest


HAS_ML_STACK = all(
    importlib.util.find_spec(pkg) is not None
    for pkg in ("numpy", "pandas", "sklearn", "matplotlib")
)


class BoxOfficeTests(unittest.TestCase):
    def test_dataset_exists(self) -> None:
        csv_path = Path(__file__).resolve().parent.parent / "data" / "box_office_2000_2024.csv"
        self.assertTrue(csv_path.is_file())

    @unittest.skipUnless(HAS_ML_STACK, "numpy/pandas/sklearn/matplotlib requis")
    def test_parse_rating_and_pipeline(self) -> None:
        from ml_box_office.anomaly import detect_box_office_anomalies
        from ml_box_office.preprocessing import load_and_clean_box_office, parse_rating

        self.assertAlmostEqual(parse_rating("6.126/10"), 6.126)
        self.assertIsNone(parse_rating("N/A"))

        csv_path = Path(__file__).resolve().parent.parent / "data" / "box_office_2000_2024.csv"
        df = load_and_clean_box_office(csv_path)
        result_df, anomalies, summary = detect_box_office_anomalies(df, contamination=0.05)

        self.assertEqual(summary.total_movies, len(df))
        self.assertGreater(summary.anomaly_count, 0)
        self.assertIn("anomaly_score", result_df.columns)
        self.assertTrue(anomalies["anomaly_score"].is_monotonic_increasing)


if __name__ == "__main__":
    unittest.main()
