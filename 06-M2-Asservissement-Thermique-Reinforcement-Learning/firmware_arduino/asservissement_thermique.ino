#include <LiquidCrystal_I2C.h>
#include <Keypad.h>
#include <String.h>
#include <Wire.h>
#include <PID_v1_bc.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);   // LCD I2C 20x4

// Températures
float Temperature1 = 0.0f;  // Température1
float Temperature2 = 0.0f;
float Temperature3 = 0.0f;
float Temperature4 = 0.0f;

// États
int start  = 0;      // ventilateur allumé ou non
int pwm_v  = 0;      // Commande de la vitesse du ventilateur
int autom  = 1;      // régulation auto ou non
int prop   = 1;      // PID en cours ou non

// ===== PID =====
double Setpoint, Input, Output;
double Kp=3, Ki=5, Kd=0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, REVERSE);

// ===== Strings pour l’affichage =====
String T1;
String T2;
String T3;
String T4;
String V = "V=0";
String Mode = "FAN OFF";
String R = "R OFF";
String E;

// ===== Broches =====
int relais      = 48;
int moteurPin1  = 22;
int moteurPin2  = 23;
int moteurEN    = 4;     // Pin4 PWM

// ===== Clavier matriciel 4x3 =====
const byte LIGNES   = 4;
const byte COLONNES = 3;
char keys[LIGNES][COLONNES] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};
byte rowPins[LIGNES]   = {7, 8, 9, 10};
byte colPins[COLONNES] = {11, 12, 13};
Keypad CLV = Keypad(makeKeymap(keys), rowPins, colPins, LIGNES, COLONNES);

// ------------------------------------------------------------------

void setup() {
  Serial.begin(9600);

  pinMode(relais, OUTPUT);
  pinMode(moteurPin1, OUTPUT);
  pinMode(moteurPin2, OUTPUT);
  pinMode(moteurEN, OUTPUT);

  // Transmission vers Excel (PLX-DAQ)
  Serial.println("CLEARDATA");
  Serial.println("LABEL, Date, Temps, Te1, Te2, Te3, Te4, pwm");

  // LCD
  lcd.init();
  lcd.backlight();

  Setpoint = 27;                 // consigne pour PID
  myPID.SetMode(AUTOMATIC);
}

// ------------------------------------------------------------------

void loop() {

  char key = CLV.getKey();
  if (key != NO_KEY) {
    Serial.println(key);

    if (key == '6') {                         // Rechauffeur ON
      digitalWrite(relais, HIGH);
      R = "R ON";
    }
    if (key == '9') {                         // Rechauffeur OFF
      digitalWrite(relais, LOW);
      R = "R OFF";
    }
  }

  // ===== Lecture capteurs (évolution sans régulation) =====
  int reading1 = analogRead(12);
  int reading2 = analogRead(13);
  int reading3 = analogRead(14);
  int reading4 = analogRead(15);

  // Conversion en °C
  Temperature1 = reading1 * (5.0 / 1023.0) * 100.0;
  Temperature2 = reading2 * (5.0 / 1023.0) * 100.0;
  Temperature3 = reading3 * (5.0 / 1023.0) * 100.0;
  Temperature4 = reading4 * (5.0 / 1023.0) * 100.0;

  if (Temperature4 > Setpoint) { E = "!"; } 
  else { E = " "; }

  // Envoi vers Excel
  Serial.println((String)"DATA, DATE, TIME," +
                 Temperature1 + + "," + Temperature2 + "," +
                 Temperature3 + "," + Temperature4 + "," + pwm_v);

  // Préparation textes
  T1 = "T1=";
  T1 += Temperature1;
  T2 = "T2="; 
  T2 += Temperature2;
  T3 = "T3="; 
  T3 += Temperature3;
  T4 = "T4="; 
  T4 += Temperature4;

  // ===== Pilotage moteur (sens) =====
  digitalWrite(moteurPin1, 1);
  digitalWrite(moteurPin2, 0);
  analogWrite(moteurEN, pwm_v);

  // ===== Commandes clavier =====
  if (key != NO_KEY) {

    if (key == '1') {                // Allumage ventilateur (mini)
      pwm_v = 60;
      start = 1;
      V = "V="; 
      V += pwm_v;
      Mode = "FAN ON";
    }

    if (key == '*') {                // Extinction ventilateur
      pwm_v = 0;
      start = 0;
      V = "V="; 
      V += pwm_v;
      Mode = "FAN OFF";
    }

    // Réglage manuel vitesse (+ / -)
    if (start == 1 && key == '4') {
      pwm_v += 10;
      if (pwm_v > 255) {pwm_v = 255;}
      Mode = "REG MAN";
      V = "V="; 
      V += pwm_v;
    }
    if (start == 1 && key == '7') {
      pwm_v -= 10;
      if (pwm_v < 0) {pwm_v = 0;}
      Mode = "REG MAN";
      V = "V= "; 
      V += pwm_v;
    }
}

    // ===== Régulation automatique simple =====
    if (start == 1 && key == '2') {autom = 0; }

    while (autom != 1) {

      // Nouvelles lectures
      int reading1 = analogRead(12);
      int reading2 = analogRead(13);
      int reading3 = analogRead(14);
      int reading4 = analogRead(15);

      Temperature1 = reading1 * (5.0 / 1023.0) * 100.0;
      Temperature2 = reading2 * (5.0 / 1023.0) * 100.0;
      Temperature3 = reading3 * (5.0 / 1023.0) * 100.0;
      Temperature4 = reading4 * (5.0 / 1023.0) * 100.0;

      if (Temperature4 > Setpoint) { E = "!"; } 
      else { E = "-"; }

      Serial.println((String)"DATA, DATE, TIME," +
                     Temperature1 + + "," + Temperature2 + "," +
                     Temperature3 + "," + Temperature4 + "," + pwm_v);

      T1 = "T1=";
      T1 += Temperature1;
      T2 = "T2="; 
      T2 += Temperature2;
      T3 = "T3="; 
      T3 += Temperature3;
      T4 = "T4="; 
      T4 += Temperature4;

    digitalWrite(moteurPin1, 1);
    digitalWrite(moteurPin2, 0);
    analogWrite(moteurEN, pwm_v);

      // Stratégie Auto très simple (seuils)
    char k = CLV.getKey();

    if (Temperature4 < Setpoint) {
      pwm_v = 50;
      V = "V="; 
      V += pwm_v;
      Mode = "Auto";
      }

      if (Temperature4 > 32) {
        pwm_v = 255;
        V = "V="; 
        V += pwm_v;
        Mode = "Auto";
      }

      // Affichage
      lcd.clear();
      lcd.setCursor(0,0); 
      lcd.print(T4);
      lcd.setCursor(8,0); 
      lcd.print(E);
      lcd.setCursor(0,1); 
      lcd.print(R);
      lcd.setCursor(11,0); 
      lcd.print(V);
      lcd.setCursor(9,1); 
      lcd.print(Mode);
      delay(300);

      // Sortie de l’auto
      if (k == '0') { Mode = "Fin Reg"; pwm_v = 60; V = "V="; V += pwm_v; autom = 1; }
    }

    // ===== PID =====
    if (start == 1 && key == '3') { prop = 0; }
    while (prop != 1) {
      char k = CLV.getKey();

      // Lectures
      int reading1 = analogRead(12);
      int reading2 = analogRead(13);
      int reading3 = analogRead(14);
      int reading4 = analogRead(15);

      Temperature1 = reading1 * (5.0 / 1023.0) * 100.0;
      Temperature2 = reading2 * (5.0 / 1023.0) * 100.0;
      Temperature3 = reading3 * (5.0 / 1023.0) * 100.0;
      Temperature4 = reading4 * (5.0 / 1023.0) * 100.0;

      if (Temperature4 > Setpoint) { E = "!"; } 
      else { E = " "; }

      Serial.println((String)"DATA, DATE, TIME," +
                     Temperature1 + + "," + Temperature2 + "," +
                     Temperature3 + "," + Temperature4 + "," + pwm_v);
      
      T1 = "T1=";
      T1 += Temperature1;
      T2 = "T2="; 
      T2 += Temperature2;
      T3 = "T3="; 
      T3 += Temperature3;
      T4 = "T4="; 
      T4 += Temperature4;

      Mode  = "PID";
      Input = Temperature4;
      myPID.Compute();

      digitalWrite(moteurPin1, 1);
      digitalWrite(moteurPin2, 0);
      analogWrite(4, Output);

      pwm_v = Output;
      V = "V="; V += pwm_v;

      // Affichage
      lcd.clear();
      lcd.setCursor(0,0); 
      lcd.print(T4);
      lcd.setCursor(8,0); 
      lcd.print(E);
      lcd.setCursor(0,1); 
      lcd.print(R);
      lcd.setCursor(11,0); 
      lcd.print(V);
      lcd.setCursor(9,1); 
      lcd.print(Mode);
      delay(300);

      if (k == '#') { Mode = "Fin PID"; pwm_v = 60; V = "V="; V += pwm_v; prop = 1; }
    }
  

  // ===== Affichage “idle” =====
      lcd.clear();
      lcd.setCursor(0,0); 
      lcd.print(T4);
      lcd.setCursor(8,0); 
      lcd.print(E);
      lcd.setCursor(0,1); 
      lcd.print(R);
      lcd.setCursor(11,0); 
      lcd.print(V);
      lcd.setCursor(9,1); 
      lcd.print(Mode);
      delay(300);
}
