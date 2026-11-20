# 🏭 Projet M1 : Usine 5.0 & Maquette de Tri Automatisé - Siemens S7-1200 & Node-RED

Projet mécatronique complet d'automatisation industrielle (**Industrie 5.0**) portant sur la conception mécanique, le câblage, la programmation et la supervision d'une **maquette de tri automatisé de roues de skateboard par couleur**.

---

## 🎯 Objectifs & Réalisations Clés
- **Tri industriel automatisé :** Reconnaissance optique temps réel de roues selon leur couleur (rouge, bleu, vert, etc.) et orientation dynamique vers les goulottes dédiées.
- **Automatisme & Logique séquentielle :** Programmation de l'automate industriel **Siemens S7-1200** sous **Siemens TIA Portal V15**.
- **Protocole IO-Link :** Intégration et paramétrage d'un capteur de couleur industriel haute précision **Allen-Bradley 45CRM** via un module maître IO-Link **Siemens SM 1278**.
- **Actionnement de puissance :** Commande d'un moteur pas-à-pas via son driver **DM542** pour le positionnement précis du mécanisme d'aiguillage.
- **Supervision IIoT & IHM :** Création d'un tableau de bord interactif sous **Node-RED** communiquant directement avec l'automate Siemens (commandes Marche/Arrêt, visualisation d'état, comptage).
- **Traçabilité & Base de données :** Enregistrement des données de tri en temps réel dans une base de données relationnelle **MySQL** (PhpMyAdmin).
- **Conception & Fabrication mécanique :** Modélisation CAO 3D intégrale sous **Autodesk Inventor** et fabrication additive (impression 3D en **PLA+**).

---

## 🧩 Architecture Matérielle & Composants

| Rôle | Composant | Caractéristiques / Protocole |
| :--- | :--- | :--- |
| **Automate central (API)** | **Siemens SIMATIC S7-1200** | CPU 1215C DC/DC/DC (14 DI, 10 DQ, 2 AI, 2 AQ, PROFINET) |
| **Module de communication**| **Siemens SM 1278** | Maître 4 canaux **IO-Link** |
| **Capteur de couleur** | **Allen-Bradley 45CRM** | Capteur couleur industriel haute fidélité (liaison IO-Link) |
| **Driver Moteur** | **Leadshine DM542** | Driver pas-à-pas numérique microstepping |
| **Actionneur** | Moteur Pas-à-Pas bipolaire | Positionnement angulaire précis du plateau de tri |
| **Supervision / Cloud** | **Node-RED & MySQL** | Dashboard opérateur, commandes à distance et logs |

---

## 📂 Contenu du Répertoire

- **`docs/` :**
  - `Rapport_Maquette5_0_Tri_Siemens.pdf` : Rapport technique détaillé (45 pages) couvrant la gestion de projet, l'analyse fonctionnelle, les schémas de câblage, le protocole IO-Link, la programmation TIA Portal et l'interface Node-RED.
- **`programation_tia/` :** Projet **TIA Portal V15** (`Projet1.ap15_1`) prêt à être déployé sur CPU Siemens S7-1200.
- **`node_red/` :**
  - `flows.json` : Flux Node-RED complet (dashboard, nœuds S7 pour la communication automate, requêtes SQL).
- **`database/` :**
  - `tri_test.sql` : Script de création et structure de la base de données MySQL pour le logging des pièces.
- **`cad_inventor/` :** Modèles 3D paramétriques Autodesk Inventor (`.ipt`, `.ipj`) et fichiers `.stl` / `.stp` pour impression 3D (châssis, supports capteur, entonnoir, cales, têtes d'arbre).

---

## 🚀 Mise en Œuvre
1. **Automate :** Ouvrir le projet dans **Siemens TIA Portal V15**, compiler et charger dans la CPU 1215C via le port Ethernet PROFINET.
2. **Supervision :** Importer `node_red/flows.json` dans votre serveur **Node-RED** local pour accéder à l'interface de contrôle et de visualisation.
3. **Base de données :** Importer `database/tri_test.sql` sous MySQL / phpMyAdmin.
