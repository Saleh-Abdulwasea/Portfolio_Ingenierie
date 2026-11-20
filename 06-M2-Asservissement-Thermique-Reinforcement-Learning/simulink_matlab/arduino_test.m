%*********************************************************************
% Ce script MATLAB initialise une communication avec une carte Arduino, 
% contrôle un relais, lit des valeurs de température à partir d'un capteur 
% LM35, et gère un moteur à courant continu via PWM. Il configure également 
% une communication série pour envoyer des commandes à un dispositif externe 
% et lire des données de celui-ci.
%*********************************************************************

clear; clc;

port = "/dev/cu.usbmodem1101";   % à adapter (Mac)
% port = "COM5";                % Windows exemple

a = arduino(port, "Mega2560");  
disp(a)


% Initialisation de la communication série
pinRelais = "D48";

writeDigitalPin(a, pinRelais, 1); pause(1);   % ON 
writeDigitalPin(a, pinRelais, 0); pause(1);   % OFF

pinT3 = "A15";
V = readVoltage(a, pinT3);
T3 = V * 100;             % LM35: 10mV/°C => T=V*100
fprintf("V=%.3f V  T3=%.2f °C\n", V, T3);

t0 = tic;
while toc(t0) < 10
    T3 = readVoltage(a,"A14") * 100;
    fprintf("T3=%.2f °C\n", T3);
    pause(0.2);
end

IN1 = "D22";
IN2 = "D23";
EN  = "D4";   % PWM

% Sens
writeDigitalPin(a, IN1, 1);
writeDigitalPin(a, IN2, 0);

% Test plein pot
writePWMDutyCycle(a, EN, 1.0);
pause(2);

% 50%
writePWMDutyCycle(a, EN, 0.5);
pause(2);

% Off
writePWMDutyCycle(a, EN, 0.0);




s = serialport(port,9600);
configureTerminator(s,"LF");
flush(s);

% Chauffage ON
writeline(s,"HEAT=1");
writeline(s,"MODE=TEST");

% PWM ventilo 120
writeline(s,"PWM=120");

% Lire quelques lignes mesures
for i=1:20
    line = readline(s);
    disp(line)
end
