# Gestion d'Inventaire & Alertes

Application de gestion d'inventaire avec une architecture modulaire, zéro dépendance externe, envoi de rapports par **Gmail** (ou Unistra / SMTP personnalisé) et interface graphique `tkinter`.

## Structure du projet

```text
gestion_inventaire/
├── main.py                     # Point d'entrée (GUI par défaut, ou CLI avec --cli / --send / --schedule)
├── inventaire.csv              # Données d'inventaire source
├── inventaire_test_5000.csv    # Jeu de données de test (5 000 produits)
├── inventory_app/
│   ├── models.py               # Modèles Product, StockStatus, InventoryReport
│   ├── inventory.py            # Lecture CSV robuste + génération rapport.txt, produits_alertes.csv et HTML
│   ├── mailer.py               # Envoi SMTP (Gmail par défaut, Unistra, personnalisé)
│   ├── scheduler.py            # Planificateur quotidien (bibliothèque standard)
│   └── ui.py                   # Interface graphique ttk (KPIs, tableau filtrable, envoi asynchrone)
└── tests/
    └── test_inventory.py       # Tests unitaires (unittest)
```

## Lancer l'application

### Interface graphique
```bash
python3 main.py
```

### Ligne de commande (CLI)
```bash
python3 main.py --cli
```

Pour envoyer aussi par e-mail (ou planifier à `08:00`) :
```bash
export EMAIL_EXPEDITEUR="ton.adresse@gmail.com"
export EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"
export EMAIL_DESTINATAIRE="destinataire@exemple.com"
python3 main.py --send
# ou en tâche quotidienne :
python3 main.py --schedule 08:00
```

## Configurer Gmail (important)

Google n'accepte plus le mot de passe classique du compte pour les connexions SMTP. Il faut créer un **Mot de passe d'application** :
1. Activer la **Validation en 2 étapes** sur votre compte Google.
2. Aller dans **Compte Google → Sécurité → Mots de passe des applications**.
3. Générer un mot de passe (16 caractères) pour « Mail » / « Autre » et l'utiliser dans le champ *Mot de passe d'application* de l'interface (ou dans `EMAIL_PASSWORD`).

## Lancer les tests

```bash
python3 -m unittest discover -s tests -v
```
