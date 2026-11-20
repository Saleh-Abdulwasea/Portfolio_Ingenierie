%% ===== Compare RL vs PID over first 180 seconds =====
clear; clc;

% ---- Put your filenames here ----
fileRL  = "results_RL.mat";
filePID = "results_PID.mat";

load(fileRL, "RL");
load(filePID, "PID");

Tend = 180;  % seconds to compare

% ---- Extract and trim to 180s ----
tRL  = RL.t(:);  TRL  = RL.T3(:);  uRL  = RL.u(:);  eRL  = RL.e(:);
tPID = PID.t(:); TPID = PID.T3(:); uPID = PID.u(:); ePID = PID.e(:);

idxRL  = (tRL  <= Tend);
idxPID = (tPID <= Tend);

tRL  = tRL(idxRL);  TRL  = TRL(idxRL);  uRL  = uRL(idxRL);  eRL  = eRL(idxRL);
tPID = tPID(idxPID); TPID = TPID(idxPID); uPID = uPID(idxPID); ePID = ePID(idxPID);

% ---- Use PID time as common time base (since your PID test is 180s) ----
t = tPID;

% Interpolate RL onto PID time base
TRL_i = interp1(tRL, TRL, t, "linear", "extrap");
uRL_i  = interp1(tRL, uRL,  t, "linear", "extrap");
eRL_i  = interp1(tRL, eRL,  t, "linear", "extrap");

TPID_i = TPID;  % already on t
uPID_i = uPID;
ePID_i = ePID;

SP = PID.SP; % compare against PID setpoint (should match RL desired SP)

% ---- Plots (3 subplots) ----
figure;

subplot(3,1,1);
plot(t, TRL_i, 'b', 'LineWidth', 1.4); hold on;
plot(t, TPID_i,'m', 'LineWidth', 1.4);
yline(SP, '--k', 'LineWidth', 1.2);
grid on;
ylabel("Temperature (°C)");
title("Temperature: RL vs PID (0-180 s)");
legend("RL","PID","Setpoint","Location","best");

subplot(3,1,2);
plot(t, 100*uRL_i, 'g', 'LineWidth', 1.2); hold on;
plot(t, 100*uPID_i,'c', 'LineWidth', 1.2);
grid on;
ylabel("Fan Speed (%)");
title("Control Input (Fan)");
legend("RL","PID","Location","best");

subplot(3,1,3);
plot(t, eRL_i, 'r', 'LineWidth', 1.2); hold on;
plot(t, ePID_i,'k', 'LineWidth', 1.2);
grid on;
xlabel("Time (s)");
ylabel("Error (°C)");
title("Tracking Error (T - SP)");
legend("RL","PID","Location","best");

% ---- Metrics (0-180s) ----
RMSE_RL  = sqrt(mean(eRL_i.^2));
RMSE_PID = sqrt(mean(ePID_i.^2));

IAE_RL  = trapz(t, abs(eRL_i));
IAE_PID = trapz(t, abs(ePID_i));

MaxErr_RL  = max(abs(eRL_i));
MaxErr_PID = max(abs(ePID_i));

fprintf("\n=== Comparison over 0-%ds ===\n", Tend);
fprintf("RMSE  (°C): RL = %.3f | PID = %.3f\n", RMSE_RL, RMSE_PID);
fprintf("IAE   (°C·s): RL = %.3f | PID = %.3f\n", IAE_RL, IAE_PID);
fprintf("Max|e| (°C): RL = %.3f | PID = %.3f\n", MaxErr_RL, MaxErr_PID);
