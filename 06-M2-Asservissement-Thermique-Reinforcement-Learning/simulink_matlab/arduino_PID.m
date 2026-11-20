%% ===== PID Control System for Temperature Regulation using PWM =====
% This script implements a PID control system to regulate the temperature
% of a system using a fan and a heater. The temperature is measured using
% an LM35 sensor, and the fan speed is controlled via PWM. The PID
% controller adjusts the fan speed based on the difference between the
% measured temperature and the desired setpoint. The results are logged
% and plotted for analysis.
%% ===== PID MATLAB : Regulation T4 par PWM ventilo =====
clear; clc;

% --- Connexion ---
port = "/dev/cu.usbmodem1101";          
a = arduino(port,"Mega2560");

% --- Pins ---
pinEN  = "D4";      % PWM ventilo
pinIN1 = "D22";     % sens
pinIN2 = "D23";
pinT3  = "A15";     % LM35 T4
pinRelais = "D48";  % résistance

relayActiveHigh = true;   % mets false si relais actif bas

% --- Essai ---
dt = 0.2;                 % s
T_total = 180;            % s
SP = 25.0;                % consigne (°C)

% --- PID (valeurs de départ) ---
% Comme le ventilo REFROIDIT : on prend e = T - SP (si T>SP => ventiler +)
Kp = 0.08;                % à ajuster
Ki = 0.02;                % à ajuster
Kd = 0.00;                % commence à 0

u_min = 0.0;              % PWM min (0..1)
u_max = 1.0;              % PWM max

% --- Chauffage (apport) ---
heaterOn = 1;             % on met la résistance ON fixe pendant le test

% --- Init actionneurs ---
writeDigitalPin(a,pinIN1,1);
writeDigitalPin(a,pinIN2,0);
writePWMDutyCycle(a,pinEN,0);

if relayActiveHigh
    writeDigitalPin(a,pinRelais, heaterOn);
else
    writeDigitalPin(a,pinRelais, ~heaterOn);
end

% --- Logs ---
N = floor(T_total/dt)+1;
t = zeros(N,1);
T = zeros(N,1);
u = zeros(N,1);
e_log = zeros(N,1);

% --- PID states ---
I = 0;
e_prev = 0;

% kickstart (démarrer le ventilo fort 0.3s si u>0)
kick = true;

t0 = tic;
k = 0;

while true
    tk = toc(t0);
    if tk >= T_total
        break;   % arrêt garanti
    end

    k = k + 1;
    t(k,1) = tk;

    % --- Mesure ---
    T(k,1) = readVoltage(a,pinT3) * 100;
    e = T(k,1) - SP;
    e_log(k,1) = e;

    % --- PID ---
    I = I + e*dt;
    D = (e - e_prev)/dt;
    u_raw = Kp*e + Ki*I + Kd*D;

    u_sat = min(u_max, max(u_min, u_raw));
    u(k,1) = u_sat;

    % Anti-windup simple
    if u_raw ~= u_sat
        I = I - e*dt;
    end

    writePWMDutyCycle(a,pinEN, u_sat);
    e_prev = e;

    % Print 1 Hz
    if mod(k, round(1/dt)) == 0
        fprintf("t=%6.1f / %5.1f | T3=%.2f | u=%.2f\n", tk, T_total, T(k), u_sat);
    end

    pause(dt);
end



% --- Sécurité : tout couper ---
writePWMDutyCycle(a,pinEN,0);
if relayActiveHigh
    writeDigitalPin(a,pinRelais,0);
else
    writeDigitalPin(a,pinRelais,1);
end

% --- Nettoyage logs si arrêt avant la fin ---
valid = t > 0;
t = t(valid); T = T(valid); u = u(valid); e_log = e_log(valid);

% ===== Plots (3 subplots) =====
figure;

% 1) Temperature vs Setpoint
subplot(3,1,1);
plot(t, T, 'b', 'LineWidth', 1.5); hold on;
yline(SP, '--k', 'LineWidth', 1.5);
grid on;
ylabel('Temperature (°C)');
title('Measured Temperature vs Setpoint');
legend('Measured', 'Setpoint', 'Location', 'best');

% 2) Fan speed (PWM)
subplot(3,1,2);
plot(t, 100*u, 'g', 'LineWidth', 1.2);  % u is 0..1 -> convert to %
grid on;
ylabel('Fan Speed (%)');
title('Fan Speed');


% 3) Heater power otherwise plot PID error
subplot(3,1,3);
plot(t, e_log, 'r', 'LineWidth', 1.2);
grid on;
xlabel('Time (s)');
ylabel('Error (°C)');                 
title('Control Error (T - SP)');




%% ===== Save results (PID) =====
PID.t  = t;
PID.T3 = T;        
PID.u  = u;        
PID.e  = e_log;

PID.SP = SP;
PID.dt = dt;
PID.T_total = T_total;

PID.Kp = Kp; PID.Ki = Ki; PID.Kd = Kd;
PID.u_min = u_min; PID.u_max = u_max;
PID.heaterOn = heaterOn;
PID.port = port;
PID.pinT3 = pinT3;

fname_mat = "results_PID_" + datestr(now,"yyyymmdd_HHMMSS") + ".mat";
save(fname_mat, "PID");
disp("Saved: " + fname_mat);


