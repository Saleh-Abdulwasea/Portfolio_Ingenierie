#include <Arduino.h>
#include <math.h>
#include <Braccio.h>
#include <Servo.h>
#include <Pixy2.h>

Pixy2 pixy;
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

void calcule_angles(float X, float Y);

void setup() {
  Serial.begin(115200);
  pixy.init();
  Braccio.begin();
  
}

void loop() {
  pixy.ccc.getBlocks();
  if (pixy.ccc.numBlocks>0) {
      Serial.print(pixy.ccc.blocks[0].m_x);
      Serial.print(",");
      Serial.println(pixy.ccc.blocks[0].m_y);


     float X = pixy.ccc.blocks[0].m_x;
     float Y = pixy.ccc.blocks[0].m_y;
      if(X>130){
        float X_r = 50 - X/3.67;
        float Y_r = 4.3+Y/3.7;
      }else if(X<130 && X>90){
        float X_r = 50 - X/4.6;
        float Y_r = 4.3+Y/3.7;
      }else{
          float X_r = 50 - X/4.67;
          float Y_r = 4.3+Y/3.7;
       }

      float X_r = 50 - X/3.6;
      float Y_r = 4.3+Y/3.7;

      Serial.print("X_r = ");
      Serial.println(X_r);
      Serial.print("Y_r = ");
      Serial.println(Y_r);

      // Calculer la distance D
      float D = sqrt(pow(X_r, 2) + pow(Y_r, 2));
      Serial.print("Distance calculée : ");
      Serial.println(D);

      // Vérifier si la distance est acceptable
      if (D >= 12 && D <= 42) {
        // Calculer et afficher les angles pour les nouvelles coordonnées
        calcule_angles(X_r, Y_r);                                     /////////////////////////////////////////////////////////
        delay(500);
        Braccio.ServoMovement(20, 150, 100, 40, 70, 40, 65);
       
        Braccio.ServoMovement(20, 150, 100, 40, 70, 40, 10);
      } else {
        Serial.println("Cette distance n'est pas acceptable.");
      }
      
  } else {
    Serial.println("Aucun objet détecté.");
  }
  delay(1000);
}

void calcule_angles(float X, float Y) {
  int a1 = 6;
  int a2 = 13;
  int a3 = 13;
  int a4 = 19.5;

  // Calculer la distance D
  float D = sqrt(pow(X, 2) + pow(Y, 2));

  // Convertir l'angle en radians pour les calculs trigonométriques
  float angle_B = radians(90 - 2 * (D - 12));

  // Calculer les coordonnées de C
  float Cx = D - a4 * cos(angle_B);
  float Cy = a4 * sin(angle_B) - a1;

  // Calculer la distance r
  float r = sqrt(pow(Cx, 2) + pow(Cy, 2));

  // Calculer les angles en radians
  float angle_M1_r = atan2(Y, X);
  float angle_M2_r = atan2(Cy, Cx) + acos((pow(a2, 2) + pow(r, 2) - pow(a3, 2)) / (2 * r * a2));
  float angle_M3_r = acos((pow(a2, 2) + pow(a3, 2) - pow(r, 2)) / (2 * a2 * a3)) - PI / 2;
  float angle_M4_r = PI - angle_B - angle_M2_r - angle_M3_r;

  // Convertir les angles en degrés
  float angle_M1_d = round(130 - degrees(angle_M1_r));
  float angle_M2_d = round(degrees(angle_M2_r));
  float angle_M3_d = round(degrees(angle_M3_r));
  float angle_M4_d = round(degrees(angle_M4_r));
  float angle_M5_d = 40;
  float angle_M6_d = 10;



  // Vérifier et corriger les angles négatifs
  if (angle_M1_d < 0) angle_M1_d = 0;
  if (angle_M2_d < 0) angle_M2_d = 0;
  if (angle_M3_d < 0) angle_M3_d = 0;
  if (angle_M4_d < 0) angle_M4_d = 0;

   if (angle_M1_d >= 0 && angle_M1_d <= 180 &&
        angle_M2_d >= 15 && angle_M2_d <= 165 &&
        angle_M3_d >= 0 && angle_M3_d <= 180 &&
        angle_M4_d >= 0 && angle_M4_d <= 180 &&
        angle_M5_d >= 0 && angle_M5_d <= 180 &&
        angle_M6_d >= 10 && angle_M6_d <= 73) {
      Braccio.ServoMovement(20, angle_M1_d, angle_M2_d, angle_M3_d, angle_M4_d, angle_M5_d, angle_M6_d);
      delay(500);
      Braccio.ServoMovement(20, angle_M1_d, angle_M2_d, angle_M3_d, angle_M4_d, angle_M5_d, 60);
    } else {
      Serial.println("Un ou plusieurs angles ne sont pas dans les plages autorisées.");
    }

  // Afficher les résultats
  Serial.print("M1 :   ");
  Serial.println(angle_M1_d);
  Serial.print("M2 :   ");
  Serial.println(angle_M2_d);
  Serial.print("M3 :   ");
  Serial.println(angle_M3_d);  
  Serial.print("M4 :   ");
  Serial.println(angle_M4_d);
}
