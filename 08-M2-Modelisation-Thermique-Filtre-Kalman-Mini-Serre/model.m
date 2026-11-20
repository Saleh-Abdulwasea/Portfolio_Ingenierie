%% ========================================================================
%  MODEL.M — Modèle thermique d'état continu de la mini-serre (5 états)
% =========================================================================
%  Vecteur d'état :
%    x = [theta_RES ; theta_ALU ; theta_BOX ; theta_SEN ; theta_FAN]  [°C]
%
%  Entrées :
%    u = P     : Puissance de chauffe injectée dans la résistance       [W]
%    v = Tamb  : Température ambiante extérieure                      [°C]
%
%  Représentation d'état continue :
%    dx/dt = A*x + B*u + E*v
%    y     = C*x + D*u
% =========================================================================

%% 1. Paramètres thermiques (résistances [K/W] et capacités [J/K])
%  Note : Les demi-résistances (*, *2) sont conservées pour le schéma Simscape.

% Résistance chauffante & bloc aluminium
Cth_Res  = 6.5;             % Capacité thermique de la résistance   [J/K]
Rth_alu  = 1.84 / 2;        % Demi-résistance de conduction alu     [K/W]
Rth_alu2 = 1.84 / 2;        % Demi-résistance de conduction alu (2) [K/W]
Cth_alu  = 10.79;           % Capacité thermique de l'aluminium     [J/K]
Rc_alu   = 11.0;            % Résistance de convection alu -> air   [K/W]

% Capteur de température sur l'aluminium
Rth_sen  = 180.0;           % Résistance thermique capteur          [K/W]
Cth_sen  = 0.22;            % Capacité thermique capteur            [J/K]

% Air intérieur de la serre (Box)
Cth_air  = 1647 / 8;        % Capacité thermique de l'air           [J/K]

% Enveloppe PET (parois)
Rc_pet   = 28.9;            % Résistance de convection PET (int.)   [K/W]
Rth_pet  = 22.5 / 2;        % Demi-résistance de conduction PET     [K/W]
Rth_pet2 = 22.5 / 2;        % Demi-résistance de conduction PET (2) [K/W]
Rc_pet1  = 28.9;            % Résistance de convection PET (ext.)   [K/W]
Cth_pet  = 67.5;            % Capacité thermique du PET             [J/K]

% Ventilateur (Fan)
Rc_fan   = 3.33;            % Résistance de convection fan (int.)   [K/W]
Rth_fan  = 65.0 / 2;        % Demi-résistance de conduction fan     [K/W]
Rth_fan2 = 65.0 / 2;        % Demi-résistance de conduction fan (2) [K/W]
Rc_fan1  = 3.33;            % Résistance de convection fan (ext.)   [K/W]
Cth_fan  = 147.0;           % Capacité thermique du ventilateur     [J/K]

% Fuites / ventilation directe
Rv       = 3.1;             % Résistance de ventilation             [K/W]

%% 2. Résistances totales équivalentes pour le modèle d'état réduit
Rth_alu_tot = Rth_alu + Rth_alu2;               % 1.84 K/W
Rth_fan_tot = Rth_fan + Rth_fan2;               % 65.0 K/W
R_pet       = Rth_pet + Rth_pet2 + Rc_pet1;     % 51.4 K/W

%% 3. Construction des matrices d'état continues (A, B, E, C, D)
% Ligne 1 : Résistance chauffante (theta_RES)
a11 = -2 / (Rth_alu_tot * Cth_Res);
a12 =  2 / (Rth_alu_tot * Cth_Res);

% Ligne 2 : Bloc aluminium (theta_ALU)
a21 =  2 / (Rth_alu_tot * Cth_alu);
a22 = -(2 / Rth_alu_tot + 1 / Rth_sen + 1 / Rc_alu) / Cth_alu;
a23 =  1 / (Rc_alu * Cth_alu);
a24 =  1 / (Rth_sen * Cth_alu);

% Ligne 3 : Air de la serre (theta_BOX)
a32 =  1 / (Rc_alu * Cth_air);
a33 = -(1 / Rc_alu + 1 / Rv + 1 / R_pet + 1 / (Rc_fan + Rth_fan_tot)) / Cth_air;
a35 =  1 / ((Rc_fan + Rth_fan_tot) * Cth_air);

% Ligne 4 : Capteur aluminium (theta_SEN)
a42 =  1 / (Rth_sen * Cth_sen);
a44 = -1 / (Rth_sen * Cth_sen);

% Ligne 5 : Ventilateur (theta_FAN)
a53 =  1 / ((Rc_fan + Rth_fan_tot) * Cth_fan);
a55 = -1 / ((Rc_fan + Rth_fan_tot) * Cth_fan);

A = [
    a11, a12,   0,   0,   0;
    a21, a22, a23, a24,   0;
      0, a32, a33,   0, a35;
      0, a42,   0, a44,   0;
      0,   0, a53,   0, a55
];

B = [1 / Cth_Res; 0; 0; 0; 0];

E = [0; 0; (1 / Rv + 1 / R_pet) / Cth_air; 0; 0];

C = eye(5);
D = 0;
