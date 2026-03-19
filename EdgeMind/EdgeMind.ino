#include <Wire.h>
#include "MAX30105.h" // SparkFun MAX3010x library
#include "heartRate.h" // SparkFun integrated heart rate
#include "model.h" // TinyML exported RF Model
#include "BluetoothSerial.h"

// --- HARDWARE CONFIG ---
#define GSR_PIN 34 // Analog pin for GSR

// MAX30102 Sensor
MAX30105 particleSensor;

// BLE
BluetoothSerial SerialBT;
unsigned long stressTriggerTime = 0;
bool bluetoothActive = false;

// --- FEATURE ENGINEERING BUFFERS ---
const byte RATE_SIZE = 10; // 10-beat rolling window for HR & RMSSD
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;

// RMSSD calculations
int rrIntervals[RATE_SIZE]; 

void setup() {
  Serial.begin(115200);
  pinMode(GSR_PIN, INPUT);

  Serial.println("Initializing EdgeMind Hardware...");

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 was not found. Please check wiring/power.");
    while (1);
  }

  // Optimize MAX30102 for heart rate
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A); // Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); // Turn off Green LED
  
  Serial.println("System Ready. Waiting for finger...");
}

void loop() {
  long irValue = particleSensor.getIR();

  // 1. Peak Detection & RR Interval Capture
  if (checkForBeat(irValue) == true) {
    // We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      // Store RR intervals for RMSSD and HR for averaging
      rates[rateSpot++] = (byte)beatsPerMinute; 
      rrIntervals[rateSpot-1] = delta;
      
      rateSpot %= RATE_SIZE; // Wrap indicator

      // Take mean of HR
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
      
      // Calculate RMSSD from rolling window
      float rmssd = calculateRMSSD(rrIntervals, RATE_SIZE);
      
      // 2. Read GSR
      float gsrVolts = analogRead(GSR_PIN) * (3.3 / 4095.0);
      
      Serial.print("HR: "); Serial.print(beatAvg);
      Serial.print(" | RMSSD: "); Serial.print(rmssd);
      Serial.print(" | GSR(V): "); Serial.println(gsrVolts);
      
      // 3. TinyML Inference
      float features[3] = {(float)beatAvg, rmssd, gsrVolts};
      RandomForestModel rf;
      int predictedCondition = rf.predict(features);
      
      // 4. Sensor Fusion & BLE Hijack
      // Cond = 1 means Stress. But we strictly require GSR to be > 1.2V to prevent false positives.
      if (predictedCondition == 1 && gsrVolts > 1.2) {
        Serial.println(">>> HIGH COGNITIVE STRESS DETECTED <<<");
        triggerBLEMacroDroid();
      }
    }
  }

  // Handle BLE disable timeout (15 seconds)
  if (bluetoothActive && (millis() - stressTriggerTime > 15000)) {
    Serial.println("Turning Bluetooth OFF to conserve power as MacroDroid intent is registered.");
    SerialBT.end(); 
    bluetoothActive = false;
  }
}

float calculateRMSSD(int* intervals, byte size) {
  if (size < 2) return 0.0;
  float sum_sq_diff = 0;
  int valid_diffs = 0;
  for (int i = 1; i < size; i++) {
    if (intervals[i] > 0 && intervals[i-1] > 0) {
      float diff = intervals[i] - intervals[i-1];
      sum_sq_diff += diff * diff;
      valid_diffs++;
    }
  }
  if (valid_diffs == 0) return 0.0;
  return sqrt(sum_sq_diff / valid_diffs);
}

void triggerBLEMacroDroid() {
  if (!bluetoothActive) {
    Serial.println("Activating BLE Alert SSID: EDGEMIND_ALERT...");
    SerialBT.begin("EDGEMIND_ALERT"); // MacroDroid listens for this specific connection state
    bluetoothActive = true;
    stressTriggerTime = millis();
  }
}
