%% ===== ACQUISITION ROBUSTE + PLOT =====
clear; clc;

port = "/dev/cu.usbmodem1101";
a = arduino(port,"Mega2560");

pinRelais="D48";
A1="A12"; A2="A13"; A3="A14"; A4="A15";

dt = 0.2;
T_total = 100;      % durée totale (s)
t_on  = 5;
t_off = 90;

relayActiveHigh = true;

N = floor(T_total/dt)+1;
t = zeros(N,1);
T1 = zeros(N,1); T2 = zeros(N,1); T3 = zeros(N,1); T4 = zeros(N,1);
heater = zeros(N,1);


fprintf("T_total = %.1f s | dt = %.3f s\n", T_total, dt);

% Etat initial: chauffage OFF
if relayActiveHigh, writeDigitalPin(a,pinRelais,0);
else,             writeDigitalPin(a,pinRelais,1);
end

t0 = tic;
k = 0;

while true
    tk = toc(t0);
    if tk >= T_total
        break;
    end

    k = k + 1;
    t(k) = tk;

    h = (tk >= t_on) && (tk < t_off);
    heater(k) = h;

    if relayActiveHigh
        writeDigitalPin(a,pinRelais,h);
    else
        writeDigitalPin(a,pinRelais,~h);
    end

    T1(k) = readVoltage(a,A1)*100;
    T2(k) = readVoltage(a,A2)*100;
    T3(k) = readVoltage(a,A3)*100;
    T4(k) = readVoltage(a,A4)*100;

    if mod(k, round(1/dt)) == 0
        fprintf("t=%6.1f | T1=%.2f T2=%.2f T3=%.2f T4=%.2f | heater=%d\n", ...
            tk, T1(k), T2(k), T3(k), T4(k), h);
    end

    pause(dt);
end



% Sécurité : chauffage OFF quoi qu'il arrive
if relayActiveHigh, writeDigitalPin(a,pinRelais,0);
else,             writeDigitalPin(a,pinRelais,1);
end

% Nettoyage des points non remplis (si arrêt avant la fin)
valid = t > 0;
t = t(valid); T1=T1(valid); T2=T2(valid); T3=T3(valid); T4=T4(valid); heater=heater(valid);

% PLOTS
figure; plot(t,T1,t,T2,t,T3,t,T4);
grid on; xlabel("Temps (s)"); ylabel("Température (°C)");
legend("T1","T2","T3","T4","Location","best");
title("Evolution des températures");

figure; plot(t,heater);
grid on; ylim([-0.2 1.2]);
xlabel("Temps (s)"); ylabel("Chauffage (0/1)");
title("Commande résistance");
