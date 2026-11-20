%% ========================================================================
%  KALMAN_SIMULINK.M — Partie 2 : Filtre de Kalman intégré Simulink
% =========================================================================
%  Discrétise le modèle continu (A, B, E) de model.m (ZOH) et exécute
%  le bloc Kalman Filter intégré dans kalman_simulink_sim.slx.
% =========================================================================
clear; clc; close all;

%% 1. Chargement du modèle continu et des mesures expérimentales
run("model.m");

tempRes = readmatrix('table_TempUpRes_6V570mA.dat');   % Mesure résistance [°C]
tempBox = readmatrix('table_TempUpBox_6V570mA.dat');   % Mesure air serre  [°C]

Ts = 1;                                 % Période d'échantillonnage [s]
N  = length(tempRes(2, :));
t  = (0:N-1)' * Ts;                     % Vecteur temps [s]

% Entrées connues : puissance u [W] et température ambiante v [°C]
u    = (0.57 * 6) * ones(N, 1);
Tamb = tempBox(2, 1);
v    = Tamb * ones(N, 1);

%% 2. Discrétisation ZOH du modèle à 2 entrées [u ; v]
C_meas = [1 0 0 0 0;                    % Mesure 1 : theta_RES
          0 0 1 0 0];                   % Mesure 2 : theta_BOX
D_meas = zeros(2, 2);

sysc = ss(A, [B E], C_meas, D_meas);
sysd = c2d(sysc, Ts, 'zoh');

Ad   = sysd.A;
Bd   = sysd.B(:, 1);                    % Entrée commande u (puissance)
Gd   = sysd.B(:, 2);                    % Entrée perturbation v (Tamb)
Bkal = [Bd Gd];                         % Matrice d'entrée complète (5x2)
Cd   = sysd.C;
Dd   = D_meas;

%% 3. Paramètres du filtre de Kalman (Q, R, état initial)
Q     = 1e-3 * eye(5);                  % Covariance du bruit de modèle
R     = diag([0.4956^2, 0.5792^2]);     % Covariance du bruit de mesure (estimate_R.m)
x0    = Tamb * ones(5, 1);
xhat0 = Tamb * ones(5, 1);

% Signaux d'entrée pour Simulink (From Workspace : [temps, valeurs])
y_meas = [tempRes(2, :)', tempBox(2, :)'];
U_in   = [t, u];
V_in   = [t, v];
Y_in   = [t, y_meas];

%% 4. Simulation Simulink (kalman_simulink_sim.slx)
modelName = 'kalman_simulink_sim.slx';
simOut = sim(modelName, ...
    'StopTime', num2str(t(end)), ...
    'ReturnWorkspaceOutputs', 'on');

if isprop(simOut, 'yhat_ts')
    yhat_ts = simOut.yhat_ts;
else
    error('Le bloc To Workspace doit exporter la variable "yhat_ts" (Timeseries).');
end

%% 5. Extraction et métriques (RMSE)
t_hat = yhat_ts.Time(:);
Yhat  = yhat_ts.Data;
L     = min(length(t_hat), length(t));

t_plt = t_hat(1:L);
Yhat  = Yhat(1:L, :);
Ymeas = y_meas(1:L, :);

rmse_res = sqrt(mean((Yhat(:, 1) - Ymeas(:, 1)).^2));
rmse_box = sqrt(mean((Yhat(:, 2) - Ymeas(:, 2)).^2));

%% 6. Mise en forme des figures (qualité rapport)
figure('Color', 'w', 'Position', [100, 100, 950, 620], ...
       'Name', 'Filtre de Kalman intégré Simulink');

subplot(2, 1, 1);
plot(t_plt, Ymeas(:, 1), 'Color', [0.35 0.35 0.35], 'LineWidth', 1.0); hold on;
plot(t_plt, Yhat(:, 1),  'r-', 'LineWidth', 1.8);
grid on; box on; set(gca, 'FontSize', 10);
xlabel('Temps (s)', 'FontSize', 11);
ylabel('Température (°C)', 'FontSize', 11);
title(sprintf('Résistance chauffante (\\theta_{RES}) — RMSE : %.3f °C', rmse_res), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend('Mesure bruitée', 'Estimation Kalman (Simulink)', ...
       'Location', 'southeast', 'FontSize', 9.5);

subplot(2, 1, 2);
plot(t_plt, Ymeas(:, 2), 'Color', [0.35 0.35 0.35], 'LineWidth', 1.0); hold on;
plot(t_plt, Yhat(:, 2),  'b-', 'LineWidth', 1.8);
grid on; box on; set(gca, 'FontSize', 10);
xlabel('Temps (s)', 'FontSize', 11);
ylabel('Température (°C)', 'FontSize', 11);
title(sprintf('Air de la serre (\\theta_{BOX}) — RMSE : %.3f °C', rmse_box), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend('Mesure bruitée', 'Estimation Kalman (Simulink)', ...
       'Location', 'southeast', 'FontSize', 9.5);

sgtitle('Estimation par filtre de Kalman intégré (Simulink)', ...
        'FontSize', 13, 'FontWeight', 'bold');
