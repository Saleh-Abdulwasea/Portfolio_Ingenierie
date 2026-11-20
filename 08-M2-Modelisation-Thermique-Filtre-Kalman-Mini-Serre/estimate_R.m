%% === Estimation sigma et matrice R (Res/Box) à partir des logs ===
clear; clc; close all;

% 1) Lire les fichiers 
tempRes = readmatrix('table_TempUpRes_6V570mA.dat');   % °C
tempBox = readmatrix('table_TempUpBox_6V570mA.dat');   % °C

% Hypothèse: la 2e ligne contient la série temporelle 
yH = tempRes(2,:).';     % Heater (Res)
yB = tempBox(2,:).';     % Box (air/boîtier)

% Pas d’échantillonnage 
Ts = 1;                               % [s] 
N  = min(length(yH), length(yB));
t  = (0:N-1)'*Ts;

% Tronquer à la même longueur
yH = yH(1:N); 
yB = yB(1:N);

% 2) Choisir un palier "stable" (ici: dernier 20% des points)
idx = round(0.8*N):N;
yH_s = yH(idx);
yB_s = yB(idx);
t_s  = t(idx);

% 3) Lissage pour approximer le signal "vrai" (moyenne glissante)
W   = max(5, 2*floor(5/Ts)+1);   % fenêtre ~5 s (impair)
yH_f = movmean(yH_s, W);
yB_f = movmean(yB_s, W);

% 4) Résiduel (bruit estimé)
eH = yH_s - yH_f;
eB = yB_s - yB_f;

% 5) Écarts-types et matrice R
sigma_H = std(eH, 0);               % écarts-types (non biaisé par défaut)
sigma_B = std(eB, 0);
R_full  = cov([eH eB], 1);          % covariance MLE (1/N) → 2x2
R_unb   = cov([eH eB]);             % non biaisée (1/(N-1)) → 2x2
R_diag  = diag([sigma_H^2, sigma_B^2]);

% 6) Affichages 
fprintf('\n=== Estimation du bruit de mesure (palier final) ===\n');
fprintf('Ts = %.3f s, fenêtre de lissage W = %d échantillons\n', Ts, W);
fprintf('sigma_Res (Heater) = %.4f °C\n', sigma_H);
fprintf('sigma_Box          = %.4f °C\n', sigma_B);
disp('R_full (MLE, 1/N)   ='); disp(R_full);
disp('R_unbiased (1/(N-1))='); disp(R_unb);
disp('R_diag (indépendant)='); disp(R_diag);

% 7) Graphes de contrôle
figure('Color','w','Name','Palier + résiduel');
subplot(2,1,1);
plot(t_s, yH_s,'k-', t_s, yH_f,'r-','LineWidth',1.2); grid on
title('Heater (Res) : palier et lissé'); xlabel('Temps (s)'); ylabel('°C'); legend('mesure','lissé');
subplot(2,1,2);
plot(t_s, yB_s,'k-', t_s, yB_f,'m-','LineWidth',1.2); grid on
title('Box : palier et lissé'); xlabel('Temps (s)'); ylabel('°C'); legend('mesure','lissé');

figure('Color','w','Name','Résidu (bruit estimé)');
subplot(2,1,1); plot(t_s, eH,'b-'); grid on; title('e_H = y_H - \hat{s}_H'); xlabel('Temps (s)'); ylabel('°C');
subplot(2,1,2); plot(t_s, eB,'b-'); grid on; title('e_B = y_B - \hat{s}_B'); xlabel('Temps (s)'); ylabel('°C');

% (Option) histogrammes
figure('Color','w','Name','Histogrammes des résidus');
subplot(1,2,1); histogram(eH); title(sprintf('Heater (\\sigma=%.3f)', sigma_H)); grid on
subplot(1,2,2); histogram(eB); title(sprintf('Box (\\sigma=%.3f)', sigma_B)); grid on

% Sauvegarder pour le Kalman 
R = R_diag;           %  prends diag si corrélation faible ; sinon R_full
save('R_from_logs.mat','R','sigma_H','sigma_B','R_full','R_unb','R_diag','Ts');
