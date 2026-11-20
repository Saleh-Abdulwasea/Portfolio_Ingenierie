/*
  Contrôle thermique par Q-learning (ventilateur via PWM, résistance toujours ON)
  Matériel ciblé : Arduino MEGA (A12 dispo, EEPROM 4 KB)

  - Capteur LM35 sur A12 (10 mV/°C, Vref = 5V)
  - Ventilateur via L298N, PWM sur D5
  - Q-table: 41 (erreur) x 3 (dérivée) x 5 (actions) = 615 floats (~2.4 KB)
  - Sauvegarde EEPROM toutes les 60 s pour limiter l'usure
*/

#include <Arduino.h>
#include <EEPROM.h>

// === IO (adapter aux tiens)
const int PIN_FAN_PWM = 5;     // ventilateur via L298N (ENABLE)
const int PIN_T_LM35  = A14;   // capteur LM35 (Arduino MEGA)

// === Consignes & sécurité
float Tset  = 30.0;  // °C, consigne
float Tmax  = 70.0;  // °C, dépassement fortement puni dans la récompense
float Tcrit = 80.0;  // °C, sécurité dure -> ventilateur 100%

// === Discrétisation
const float BIN_E = 0.5f;  // pas d'erreur en °C
inline int binE(float e){
  int b = (int)round(e / BIN_E) + 20;    // map [-10, +10]°C -> [0..40]
  if (b < 0)  b = 0;
  if (b > 40) b = 40;
  return b;
}
inline int binDE(float de){
  if (de < -0.5f) return 0;   // refroidit
  if (de >  0.5f) return 2;   // chauffe
  return 1;                   // ~stable
}

// === Actions (uniquement fan)
#define N_A 5
const uint8_t FAN_LVL[N_A] = {0, 80, 140, 200, 255};

// === Espace d'état
#define N_E  41
#define N_DE 3

// === Q-table & hyperparamètres RL
float Q[N_E][N_DE][N_A];      // init à 0 dans setup()
float alpha  = 0.10f;         // taux d’apprentissage
float gamma_ = 0.98f;         // facteur d’actualisation
float eps    = 0.30f;         // epsilon-greedy (diminue vers 0.05)

// === Persistance EEPROM
// Mise en page EEPROM:
// [0..3]  magic 'QMEG' (0x51 0x4D 0x45 0x47)
// [4..5]  version (uint16_t)
// [6..7]  nFloats (uint16_t) = 615
// [8..(8+4*615-1)]  Q-table (floats)
// [fin..fin+3] checksum (uint32_t somme octets mod 2^32)
const uint32_t EEPROM_MAGIC   = 0x514D4547UL; // 'QMEG'
const uint16_t EEPROM_VERSION = 1;
const int      Q_FLOATS       = N_E * N_DE * N_A; // 615
const int      EEPROM_BASE    = 0;
const int      EEPROM_Q_START = EEPROM_BASE + 8;  // après header
const int      EEPROM_END     = EEPROM_Q_START + Q_FLOATS * sizeof(float);
const int      EEPROM_CK_POS  = EEPROM_END;       // checksum 4 octets
// Taille totale = 8 + 4*615 + 4 = 2472 bytes (OK sur MEGA 4KB)

// Utilitaires EEPROM
void eepromWriteU32(int addr, uint32_t v){
  EEPROM.update(addr+0, (uint8_t)(v >> 24));
  EEPROM.update(addr+1, (uint8_t)(v >> 16));
  EEPROM.update(addr+2, (uint8_t)(v >>  8));
  EEPROM.update(addr+3, (uint8_t)(v >>  0));
}
uint32_t eepromReadU32(int addr){
  uint32_t b0 = EEPROM.read(addr+0);
  uint32_t b1 = EEPROM.read(addr+1);
  uint32_t b2 = EEPROM.read(addr+2);
  uint32_t b3 = EEPROM.read(addr+3);
  return (b0<<24) | (b1<<16) | (b2<<8) | b3;
}
void eepromWriteU16(int addr, uint16_t v){
  EEPROM.update(addr+0, (uint8_t)(v >> 8));
  EEPROM.update(addr+1, (uint8_t)(v >> 0));
}
uint16_t eepromReadU16(int addr){
  uint16_t b0 = EEPROM.read(addr+0);
  uint16_t b1 = EEPROM.read(addr+1);
  return (uint16_t)((b0<<8) | b1);
}

uint32_t computeChecksumQ(){
  // somme des octets de la Q-table (ordre mémoire Arduino, little-endian)
  uint32_t sum = 0;
  const uint8_t* p = (const uint8_t*)Q;
  for (int i = 0; i < (int)(Q_FLOATS * sizeof(float)); ++i) {
    sum += p[i];
  }
  return sum;
}

void saveQToEEPROM(){
  // Écrit header (temporaire), Q, puis checksum
  eepromWriteU32(EEPROM_BASE, EEPROM_MAGIC);
  eepromWriteU16(EEPROM_BASE + 4, EEPROM_VERSION);
  eepromWriteU16(EEPROM_BASE + 6, (uint16_t)Q_FLOATS);

  int addr = EEPROM_Q_START;
  for (int iE = 0; iE < N_E; ++iE){
    for (int iDE = 0; iDE < N_DE; ++iDE){
      for (int a = 0; a < N_A; ++a){
        float v = Q[iE][iDE][a];
        // écrire v (4 octets)
        uint8_t* pb = (uint8_t*)&v;
        for (int b = 0; b < 4; ++b) {
          EEPROM.update(addr++, pb[b]);
        }
      }
    }
  }
  uint32_t cksum = computeChecksumQ();
  eepromWriteU32(EEPROM_CK_POS, cksum);
}

bool loadQFromEEPROM(){
  uint32_t magic = eepromReadU32(EEPROM_BASE);
  uint16_t ver   = eepromReadU16(EEPROM_BASE + 4);
  uint16_t nF    = eepromReadU16(EEPROM_BASE + 6);
  if (magic != EEPROM_MAGIC || ver != EEPROM_VERSION || nF != Q_FLOATS) {
    return false;
  }

  int addr = EEPROM_Q_START;
  for (int iE = 0; iE < N_E; ++iE){
    for (int iDE = 0; iDE < N_DE; ++iDE){
      for (int a = 0; a < N_A; ++a){
        float v;
        uint8_t* pb = (uint8_t*)&v;
        for (int b = 0; b < 4; ++b) {
          pb[b] = EEPROM.read(addr++);
        }
        Q[iE][iDE][a] = v;
      }
    }
  }
  uint32_t cks_read = eepromReadU32(EEPROM_CK_POS);
  uint32_t cks_now  = computeChecksumQ();
  if (cks_read != cks_now) {
    // checksum KO -> on considère invalide
    return false;
  }
  return true;
}

// === Utilitaires RL
inline int argmax(const float* arr){
  int k = 0;
  for (int i = 1; i < N_A; ++i) if (arr[i] > arr[k]) k = i;
  return k;
}

float readTempC(){
  // LM35 : 10 mV/°C ; ADC 10 bits ; Vref = 5.00 V par défaut (MEGA)
  int raw = analogRead(PIN_T_LM35);          // 0..1023
  float V  = raw * (5.0f / 1023.0f);         // volts
  return V * 100.0f;                         // °C
}

void setup(){
  // PWM fan au repos
  analogWrite(PIN_FAN_PWM, 0);

  // Seed pour l'aléatoire (A0 en entrée flottante si dispo)
  randomSeed(analogRead(A0));

  // Init Q à 0
  for (int iE = 0; iE < N_E; ++iE)
    for (int iDE = 0; iDE < N_DE; ++iDE)
      for (int a = 0; a < N_A; ++a)
        Q[iE][iDE][a] = 0.0f;

  // Tentative de chargement EEPROM
  bool ok = loadQFromEEPROM();

  Serial.begin(115200);
  delay(50);
  Serial.println(F("==== Q-Learning Thermal Control (MEGA) ===="));
  Serial.print(F("EEPROM load: ")); Serial.println(ok ? F("OK") : F("empty/invalid -> Q=0"));
  Serial.print(F("Tset="));  Serial.print(Tset);
  Serial.print(F("  Tmax=")); Serial.print(Tmax);
  Serial.print(F("  Tcrit=")); Serial.println(Tcrit);
}

void loop(){
  static float e_prev = 0.0f;
  static float T_prev = readTempC();
  static int   a_prev = 0;
  static unsigned long lastSaveMs = 0;

  delay(250); // cadence ~2 Hz au total (deux délais par tour)

  // Mesure & état courant
  float T  = readTempC();
  float e  = T - Tset;
  float de = e - e_prev;

  // Sécurité dure
  if (T > Tcrit) {
    analogWrite(PIN_FAN_PWM, 255);
    e_prev = e; T_prev = T;
    // on ne met pas à jour Q pour cette itération
    return;
  }

  // Indices d'état
  int iE  = binE(e);
  int iDE = binDE(de);

  // Politique epsilon-greedy
  int a;
  if (random(1000) < (int)(1000.0f * eps)) a = random(N_A);      // exploration
  else                                      a = argmax(Q[iE][iDE]); // exploitation

  // Action: mettre le ventilateur au niveau choisi
  analogWrite(PIN_FAN_PWM, FAN_LVL[a]);

  // Observer l'état suivant
  delay(250);
  float Tn  = readTempC();
  float en  = Tn - Tset;
  float den = en - e;

  // Récompense
  float r = -fabs(en);                     // punir l'écart à la consigne
  if (fabs(en) < 0.3f) r += 0.5f;          // bonus de précision
  // Pénalité de "brassage" (changement brutal de vitesse)
  r -= 0.02f * (float)abs((int)FAN_LVL[a] - (int)FAN_LVL[a_prev]) / 255.0f;
  // Pénalité de dépassement (douce mais ferme avant Tcrit)
  if (Tn > Tmax) r -= 50.0f;

  // Bellman
  int jE  = binE(en);
  int jDE = binDE(den);
  float maxQnext = Q[jE][jDE][0];
  for (int k = 1; k < N_A; ++k) if (Q[jE][jDE][k] > maxQnext) maxQnext = Q[jE][jDE][k];

  Q[iE][iDE][a] = (1.0f - alpha) * Q[iE][iDE][a] + alpha * (r + gamma_ * maxQnext);

  // Annealing exploration
  if (eps > 0.05f) eps -= 1e-5f;

  // Mémoires
  a_prev = a; e_prev = e; T_prev = T;

  // Sauvegarde périodique (toutes les 60 s)
  unsigned long now = millis();
  if (now - lastSaveMs > 60000UL) {
    saveQToEEPROM();
    lastSaveMs = now;
    Serial.print(F("[SAVE] eps=")); Serial.print(eps, 4);
    Serial.print(F("  T=")); Serial.print(T, 2);
    Serial.print(F("  e=")); Serial.print(e, 2);
    Serial.print(F("  a=")); Serial.println(a);
    Serial.print(F("  pwm=")); Serial.println(FAN_LVL[a]);

  }
}
