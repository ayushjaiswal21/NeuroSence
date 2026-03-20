#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "MAX30105.h" 
#include "heartRate.h"
#include "model.h"

// --- Configuration ---
const char* ssid = "YOUR_HOTSPOT_NAME";
const char* password = "YOUR_HOTSPOT_PASSWORD";
const char* serverName = "http://192.168.X.X:5000/webhook"; // Replace with your laptop's IPv4 address

const int GSR_PIN = 34;
float baseline_gsr = 0.0; // Dynamic baseline

// MAX30102 Sensor
MAX30105 particleSensor;

// --- FEATURE ENGINEERING BUFFERS ---
const byte RATE_SIZE = 10; // 10-beat rolling window for HR & RMSSD
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;

// RMSSD calculations
int rrIntervals[RATE_SIZE]; 

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

void setup() {
    Serial.begin(115200);
    pinMode(GSR_PIN, INPUT);
    
    // 1. Connect to Wi-Fi Hostpot
    Serial.print("Connecting to Wi-Fi");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to Wi-Fi!");

    // 2. DYNAMIC GSR CALIBRATION (The Bug Fix)
    Serial.println("Calibrating GSR Baseline. Please remain still for 10 seconds...");
    long gsr_sum = 0;
    for (int i = 0; i < 10; i++) {
        gsr_sum += analogRead(GSR_PIN);
        delay(1000);
    }
    baseline_gsr = (gsr_sum / 10.0) * (3.3 / 4095.0);
    Serial.print("Calibration Complete. Personal Baseline: ");
    Serial.println(baseline_gsr);
    
    // Initialize MAX30102 here...
    if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
      Serial.println("MAX30102 was not found. Please check wiring/power.");
      while (1);
    }
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A); // Turn Red LED to low to indicate sensor is running
    particleSensor.setPulseAmplitudeGreen(0); // Turn off Green LED
}

void loop() {
    long irValue = particleSensor.getIR();
    bool window_complete = false;

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
        
        if (rateSpot >= (RATE_SIZE - 1)) {
            window_complete = true;
        }
        
        rateSpot %= RATE_SIZE; // Wrap indicator

        // Take mean of HR
        beatAvg = 0;
        for (byte x = 0 ; x < RATE_SIZE ; x++)
          beatAvg += rates[x];
        beatAvg /= RATE_SIZE;
      }
    }
    
    if (window_complete) {
        // Extract Features
        float current_bpm = (float)beatAvg; 
        float current_rmssd = calculateRMSSD(rrIntervals, RATE_SIZE); 
        int raw_gsr = analogRead(GSR_PIN);
        float current_gsr = raw_gsr * (3.3 / 4095.0);
        
        // Calculate GSR Spike (Percentage above dynamic baseline)
        float gsr_spike = current_gsr - baseline_gsr;
        
        // Feed into TinyML Model
        float features[] = {current_bpm, current_rmssd, gsr_spike};
        RandomForestModel rf;
        int stress_prediction = rf.predict(features);
        
        // SEND WEBHOOK TO LAPTOP DASHBOARD
        if (WiFi.status() == WL_CONNECTED) {
            HTTPClient http;
            http.begin(serverName);
            http.addHeader("Content-Type", "application/json");
            
            // Build lightweight JSON payload without heavy libraries
            String jsonPayload = "{\"bpm\":" + String(current_bpm) + 
                                 ",\"rmssd\":" + String(current_rmssd) + 
                                 ",\"gsr\":" + String(current_gsr) + 
                                 ",\"stress\":" + String(stress_prediction) + "}";
            
            int httpResponseCode = http.POST(jsonPayload);
            
            if (httpResponseCode > 0) {
                Serial.print("Data Sent to Dashboard. Response: ");
                Serial.println(httpResponseCode);
            } else {
                Serial.print("Error sending payload: ");
                Serial.println(httpResponseCode);
            }
            http.end();
        }
    }
}
