# 🐍 Projet M1 : Automatisation Python & Détection d'Anomalies Machine Learning

Suite logicielle en **Python** développée en **Master 1**, regroupant deux applications complémentaires orientées **automatisation industrielle / gestion** et **Data Science / Machine Learning** avec interfaces graphiques dédiées (`Tkinter` / `ttk` & `Matplotlib`).

---

## 🎯 Vue d'ensemble des 2 Modules

### 1. 📦 Gestion d'Inventaire & Reporting Automatisé ([`gestion_inventaire/`](./gestion_inventaire))
Application de suivi de stocks et d'alertes critiques, sans aucune dépendance externe (bibliothèque standard Python uniquement) :
- **Analyse CSV robuste :** Lecture, validation des lignes et classification automatique (`En stock`, `Alerte`, `Rupture`).
- **Génération de rapports :** Export automatique vers `produits_alertes.csv`, `rapport.txt` et mise en forme **HTML** pour e-mail.
- **Envoi SMTP (Gmail / Unistra / Personnalisé) :** Envoi asynchrone (non bloquant) avec pièces jointes et support des mots de passe d'application Gmail.
- **Planificateur quotidien intégré :** Envoi automatique récurrent à l'heure choisie (`threading.Timer`).
- **Interface graphique & CLI :** Dashboard `ttk` avec cartes KPI, tableau filtrable (testé sur 5 000 produits), et mode terminal (`--cli`, `--send`, `--schedule`).

### 2. 🎬 Analyse Box Office & Détection d'Anomalies ML ([`analyse_box_office/`](./analyse_box_office))
Application d'exploration et de détection d'anomalies sur un jeu de données réel de **5 000 films (2000–2024)** avec `scikit-learn` :
- **Prétraitement & Feature Engineering :** Extraction numérique des notes (`Rating_Num`), imputation médiane (`SimpleImputer`) et standardisation (`StandardScaler`) via `Pipeline`.
- **Détection d'anomalies (`Isolation Forest`) :** Calcul des scores d'anomalie (`decision_function`), classement et export des films atypiques (`anomalies_box_office.csv`).
- **Comparaison SVM (`Linear` vs `RBF`) :** Évaluation comparative de classifieurs à noyau et tracé des frontières de décision.
- **Dashboard interactif (`Tkinter` + `Matplotlib`) :** Curseur de réglage en direct du taux de contamination, sélecteur d'axes (échelle `symlog`), explorateur de films et onglet comparatif SVM.

---

## 📂 Contenu du Répertoire

- **`gestion_inventaire/`**
  - `main.py` : Point d'entrée (GUI par défaut ou CLI).
  - `inventory_app/` : Modules `models.py`, `inventory.py`, `mailer.py`, `scheduler.py`, `ui.py`.
  - `inventaire.csv` & `inventaire_test_5000.csv` : Jeux de données source et de charge (5 000 lignes).
  - `tests/` : Tests unitaires (`unittest`).
- **`analyse_box_office/`**
  - `main.py` : Point d'entrée (Dashboard interactif ou CLI `--cli --svm`).
  - `ml_box_office/` : Modules `preprocessing.py`, `anomaly.py`, `classification.py`, `visualization.py`, `ui.py`.
  - `data/box_office_2000_2024.csv` : Jeu de données Box Office (5 000 films).
  - `requirements.txt` & `tests/` : Dépendances (`numpy`, `pandas`, `scikit-learn`, `matplotlib`) et tests unitaires.

---

## 🚀 Mise en Œuvre Rapide

### Module 1 — Gestion d'Inventaire (aucune installation requise)
```bash
cd gestion_inventaire
python3 main.py
# Tests unitaires :
python3 -m unittest discover -s tests -v
```

### Module 2 — Analyse Box Office ML
```bash
cd analyse_box_office
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
