%% ===== Simple RL vs PID metrics (0..180s) + save to TXT =====
clear; clc;

Tend = 180;

% Fichiers (mets tes noms ici si besoin)
load("results_RL.mat","RL");
load("results_PID.mat","PID");

% --- Récupération signaux ---
tR = RL.t(:);  TR = RL.T3(:);  uR = RL.u(:);  eR = RL.e(:);
tP = PID.t(:); TP = PID.T3(:); uP = PID.u(:); eP = PID.e(:);
SP = PID.SP;

% --- Coupe à 0..180s ---
idxR = (tR>=0 & tR<=Tend);   tR=tR(idxR); TR=TR(idxR); uR=uR(idxR); eR=eR(idxR);
idxP = (tP>=0 & tP<=Tend);   tP=tP(idxP); TP=TP(idxP); uP=uP(idxP); eP=eP(idxP);

% --- Base temps commune: PID ---
t = tP;
TR = interp1(tR, TR, t, "linear", "extrap");
uR = interp1(tR, uR, t, "linear", "extrap");
eR = interp1(tR, eR, t, "linear", "extrap");

% --- Clamp u entre 0 et 1 ---
uR = min(1,max(0,uR));
uP = min(1,max(0,uP));

% --- METRICS (simples) ---
RMSE_RL  = sqrt(mean(eR.^2));
RMSE_PID = sqrt(mean(eP.^2));

IAE_RL  = trapz(t, abs(eR));
IAE_PID = trapz(t, abs(eP));

maxE_RL  = max(abs(eR));
maxE_PID = max(abs(eP));

meanU_RL  = mean(uR);
meanU_PID = mean(uP);

Ju2_RL  = trapz(t, uR.^2);   % proxy énergie ventilo
Ju2_PID = trapz(t, uP.^2);

pct02_RL  = 100*mean(abs(eR)<=0.2);
pct02_PID = 100*mean(abs(eP)<=0.2);

pct05_RL  = 100*mean(abs(eR)<=0.5);
pct05_PID = 100*mean(abs(eP)<=0.5);

% --- Affichage console ---
fprintf("\n=== RL vs PID (0..%ds), SP=%.2f°C ===\n", Tend, SP);
fprintf("RMSE (°C)        : RL=%.3f | PID=%.3f\n", RMSE_RL, RMSE_PID);
fprintf("IAE  (°C*s)      : RL=%.2f  | PID=%.2f\n", IAE_RL, IAE_PID);
fprintf("Max |e| (°C)     : RL=%.3f | PID=%.3f\n", maxE_RL, maxE_PID);
fprintf("Mean PWM (%%)     : RL=%.1f | PID=%.1f\n", 100*meanU_RL, 100*meanU_PID);
fprintf("∫u^2 dt (proxy)  : RL=%.2f  | PID=%.2f\n", Ju2_RL, Ju2_PID);
fprintf("Time in ±0.2°C   : RL=%.1f%% | PID=%.1f%%\n", pct02_RL, pct02_PID);
fprintf("Time in ±0.5°C   : RL=%.1f%% | PID=%.1f%%\n", pct05_RL, pct05_PID);

% --- Sauvegarde TXT ---
fname = "comparison_simple_" + datestr(now,"yyyymmdd_HHMMSS") + ".txt";
fid = fopen(fname,"w");
fprintf(fid,"RL vs PID (0..%ds), SP=%.2f°C\n", Tend, SP);
fprintf(fid,"RMSE (°C)        : RL=%.3f | PID=%.3f\n", RMSE_RL, RMSE_PID);
fprintf(fid,"IAE  (°C*s)      : RL=%.2f  | PID=%.2f\n", IAE_RL, IAE_PID);
fprintf(fid,"Max |e| (°C)     : RL=%.3f | PID=%.3f\n", maxE_RL, maxE_PID);
fprintf(fid,"Mean PWM (%%)     : RL=%.1f | PID=%.1f\n", 100*meanU_RL, 100*meanU_PID);
fprintf(fid,"Integral u^2 dt  : RL=%.2f  | PID=%.2f\n", Ju2_RL, Ju2_PID);
fprintf(fid,"Time in ±0.2°C   : RL=%.1f%% | PID=%.1f%%\n", pct02_RL, pct02_PID);
fprintf(fid,"Time in ±0.5°C   : RL=%.1f%% | PID=%.1f%%\n", pct05_RL, pct05_PID);
fclose(fid);

disp("Saved TXT: " + fname);

% --- Option CSV (1 ligne RL + 1 ligne PID) ---
CSV = table(["RL";"PID"], [RMSE_RL;RMSE_PID], [IAE_RL;IAE_PID], [maxE_RL;maxE_PID], ...
            [100*meanU_RL;100*meanU_PID], [Ju2_RL;Ju2_PID], [pct02_RL;pct02_PID], [pct05_RL;pct05_PID], ...
            'VariableNames', {'Controller','RMSE_C','IAE_Cs','MaxAbsErr_C','MeanPWM_pct','Int_u2_dt','Pct_in_0p2','Pct_in_0p5'});

csvname = "comparison_simple_" + datestr(now,"yyyymmdd_HHMMSS") + ".csv";
writetable(CSV, csvname);
disp("Saved CSV: " + csvname);
