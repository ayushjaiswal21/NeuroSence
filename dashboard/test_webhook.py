import requests
import time
import random

WEBHOOK_URL = "http://localhost:5000/api/update"

print("--- EdgeMind MacroDroid Webhook Simulator ---")
print("Waiting 12 seconds for Browser Subagent to open page...")
time.sleep(12)
print("We will simulate a normal state for 5 seconds, followed by a HIGH STRESS alert.")

# 1. Normal State
print("\n[Sending Normal State]")
data_normal = {
    "hr": random.randint(65, 80),
    "rmssd": random.uniform(25.0, 45.0),
    "gsr": random.uniform(0.2, 0.6),
    "stress_alert": False
}
try:
    res = requests.post(WEBHOOK_URL, json=data_normal)
    print("Server Response:", res.json())
except Exception as e:
    print("Ensure the Flask app (app.py) is running! Error:", e)

time.sleep(5)

# 2. Stress State
print("\n[Sending HIGH STRESS Alert]")
data_stress = {
    "hr": random.randint(95, 120),
    "rmssd": random.uniform(10.0, 20.0),
    "gsr": random.uniform(1.8, 2.5),
    "stress_alert": True
}
try:
    res = requests.post(WEBHOOK_URL, json=data_stress)
    print("Server Response:", res.json())
except Exception as e:
    print("Error:", e)
