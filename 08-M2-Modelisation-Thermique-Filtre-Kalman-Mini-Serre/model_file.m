%% ========================================================================
%  MODEL_FILE.M — Partie 1 : Validation du modèle en boucle ouverte
% =========================================================================
%  Compare les mesures expérimentales avec :
%    1) Le modèle physique Simscape (model_file_sim1.slx)
%    2) Le modèle d'état continu (A, B, E) défini dans model.m
% =========================================================================
clear; clc; close all;

%% 1. Chargement du modèle et des relevés expérimentaux
run("model.m");

tempRes = readmatrix('table_TempUpRes_6V570mA.dat');   % Mesure résistance [°C]
tempBox = readmatrix('table_TempUpBox_6V570mA.dat');   % Mesure air serre  [°C]

Ts = 1;                                 % Période d'échantillonnage [s]
N  = length(tempRes(2, :));
t  = (0:N-1)' * Ts;                     % Vecteur temps [s]
stopTimeSimu = t(end);

% Entrées physiques : P = U * I = 6 V * 0.57 A = 3.42 W
u    = (0.57 * 6) * ones(N, 1);
Tamb = tempBox(2, 1);                   % Température ambiante initiale [°C]
v    = Tamb * ones(N, 1);

% Structure d'entrée pour Simulink (model_file_sim1.slx)
data_in.time = t;
data_in.signals(1).values = u;
data_in.signals(2).values = tempRes(2, :)';
data_in.signals(3).values = tempBox(2, :)';

%% 2. Simulation Simscape & Modèle d'état continu
sim('model_file_sim1.slx');

C_out = [1 0 0 0 0;                     % Sortie 1 : theta_RES
         0 0 1 0 0];                    % Sortie 2 : theta_BOX
sysc  = ss(A, [B E], C_out, zeros(2, 2));
x0    = Tamb * ones(5, 1);
y_ss  = lsim(sysc, [u v], t, x0);

% Calcul des erreurs quadratiques moyennes (RMSE)
y_res_meas = tempRes(2, :)';
y_box_meas = tempBox(2, :)';
rmse_res_ss = sqrt(mean((y_ss(:, 1) - y_res_meas).^2));
rmse_box_ss = sqrt(mean((y_ss(:, 2) - y_box_meas).^2));

%% 3. Mise en forme des figures (qualité rapport)
fig = figure('Color', 'w', 'Position', [100, 100, 950, 620], ...
             'Name', 'Validation du modèle thermique — Boucle ouverte');

subplot(2, 1, 1);
plot(t, y_res_meas, 'Color', [0.25 0.25 0.25], 'LineWidth', 1.0); hold on;
plot(t, theta_1(1:N), 'r-', 'LineWidth', 1.6);
plot(t, y_ss(:, 1), 'b--', 'LineWidth', 1.8);
grid on; box on; set(gca, 'FontSize', 10);
xlabel('Temps (s)', 'FontSize', 11);
ylabel('Température (°C)', 'FontSize', 11);
title(sprintf('Résistance chauffante (\\theta_{RES}) — RMSE modèle d''état : %.2f °C', rmse_res_ss), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend('Mesures expérimentales', 'Modèle Simscape', 'Modèle d''état (A, B, E)', ...
       'Location', 'southeast', 'FontSize', 9.5);

subplot(2, 1, 2);
plot(t, y_box_meas, 'Color', [0.25 0.25 0.25], 'LineWidth', 1.0); hold on;
plot(t, theta_2(1:N), 'm-', 'LineWidth', 1.6);
plot(t, y_ss(:, 2), 'b--', 'LineWidth', 1.8);
grid on; box on; set(gca, 'FontSize', 10);
xlabel('Temps (s)', 'FontSize', 11);
ylabel('Température (°C)', 'FontSize', 11);
title(sprintf('Air de la serre (\\theta_{BOX}) — RMSE modèle d''état : %.2f °C', rmse_box_ss), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend('Mesures expérimentales', 'Modèle Simscape', 'Modèle d''état (A, B, E)', ...
       'Location', 'southeast', 'FontSize', 9.5);

sgtitle('Validation du modèle thermique de la mini-serre (U = 6 V, I = 570 mA)', ...
        'FontSize', 13, 'FontWeight', 'bold');
