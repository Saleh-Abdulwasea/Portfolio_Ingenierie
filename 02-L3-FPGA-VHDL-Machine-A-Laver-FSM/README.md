# ⚡ Projet L3 : Conception Numérique FPGA & VHDL - Machine d'États FSM

Projet de conception numérique modélisant des systèmes séquentiels synchrones sous forme de **machines à états finis (FSM - Finite State Machine)** synthétisées et déployées sur FPGA **Intel Altera MAX 10** (carte **Terasic DE10-Lite**).

---

## 🎯 Objectifs & Fonctionnalités
- **Automatisation d'un cycle de lavage :** Modélisation d'une FSM à 5 états séquentiels : `ARRET`, `PRELAVAGE`, `LAVAGE`, `RINCAGE`, `ESSORAGE`.
- **Gestion des temporisations :** Intégration d'un diviseur d'horloge pour abaisser la fréquence du quartz de la carte (50 MHz) vers une cadence de 1 Hz pour cadencer les états et décomptes.
- **Affichage dynamique :** Décodage et restitution en temps réel des états et du temps restant sur l'afficheur 7 segments `HEX0`.
- **Mode prélavage optionnel :** Prise en compte de conditions de branchement conditionnel (avec ou sans prélavage) contrôlé par commutateur.

---

## 🏗️ Architecture Matérielle & Schéma Bloc Top-Level
L'architecture matérielle globale est interconnectée dans le schéma bloc Quartus [`hardware/schemaBlockmachineAlaver.bdf`](./hardware/schemaBlockmachineAlaver.bdf) :

1. **`Diviseur_horloge` :** Divise l'horloge système de 50 MHz (`CLK`) pour obtenir des tops d'horloge de 1 Hz.
2. **`compteur` :** Compteur synchrone modulo-N qui génère les signaux de fin de temporisation pour chaque phase.
3. **`machine_a_lavermm` :** Le cœur FSM synchrone qui pilote les transitions d'états et les sorties d'actionnement.
4. **`seven_seg` :** Décodeur BCD vers afficheur 7 segments (actif niveau bas).

---

## 📌 Brochage Matériel (Carte Terasic DE10-Lite - FPGA MAX 10 `10M50DAF484C6GES`)

Les assignations physiques définies dans [`hardware/TP4.qsf`](./hardware/TP4.qsf) sont les suivantes :

| Signal logique | Direction | Composant sur carte | Broche FPGA (Pinout) |
| :--- | :---: | :--- | :--- |
| **`CLK`** | Entrée | Oscillateur 50 MHz | `PIN_P11` |
| **`RESET`** | Entrée | Commutateur `SW0` | `PIN_C10` |
| **`MARCHE`** | Entrée | Commutateur `SW1` | `PIN_D12` |
| **`PRELAVAGE`**| Entrée | Commutateur `SW2` | `PIN_C12` |
| **`SEG[0]`** | Sortie | Afficheur `HEX0[0]` | `PIN_C14` |
| **`SEG[1]`** | Sortie | Afficheur `HEX0[1]` | `PIN_E15` |
| **`SEG[2]`** | Sortie | Afficheur `HEX0[2]` | `PIN_C15` |
| **`SEG[3]`** | Sortie | Afficheur `HEX0[3]` | `PIN_C16` |
| **`SEG[4]`** | Sortie | Afficheur `HEX0[4]` | `PIN_E16` |
| **`SEG[5]`** | Sortie | Afficheur `HEX0[5]` | `PIN_D17` |
| **`SEG[6]`** | Sortie | Afficheur `HEX0[6]` | `PIN_C17` |

---

## 📂 Contenu du Répertoire

- **`src/` :** Codes sources VHDL propres (encodés en UTF-8)
  - `machine_a_laver.vhd` : FSM principale du cycle de lavage.
  - `seven_seg.vhd` : Décodeur 7 segments.
  - `compteur.vhd` : Compteur synchrone paramétrable.
  - `Diviseur_horloge.vhd` : Diviseur de fréquence d'horloge.
  - `Distributeur_de_film.vhd` : Mini-projet additionnel (FSM distributeur automatique).
- **`hardware/` :** Fichiers de conception matérielle Quartus
  - `TP4.qpf` : Fichier projet Quartus Prime.
  - `TP4.qsf` : Assignations des broches et contraintes de timing.
  - `schemaBlockmachineAlaver.bdf` : Schéma de câblage visuel Top-Level.
  - `machine_a_lavermm.smf` : Diagramme d'état (State Machine Wizard).
  - `TP4.sof` : Bitstream de programmation (SRAM Object File) prêt à flasher.
  - `TP4.pin` : Rapport officiel d'assignation des broches.

---

## 🚀 Comment ouvrir et tester le projet
1. Ouvrir le projet dans **Intel Quartus Prime** (version 18.1 ou supérieure) :
   - Fichier $\rightarrow$ Ouvrir le projet $\rightarrow$ Sélectionner `hardware/TP4.qpf`.
2. Pour reprogrammer la carte **DE10-Lite** :
   - Brancher la carte en USB (`USB-Blaster`).
   - Ouvrir l'outil **Programmer** dans Quartus.
   - Sélectionner le fichier `hardware/TP4.sof` et cliquer sur **Start**.
