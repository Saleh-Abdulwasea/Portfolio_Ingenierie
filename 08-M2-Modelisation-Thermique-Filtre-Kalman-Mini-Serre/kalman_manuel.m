%% ========================================================================
%  KALMAN_MANUEL.M — Partie 3 : Espace d'état Simulink + Kalman manuel (2 mesures)
% =========================================================================
%  Compare sur les 2 sorties (theta_RES et theta_BOX) :
%    1) Les mesures expérimentales bruitées (tempRes, tempBox)
%    2) Le modèle d'état discrétisé par blocs dans Simulink (theta_1, theta_3)
%    3) L'estimation par filtre de Kalman manuel à 2 mesures (yEST)
% =========================================================================
clear; clc; close all;

%% 1. Chargement du modèle continu et des mesures expérimentales
run("model.m");

tempRes = readmatrix('table_TempUpRes_6V570mA.dat');   % Mesure résistance [°C]
tempBox = readmatrix('table_TempUpBox_6V570mA.dat');   % Mesure air serre  [°C]

Ts = 1;                                 % Période d'échantillonnage [s]
N  = length(tempRes(2, :));
t  = (0:N-1)' * Ts;                     % Vecteur temps [s]

%% 2. Entrées et conditions initiales pour Simulink
u    = (0.57 * 6) * ones(N, 1);         % Puissance de chauffe P [W]
Tamb = tempBox(2, 1);                   % Température ambiante initiale [°C]

data_in.time = t;
data_in.signals(1).values = u;
data_in.signals(2).values = tempRes(2, :)';
data_in.signals(3).values = tempBox(2, :)';

theta_a = [t, Tamb * ones(N, 1)];       % Température ambiante [°C]
x_IC    = Tamb * ones(5, 1);            % Condition initiale de l'intégrateur [°C]

%% 3. Discrétisation ZOH et paramètres du filtre de Kalman (2 mesures)
C_meas = [1 0 0 0 0;                    % Mesure 1 : theta_RES
          0 0 1 0 0];                   % Mesure 2 : theta_BOX
sysc = ss(A, B, C_meas, zeros(2, 1));
sysd = c2d(sysc, Ts, 'zoh');

Ad = sysd.A;
Bd = sysd.B;

Q = 1e-3 * eye(5);                      % Covariance du bruit de modèle
R = diag([0.4956^2, 0.5792^2]);         % Covariance du bruit de mesure (Res, Box)

%% 4. Simulation du modèle Simulink
simOut = sim('kalman_manuel_sim.slx', ...
    'StopTime', num2str(t(end)), ...
    'ReturnWorkspaceOutputs', 'on');

%% 5. Extraction des résultats (normalisation en Nx2) et calcul des RMSE
Yraw = squeeze(simOut.yEST);
if size(Yraw, 1) == 2 && size(Yraw, 2) ~= 2
    Yhat = Yraw.';
else
    Yhat = Yraw;
end

y_sim_res  = squeeze(simOut.theta_1);
y_sim_box  = squeeze(simOut.theta_3);
y_meas_res = tempRes(2, :)';
y_meas_box = tempBox(2, :)';

L = min([length(t), size(Yhat, 1), length(y_sim_res), length(y_sim_box), length(y_meas_res)]);
t_plt      = t(1:L);
Yhat       = Yhat(1:L, :);
y_sim_res  = y_sim_res(1:L);
y_sim_box  = y_sim_box(1:L);
y_meas_res = y_meas_res(1:L);
y_meas_box = y_meas_box(1:L);

rmse_sim_res = sqrt(mean((y_sim_res - y_meas_res).^2));
rmse_kf_res  = sqrt(mean((Yhat(:, 1) - y_meas_res).^2));
rmse_sim_box = sqrt(mean((y_sim_box - y_meas_box).^2));
rmse_kf_box  = sqrt(mean((Yhat(:, 2) - y_meas_box).^2));

fprintf('=== Résultats Partie 3 (2 mesures) ===\n');
fprintf('theta_RES — RMSE Modèle Simulink : %.4f °C | RMSE Kalman manuel : %.4f °C\n', rmse_sim_res, rmse_kf_res);
fprintf('theta_BOX — RMSE Modèle Simulink : %.4f °C | RMSE Kalman manuel : %.4f °C\n', rmse_sim_box, rmse_kf_box);

%% 6. Visualisation comparative (qualité rapport)
figure('Color', 'w', 'Position', [100, 100, 980, 640], ...
       'Name', 'Partie 3 : Modèle discret Simulink vs Kalman manuel (2 mesures)');

subplot(2, 1, 1);
plot(t_plt, y_meas_res, 'Color', [0.45 0.45 0.45], 'LineWidth', 1.0); hold on;
plot(t_plt, y_sim_res,  'b--', 'LineWidth', 1.6);
plot(t_plt, Yhat(:, 1), 'r-',  'LineWidth', 1.8);
grid on; box on; set(gca, 'FontSize', 10);
xlabel('Temps (s)', 'FontSize', 11);
ylabel('Température (°C)', 'FontSize', 11);
title(sprintf('Résistance chauffante (\\theta_{RES}) — RMSE Modèle : %.3f °C | RMSE Kalman : %.3f °C', ...
      rmse_sim_res, rmse_kf_res), 'FontSize', 12, 'FontWeight', 'bold');
legend('Mesure bruitée (temp\_Res)', ...
       'Modèle discret Simulink (\theta_1)', ...
       'Estimation Kalman manuel (yEST_1)', ...
       'Location', 'southeast', 'FontSize', 9.5);

subplot(2, 1, 2);
plot(t_plt, y_meas_box, 'Color', [0.45 0.45 0.45], 'LineWidth', 1.0); hold on;
plot(t_plt, y_sim_box,  'b--', 'LineWidth', 1.6);
plot(t_plt, Yhat(:, 2), 'r-',  'LineWidth', 1.8);
grid on; box on; set(gca, 'FontSize', 10);
xlabel('Temps (s)', 'FontSize', 11);
ylabel('Température (°C)', 'FontSize', 11);
title(sprintf('Air de la serre (\\theta_{BOX}) — RMSE Modèle : %.3f °C | RMSE Kalman : %.3f °C', ...
      rmse_sim_box, rmse_kf_box), 'FontSize', 12, 'FontWeight', 'bold');
legend('Mesure bruitée (temp\_Box)', ...
       'Modèle discret Simulink (\theta_3)', ...
       'Estimation Kalman manuel (yEST_2)', ...
       'Location', 'southeast', 'FontSize', 9.5);

sgtitle('Modèle discret Simulink vs Filtre de Kalman manuel (2 mesures)', ...
        'FontSize', 13, 'FontWeight', 'bold');
