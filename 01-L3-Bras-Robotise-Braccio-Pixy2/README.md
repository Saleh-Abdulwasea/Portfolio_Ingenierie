# 🤖 Projet L3 : Bras Robotisé 6 Axes & Vision par Ordinateur

Projet d'ingénierie mécatronique combinant un bras robotique polyarticulé (**TinkerKit Braccio**) et un capteur de vision intelligent (**Pixy2 / CMUcam5**) piloté par microcontrôleur Arduino.

---

## 🎯 Objectifs du Projet
Concevoir et programmer une cellule robotisée capable de :
1. Repérer et classifier des pièces cibles dans son espace de travail via des signatures colorimétriques.
2. Extraire en temps réel les coordonnées 2D $(X, Y)$ fournies par la caméra.
3. Calculer par géométrie/cinématique inverse les angles nécessaires pour chacun des 6 servomoteurs.
4. Effectuer une séquence autonome de saisie (Pick & Place) et de dépose vers une zone définie (tri sélectif).

---

## 🧩 Matériel & Outils
- **Bras robotique :** Arduino TinkerKit Braccio (6 servomoteurs : Base, Épaule, Coude, Poignet vertical, Poignet rotatif, Pince).
- **Capteur de vision :** Pixy2 CMUcam5 (Interface I2C/SPI/Série, cadence 60 fps).
- **Microcontrôleur :** Arduino Uno / Mega.
- **Environnement logiciel :** Arduino IDE, bibliothèque `Braccio.h`, bibliothèque `Pixy2.h`.

---

## 💻 Structure du Code (`src/`)
- `cam_bras_SM_244.ino` : Programme complet intégrant l'initialisation de la caméra Pixy2, la détection de blocs colorés, la conversion des coordonnées et l'actionnement du bras vers les cibles.
- `cam_action.ino` : Module de calcul géométrique des angles (`calcule_angles(X, Y)`) et communication avec la console série.
- `cam_AUTO.ino` : Mode de fonctionnement 100% autonome en boucle fermée.

---

## 📑 Documentation (`docs/`)
- `Rapport_Projet_Braccio.pdf` : Rapport technique complet (cinématique, dimensionnement, analyse des résultats).
