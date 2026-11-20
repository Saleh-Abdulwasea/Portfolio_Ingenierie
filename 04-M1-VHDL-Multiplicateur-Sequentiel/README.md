# 📐 Projet M1 : Multiplicateur Binaire Séquentiel en VHDL (Datapath + FSM)

Conception matérielle complète au niveau RTL (Register-Transfer Level) d'un multiplicateur binaire séquentiel par additions et décalages successifs.

---

## 🏗️ Architecture du Système
Le multiplicateur repose sur la décomposition classique en deux blocs fondamentaux :
1. **L'Unité Opérative (Datapath) :**
   - Registre à décalage pour le multiplicande (`Multiplicand.vhd`).
   - Registre accumulateur pour le produit partiel (`Produit.vhd`).
   - Additionneur binaire (`Addit.vhd`).
   - Portes logiques de conditionnement (`Porte_and.vhd`).
2. **L'Unité de Commande (Control Unit / FSM) :**
   - Machine à états finis (`FSM.vhd`) orchestrant la séquence : chargement, test du bit de poids faible, commande d'addition, décalage et émission du signal de fin de calcul.

---

## 💻 Fichiers Sources (`src/`)
- `multiplicateur.vhd` : Top-level structurel interconnectant l'unité de contrôle et le datapath.
- `FSM.vhd` : Contrôleur séquentiel d'états.
- `Addit.vhd`, `Multiplicand.vhd`, `Produit.vhd`, `Porte_and.vhd` : Composants matériels du chemin de données.

---

## 🔬 Simulations & Validation (`sim/`)
- `Simulation_ModelSim_1.png` & `Simulation_ModelSim_2.png` : Chronogrammes de simulation fonctionnelle démontrant l'exactitude des calculs sur plusieurs jeux de données binaires.
- `Synthese_RTL.png` : Schéma logique RTL généré par le synthétiseur Quartus Prime.
