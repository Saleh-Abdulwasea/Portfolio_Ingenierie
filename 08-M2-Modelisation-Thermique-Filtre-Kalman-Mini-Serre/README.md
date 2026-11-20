# Modélisation Thermique et Filtrage de Kalman d'une Mini-Serre

Projet de **Commande Avancée** portant sur la modélisation physique d'une mini-serre chauffée, la validation expérimentale en boucle ouverte et l'estimation d'état par **filtre de Kalman discret** sous MATLAB / Simulink.

---

## 🎯 Objectifs du projet

1. **Modéliser** le comportement thermique d'une mini-serre à partir des lois de transfert de chaleur (analogie thermique-électrique : résistances $R_{th}$ et capacités $C_{th}$).
2. **Valider** le modèle d'état continu à 5 états face à un modèle physique complet **Simscape** et aux **mesures expérimentales** réelles.
3. **Estimer et filtrer** les températures bruitées ($\theta_{RES}$ et $\theta_{BOX}$) à l'aide d'un **filtre de Kalman discret** :
   - D'abord avec le bloc intégré **`Kalman Filter`** de Simulink,
   - Ensuite avec une **implémentation manuelle** complète (prédiction, gain de Kalman, mise à jour de covariance sous forme de Joseph) dans un bloc **`MATLAB Function`**.

---

## 🧠 Modélisation d'état (5 états)

Le système est modélisé sous la forme d'état continue :

$$\dot{x}(t) = A\,x(t) + B\,u(t) + E\,T_{\text{amb}}(t)$$

- **Vecteur d'état** ($5\times 1$) :
  $$x = \begin{bmatrix} \theta_{\text{RES}} & \theta_{\text{ALU}} & \theta_{\text{BOX}} & \theta_{\text{SEN}} & \theta_{\text{FAN}} \end{bmatrix}^T$$
  *(Températures de la résistance chauffante, du bloc aluminium, de l'air intérieur, du capteur aluminium et du ventilateur, en °C).*
- **Entrées** :
  - $u = P = U \cdot I$ : puissance de chauffe injectée ($6\text{ V} \times 0.57\text{ A} = 3.42\text{ W}$),
  - $T_{\text{amb}}$ : température ambiante extérieure ($\approx 21.5\text{ °C}$).
- **Mesures** : $\theta_{\text{RES}}$ et $\theta_{\text{BOX}}$ (échantillonnées à $T_s = 1\text{ s}$).

---

## 📁 Structure du projet

| Fichier | Rôle |
| :--- | :--- |
| `model.m` | Paramètres physiques ($R_{th}$, $C_{th}$) et matrices d'état continues $(A, B, E, C, D)$ |
| `estimate_R.m` | Estimation des écarts-types du bruit capteur ($\sigma_{\text{RES}} \approx 0.496\text{ °C}$, $\sigma_{\text{BOX}} \approx 0.579\text{ °C}$) et de la matrice $R$ à partir des logs |
| `model_file.m` & `model_file_sim1.slx` | **Partie 1** — Validation en boucle ouverte : Mesures réelles vs Simscape vs Modèle d'état $(A, B, E)$ |
| `kalman_simulink.m` & `kalman_simulink_sim.slx` | **Partie 2** — Estimation par le bloc `Kalman Filter` intégré de Simulink (2 mesures) |
| `kalman_manuel.m` & `kalman_manuel_sim.slx` | **Partie 3** — Modèle d'état discrétisé en blocs Simulink + filtre de Kalman manuel (2 mesures, forme de Joseph) |
| `table_*.dat` | Relevés expérimentaux de chauffe et refroidissement de la mini-serre |

---

## ▶️ Exécution

1. Ouvrir MATLAB dans le dossier `08-M2-Modelisation-Thermique-Filtre-Kalman-Mini-Serre`.
2. Lancer au choix :
   - `model_file` $\rightarrow$ validation du modèle thermique en boucle ouverte.
   - `kalman_simulink` $\rightarrow$ filtre de Kalman intégré Simulink.
   - `kalman_manuel` $\rightarrow$ modèle discret Simulink + filtre de Kalman manuel.

### Créer / ouvrir en tant que Projet MATLAB (`.prj`)
Pour convertir ce dossier en **Projet MATLAB** natif :
1. Dans MATLAB, aller dans **Home $\rightarrow$ New $\rightarrow$ Project $\rightarrow$ From Folder** (ou exécuter `matlab.project.createProject(pwd)` dans la Command Window).
2. Sélectionner le dossier `08-M2-Modelisation-Thermique-Filtre-Kalman-Mini-Serre`. MATLAB générera automatiquement le fichier `.prj` et le dossier `resources/project/`.

---

## 💡 Principaux enseignements

- **Modèle complet vs modèle réduit** : le schéma Simscape intègre toutes les capacités et demi-résistances physiques, tandis que le modèle d'état réduit à 5 états néglige la capacité des parois PET ($C_{th,\text{pet}}$) tout en conservant le bilan énergétique exact ($A \cdot \mathbf{1} + E = \mathbf{0}$).
- **Cohérence relatif / absolu** : lorsqu'on travaille en température relative ($\Delta\theta = \theta - T_{\text{amb}}$) dans le filtre de Kalman manuel, il est essentiel de soustraire $T_{\text{amb}}$ de la mesure dans l'innovation avant d'ajouter $T_{\text{amb}}$ en sortie.
- **Stabilité numérique** : l'utilisation de la **forme de Joseph** $P = (I - KC)P(I - KC)^T + KRK^T$ garantit la symétrie et la positivité de la matrice de covariance $P$.
- **Filtrage multi-capteurs** : l'intégration simultanée des deux mesures ($\theta_{\text{RES}}$ et $\theta_{\text{BOX}}$) avec une matrice $R$ diagonale calibrée sur les logs réduit efficacement le bruit de mesure tout en suivant fidèlement la dynamique thermique réelle.
