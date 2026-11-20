# Analyse Box Office & Détection d'Anomalies (ML)

Projet Machine Learning avec `scikit-learn` :
- **Détection d'anomalies** sur 5 000 films (2000–2024) via un `Pipeline` (`SimpleImputer` + `StandardScaler` + `IsolationForest`) avec extraction numérique de `Rating`, exclusion de `Rank`/`Year` des features, export des films atypiques et graphiques annotés.
- **Comparaison SVM** (`kernel='linear'` vs `kernel='rbf'`) avec `StandardScaler` et tracé côte à côte des frontières de décision.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Lancer l'interface graphique interactive (recommandé)
python3 main.py

# Mode ligne de commande (CLI)
python3 main.py --cli --contamination 0.03 --svm --no-show
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```
