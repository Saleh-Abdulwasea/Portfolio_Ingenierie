#include <Arduino.h>
#include <Pixy2.h>
#include <Braccio.h>

Pixy2 pixy;



void setup() {
  Serial.begin(115200);
  pixy.init();
}


void loop() {
  // Rechercher des objets avec Pixy2
  pixy.ccc.getBlocks();

  if (pixy.ccc.numBlocks) {
    Serial.print("Nombre de blocs détectés: ");
    Serial.println(pixy.ccc.numBlocks);

    for (int i = 0; i < pixy.ccc.numBlocks; i++) {
      Serial.print("Bloc ");
      Serial.print(i);
      Serial.print(": Type=");
      Serial.print(pixy.ccc.blocks[i].m_signature);
      Serial.print(" x=");
      Serial.print(pixy.ccc.blocks[i].m_x);
      Serial.print(" y=");
      Serial.print(pixy.ccc.blocks[i].m_y);
      Serial.print(" largeur=");
      Serial.print(pixy.ccc.blocks[i].m_width);
      Serial.print(" hauteur=");
      Serial.println(pixy.ccc.blocks[i].m_height);
        delay(1000);

    }
  } else {
    Serial.println("Aucun objet détecté.");
  }
  delay(1000);
}
