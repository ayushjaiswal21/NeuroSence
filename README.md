# 🧠 NeuroSence
**Real-Time Cognitive Load & Mental Stress Detection via Edge AI (TinyML)**

---

## 🌟 Our Vision & Idea
The core vision of **NeuroSence** is to build a **100% offline, zero-latency wearable IoT system** that continuously monitors a user's cognitive load and mental stress levels in real-time. 

Unlike modern health applications that rely on constant Wi-Fi connections, heavy cloud computing (AWS/GCP), or third-party APIs which compromise user privacy and drain battery—NeuroSence pushes the "intelligence" directly to the edge. By running a Machine Learning model locally on a microcontroller, we ensure absolute data privacy, instantaneous computing, and high reliability regardless of internet connectivity.

---

## 🛠️ The Engine: Sensors & Tools
To achieve this, NeuroSence bridges embedded systems engineering with data science (TinyML).

### Hardware Stack
*   **ESP32 Microcontroller:** The "brain" of the wearable. It executes the math locally and houses the Machine Learning model in its SRAM.
*   **MAX30102 Pulse Oximeter:** An I2C sensor measuring blood volume pulses (PPG). We calculate **Heart Rate (HR)** and **Heart Rate Variability (HRV)**, specifically the RMSSD (Root Mean Square of Successive Differences).
*   **Analog GSR Sensor:** Measures Galvanic Skin Response (micro-sweat). This detects spikes in electrodermal activity when the sympathetic nervous system's "fight or flight" response activates.

### Software Stack
*   **Data Science:** Python, `pandas`, and `scikit-learn` to analyze the SWELL-KW dataset and train the Random Forest Classifier.
*   **TinyML (`micromlgen`):** Porting the heavy Python Machine Learning model into a lightweight, pure `C++` header file (`model.h`) that natively runs on the ESP32.
*   **Embedded C++:** Bare-metal logic (Arduino IDE) for polling the sensors and running the inference loop.
*   **Web Dashboard:** A Flask backend paired with a Vanilla CSS "Glassmorphism" frontend to visualize live telemetry.

---

## ⚙️ System Architecture & Synopsis (How It Works)
The system operates in a continuous, localized loop designed to maximize efficiency and privacy:

1.  **Continuous Polling:** The ESP32 constantly reads blood volume pulses from the MAX30102.
2.  **On-Device Feature Engineering:** Instead of complex and heavy server-side processing, the ESP32 calculates a 10-beat rolling window to find the exact milliseconds between heartbeats (P-P intervals). It uses this to calculate the **HR** and **RMSSD**. Concurrently, it reads the voltage from the **GSR** sensor.
3.  **Local AI Inference:** The ESP32 feeds this array of 3 exact features `[HR, RMSSD, GSR]` into the `RandomForestModel.predict()` function executing locally in microseconds.
4.  **Sensor Fusion Validation:** If the AI model detects "Stress" based on HRV, the code performs a secondary check against the GSR sensor. If the GSR voltage is also elevated, it confirms the stress alert and eliminates false positives.
5.  **Zero-Cost Alert System (BLE Hijack):** Upon confirmed stress, the ESP32 briefly awakens its Bluetooth (BLE) broadcasting a hidden SSID (`EDGEMIND_ALERT`). An Android phone running MacroDroid detects this connection intent, intercepts it, and automatically dispatches an **Email/SMS** to a designated doctor, while simultaneously pushing a webhook to the Flask Web App Dashboard. 

---

## 🎯 Primary Use Cases
1. **High-Stress Knowledge Workers:** Day traders, software engineers, and air traffic controllers can wear NeuroSence to recognize burnout periods and optimize focus.
2. **Clinical Psychology & Therapy:** Doctors can remotely monitor the cognitive load of patients actively undergoing exposure therapy or managing anxiety disorders.
3. **Student Academic Monitoring:** Recognizing peak cognitive overload during intense studying or exams, helping students schedule neurologically-backed breaks.
4. **Driver Fatigue & Alertness:** Preventing accidents by alerting commercial truck drivers when their HRV drops and cognitive strain reaches dangerous thresholds.

---

## 🚀 Future Scope
NeuroSence is built to scale. The future roadmap includes:
* **Advanced Neural Networks:** Upgrading the Random Forest classifier to a quantized 1D Convolutional Neural Network (CNN) using TensorFlow Lite for Microcontrollers (TFLite Micro).
* **Miniaturization:** Moving from standard ESP32 development boards to an integrated custom PCB (Printed Circuit Board) incorporating an ESP32-C3 or ESP32-S3 for smartwatch-scale form factors.
* **Closed-Loop Biofeedback:** Utilizing the stress prediction loop to trigger physical interventions, such as turning on cooling haptic motors or playing binaural beats to actively lower the user's heart rate.
* **Federated Learning:** Allowing the device to constantly update its local Random Forest model weights based on the user's specific, personal baseline over a period of 30 days without ever sending the raw data to the cloud.

---

## 📁 Repository Structure
- `/EdgeMind/EdgeMind.ino`: The main embedded C++ script for the ESP32 logic.
- `/EdgeMind/model.h`: The compiled TinyML decision tree exported from Python.
- `/dashboard/`: Contains the Flask Python backend `app.py` and the Glassmorphism HTML/CSS UI for webhook ingestion.
- `train_model.py`: The data-science pipeline to extract SWELL-KW HRV/GSR features and train the core AI model.
