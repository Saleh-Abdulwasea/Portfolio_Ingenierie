#include <Arduino.h>
#include <math.h>
#include <Braccio.h>
#include <Servo.h>
#include <Pixy2.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

Pixy2 pixy;

void calcule_angles(float X, float Y);

void setup() {
  Serial.begin(115200);
  Braccio.begin();
  pixy.init();
  Serial.println("Initialisation terminée. Détection d'objets en cours...");
}

void loop() {
  static String inputString = "";
  static bool stringComplete = false;

  // Rechercher des objets avec Pixy2
  pixy.ccc.getBlocks();

  if (pixy.ccc.numBlocks) {
    Serial.print("Nombre de blocs détectés: ");
    Serial.println(pixy.ccc.numBlocks);

    for (int i = 0; i < pixy.ccc.numBlocks; i++) {
      Serial.print("Objet ");
      Serial.print(i);
      Serial.print(": x = ");
      Serial.print(pixy.ccc.blocks[i].m_x);
      Serial.print(", y = ");
      Serial.println(pixy.ccc.blocks[i].m_y);
    }

    Serial.println("Entrez l'indice de l'objet à déplacer vers la poubelle :");

    // Attendre l'entrée de l'utilisateur
    while (true) {
      while (Serial.available()) {
        char inChar = (char)Serial.read();
        if (inChar == '\n') {
          stringComplete = true;
        } else {
          inputString += inChar;
        }
      }

      if (stringComplete) {
        int objIndex = inputString.toInt();
        inputString = ""; // Réinitialiser l'entrée
        stringComplete = false;

        if (objIndex >= 0 && objIndex < pixy.ccc.numBlocks) {
          float X = pixy.ccc.blocks[objIndex].m_x;
          float Y = pixy.ccc.blocks[objIndex].m_y;

          Serial.print("Déplacement de l'objet ");
          Serial.println(objIndex);

          // Calculer et afficher les angles pour les nouvelles coordonnées
          calcule_angles(X, Y);   // Prendre l'objet
          Braccio.ServoMovement(20, 140, 80, 30, 80, 40, 70); // Vers la poubelle
          Braccio.ServoMovement(20, 140, 80, 30, 80, 40, 20); // Vers la poubelle
          Braccio.ServoMovement(20, 140, 80, 80, 80, 40, 70); // Vers la poubelle
          break; // Sortir de la boucle et redétecter les objets
        } else {
          Serial.println("Indice invalide. Veuillez réessayer.");
          // Réafficher les positions des objets
          Serial.print("Nombre de blocs détectés: ");
          Serial.println(pixy.ccc.numBlocks);

          for (int i = 0; i < pixy.ccc.numBlocks; i++) {
            Serial.print("Objet ");
            Serial.print(i);
            Serial.print(": x = ");
            Serial.print(pixy.ccc.blocks[i].m_x);
            Serial.print(", y = ");
            Serial.println(pixy.ccc.blocks[i].m_y);
          }

          Serial.println("Entrez l'indice de l'objet à déplacer vers la poubelle :");
        }
      }
    }
  } else {
    Serial.println("Aucun objet détecté.");
    delay(1000);
  }
}

void calcule_angles(float X, float Y) {
  float X_r, Y_r;

  // Changement aux coordonnées du bras
 
 Y_r= -2.35 + Y/4.25;

 if(X < -2){
  X_r= 54.2 - X/3.7;
  }else if(X > -2 && X < 3){
    X_r= 52.5 - X/3.9;
    } else if(X > 3 && X < 20){
      X_r= 44.5 - X/4.7;
      }else{
        X_r= 44.5 - X/4.8;
        }

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
    int a1 = 8;
    int a2 = 13;
    int a3 = 13;
    int a4 = 19.5;

    // Convertir l'angle en radians pour les calculs trigonométriques
    float angle_B = radians(90 - 2 * (D - 12));

    // Calculer les coordonnées de C
    float Cx = D - a4 * cos(angle_B);
    float Cy = a4 * sin(angle_B) - a1;

    // Calculer la distance r
    float r = sqrt(pow(Cx, 2) + pow(Cy, 2));

    // Calculer les angles en radians
    float angle_M1_r = atan2(Y_r, X_r);
    float angle_M2_r = atan2(Cy, Cx) + acos((pow(a2, 2) + pow(r, 2) - pow(a3, 2)) / (2 * r * a2));
    float angle_M3_r = acos((pow(a2, 2) + pow(a3, 2) - pow(r, 2)) / (2 * a2 * a3)) - PI / 2;
    float angle_M4_r = PI - angle_B - angle_M2_r - angle_M3_r;

    // Convertir les angles en degrés
    float angle_M1_d = 150 - round(degrees(angle_M1_r)/0.82);
    float angle_M2_d = round(degrees(angle_M2_r));
    float angle_M3_d = round(degrees(angle_M3_r));
    float angle_M4_d = round(degrees(angle_M4_r));

    // Vérifier et corriger les angles négatifs
    if (angle_M1_d < 0) angle_M1_d = 0;
    if (angle_M2_d < 0) angle_M2_d = 0;
    if (angle_M3_d < 0) angle_M3_d = 0;
    if (angle_M4_d < 0) angle_M4_d = 0;

    // Vérifier les plages d'angles autorisées pour les servos
    float angle_M5_d = 40; // Angle fixe pour wrist rotation
    float angle_M6_d = 10; // Angle fixe pour gripper initial

    if (angle_M1_d >= 0 && angle_M1_d <= 180 &&
        angle_M2_d >= 15 && angle_M2_d <= 165 &&
        angle_M3_d >= 0 && angle_M3_d <= 180 &&
        angle_M4_d >= 0 && angle_M4_d <= 180 &&
        angle_M5_d >= 0 && angle_M5_d <= 180 &&
        angle_M6_d >= 10 && angle_M6_d <= 73) {
      
      // Ajuster les angles des servos
      Braccio.ServoMovement(20, angle_M1_d, angle_M2_d, angle_M3_d, angle_M4_d, angle_M5_d, angle_M6_d); // Vers l'objet
      Braccio.ServoMovement(20, angle_M1_d, angle_M2_d, angle_M3_d, angle_M4_d, angle_M5_d, 70); // Fermer la pince
      delay(500);
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

  } else {
    Serial.println("Cette distance n'est pas acceptable.");
  }
}
