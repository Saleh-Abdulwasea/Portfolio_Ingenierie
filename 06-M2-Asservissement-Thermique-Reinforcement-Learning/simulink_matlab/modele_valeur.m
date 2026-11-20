
Cth_Res = 15;
Rth_alu= 0.1/2;
Cth_alu= 50;
Rth_alu2= 0.1/2;
Rth_sen= 24;
[Rth_sen2, Rth_sen3, Rth_sen4] = deal(0.37/2);
[Rth_sen22, Rth_sen33, Rth_sen44] = deal(0.37/2);
[Rc_sen2, Rc_sen3, Rc_sen4] = deal(90/2);
[Rc_sen22, Rc_sen33, Rc_sen44] = deal(90/2);
[Cth_sen, Cth_sen2, Cth_sen3, Cth_sen4] = deal(0.22);
Rc_alu= 10;
Cth_air= 2;
Rc_pet= 20/2;
Rth_pet= 5/2;
Cth_pet= 34;
Rth_pet2= 5/2;
Rc_pet1= 20/2;
Rc_fan= 1.2/2;
Rth_fan= 2.5/2;
Cth_fan= 287;
Rth_fan2= 2.5/2;
Rc_fan1= 1.2/2;
Rv= 50;
%___---___
R_pet = (2*Rth_pet + Rc_pet1);


a11 = -2/(Rth_alu*Cth_Res);
a12 =  2/(Rth_alu*Cth_Res);
a13 = 0;
a14 = 0;
a15 = 0;

a21 =  2/(Cth_alu*Rth_alu);
a22 = (1/Cth_alu)*((-2/Rth_alu) - 1/(2*Rth_sen) - 1/Rc_alu);
a23 =  1/(Rc_alu*Cth_alu);
a24 =  1/(Rth_sen*Cth_alu);
a25 = 0; 


a31 = 0;
a32 = 1/(Rc_alu*Cth_air) ;
a33 = (1/Cth_air)*(- (1/Rc_alu) - (1/Rv) - (1/R_pet) - (1/(Rc_fan + Rth_fan))); 
a34 = 0;
a35 =  1/((Rc_fan + Rth_fan*2)*Cth_air);

a41 = 0; 
a42 =  1/(2*Rth_sen*Cth_sen);
a43 = 0; 
a44 = -1/(2*Rth_sen*Cth_sen);
a45 = 0; 

 

a51 = 0; 
a52 = 0;
a53 = 1/((Rc_fan + Rth_fan*2)*Cth_fan);
a54 = 0;
a55 = -1/((Rc_fan + Rth_fan*2)*Cth_fan);

A = [
    a11 a12 a13 a14 a15;
    a21 a22 a23 a24 a25;
    a31 a32 a33 a34 a35;
    a41 a42 a43 a44 a45;
    a51 a52 a53 a54 a55;
];


b11 = 1/Cth_Res ;
b12 = 0;
b13 = 0;
b14 = 0; 
b15 = 0; 

B = [
    b11;
    b12;
    b13;
    b14;
    b15
];

%--------------------
c11 = 1;
c21 = 1;
c31 = 1;
c41 = 1; 
c51 = 1; 

C = [c11  0   0    0     0 ;
      0  c21  0    0     0 ;
      0   0  c31   0     0 ;
      0   0   0    c41   0 ;
      0   0   0    0   c51 ;];

Ck = [0 0 1 0 0;];

D = 0;


e11 = 0;
e12 = 0;
e13 = (1/Cth_air)* ((1/Rv) + (1/R_pet));
e14 = 0;
e15 = 0; 

E = [e11; e12; e13; e14; e15];




% 1) sample time 
Ts = 1;               % à adapter à la dynamique

% 2) Discrétisation ZOH 
sysc = ss(A, [B E], C, D);
sysd = c2d(sysc, Ts, 'zoh');

% 3) Récupère les matrices pour Simulink
Ad = sysd.A;
Bd = sysd.B(:,1);                      % pour u
Gd = sysd.B(:,2);                      % pour v = T_amb  , 2e colonne de B_discret
Cd = sysd.C;
Dd = zeros(size(C,1),2);





K   = 1;      % exemple
tau = 50;     % exemple
Ts  = 1;      % sample time

G0   = tf(K,[tau 1]);      % modèle sans délai
G0_z = c2d(G0,Ts,'zoh');   % discrétisation

[b,a] = tfdata(G0_z,'v');  % numérateur, dénominateur
b    % numerator
a    % denominator

A
B
E