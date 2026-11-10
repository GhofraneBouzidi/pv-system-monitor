/*
 * PV System Monitor - Arduino sensor node
 *
 * Reads three analog inputs, smooths them over a rolling window,
 * and streams one JSON frame per cycle to the Streamlit dashboard:
 *   {"voltage":36.42,"current":4.81,"temperature":38.5}
 *
 * Authors:    Ghofrane Bouzidi, Donia El Manaa
 * Supervisor: Prof. Mouez Bousaada
 * License:    MIT
 */

const int voltagePin = A3;
const int currentPin = A1;
const int tempPin = A2;

// VALEURS RÉALISTES POUR PANNEAU PHOTOVOLTAÏQUE
// Tension panneau PV: 30-45V (système 36V nominal)
const float MIN_VOLTAGE = 30.0;
const float MAX_VOLTAGE = 45.0;

// Courant PV: 0-10A (panneau 300-400W)
const float MIN_CURRENT = 0.0;
const float MAX_CURRENT = 10.0;

// Température module: 15-70°C
const float MIN_TEMP = 15.0;
const float MAX_TEMP = 70.0;

// Smoothing pour stabilité
const int numReadings = 10;
float voltageReadings[numReadings];
float currentReadings[numReadings];
float tempReadings[numReadings];
int readIndex = 0;

void setup() {
  Serial.begin(9600);
  analogReference(DEFAULT);
  
  // Initialiser les tableaux
  for (int i = 0; i < numReadings; i++) {
    voltageReadings[i] = 0;
    currentReadings[i] = 0;
    tempReadings[i] = 0;
  }
  
  delay(100);
}

void loop() {
  // Lecture des potentiomètres
  int voltageRaw = analogRead(voltagePin);
  int currentRaw = analogRead(currentPin);
  int tempRaw = analogRead(tempPin);
  
  // Mapping vers valeurs PV réalistes
  voltageReadings[readIndex] = map_float(voltageRaw, 0, 1023, MIN_VOLTAGE, MAX_VOLTAGE);
  currentReadings[readIndex] = map_float(currentRaw, 0, 1023, MIN_CURRENT, MAX_CURRENT);
  tempReadings[readIndex] = map_float(tempRaw, 0, 1023, MIN_TEMP, MAX_TEMP);
  
  readIndex = (readIndex + 1) % numReadings;
  
  // Moyennes pour lisser les valeurs
  float voltage = average(voltageReadings, numReadings);
  float current = average(currentReadings, numReadings);
  float temperature = average(tempReadings, numReadings);
  
  // Contraintes de sécurité
  voltage = constrain(voltage, MIN_VOLTAGE, MAX_VOLTAGE);
  current = constrain(current, MIN_CURRENT, MAX_CURRENT);
  temperature = constrain(temperature, MIN_TEMP, MAX_TEMP);
  
  // Envoi JSON vers Python
  Serial.print("{");
  Serial.print("\"voltage\":");
  Serial.print(voltage, 2);
  Serial.print(",\"current\":");
  Serial.print(current, 2);
  Serial.print(",\"temperature\":");
  Serial.print(temperature, 1);
  Serial.println("}");
  
  delay(100);  // 10 lectures par seconde
}

float map_float(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

float average(float* arr, int size) {
  float sum = 0;
  for (int i = 0; i < size; i++) {
    sum += arr[i];
  }
  return sum / size;
}