%**************************************************************************
% Fichier modèle 
%**************************************************************************
clear; clc; close all;
%**************************************************************************
% Exécution du fichier modele_valeur.m contenant les valeurs des paramètres (Rth,
% Cth, ...) et la définition des matrices de la représentation d'état 
run("modele_valeur.m");
%**************************************************************************
% Importation des relevés
tempRes = readmatrix('table_TempUpRes_6V570mA.dat');
tempBox = readmatrix('table_TempUpBox_6V570mA.dat');

%**************************************************************************
% Temps de simulation SIMULINK
Ts = 1;
N = length(tempRes(2,:));
%N = 3000;
stopTimeSimu = Ts*N;
t  = (0:N-1)'*Ts;

% Définition des vecteurs SIMULINK
u = ones(1,N)*5.95;  %vecteur signal d'entrée
data_in.time = (Ts*(1:N))';
data_in.signals(1).values = u';
data_in.signals(2).values = tempRes(2,:)';
data_in.signals(3).values = tempBox(2,:)';
theta_a     = [t, tempBox(2,1)*ones(N,1)];    % ambiance



% Simulation SIMULINK
Y = sim('model_file_sim.slx');


% Affichage PLOT

Ts = 1;                                
%N  = 2000;                              % longueur du signal
N = length(tempRes(2,:));
%t  = (0:N-1)*Ts;                       % vecteur temps
M = 5000;
t  = (0:M-1)*Ts;

figure;
plot(t, theta_1(1:M), 'r-', 'LineWidth', 1.5); hold on;
xlabel('Time (s)');
ylabel('Temperature °C');
title('θ₁ (model)');
legend('θ₁ (simulation)');
grid on;

figure; 
plot(t, theta_2(1:M), 'm-', 'LineWidth', 1.5); hold on;
xlabel('Time (s)');
ylabel('Temperature °C');
title('θ₂ (model)');
legend('θ₂ (simulation)');
grid on;