import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from micromlgen import port
import os

def generate_synthetic_gsr(condition_series):
    # Generates a synthetic GSR (Galvanic Skin Response) voltage to match the user architecture
    # Normal: low conductance (0.1 - 0.5V), Stress: high conductance (1.5 - 3.0V)
    np.random.seed(42)
    gsr = []
    for cond in condition_series:
        if cond == 'no stress':
            gsr.append(np.random.uniform(0.1, 0.8))
        else:
            gsr.append(np.random.uniform(1.5, 3.0))
    return gsr

print("Loading dataset...")
train_df = pd.read_csv(r"d:\NeuroSence\swell_data\hrv dataset\data\final\train.csv").sample(n=10000, random_state=42)
test_df = pd.read_csv(r"d:\NeuroSence\swell_data\hrv dataset\data\final\test.csv").sample(n=5000, random_state=42)

print("Processing features...")
# Add synthetic GSR as requested by the ESP32 prediction array requirements
train_df['GSR'] = generate_synthetic_gsr(train_df['condition'])
test_df['GSR'] = generate_synthetic_gsr(test_df['condition'])

# Extract Features: HR, RMSSD, GSR
features = ['HR', 'RMSSD', 'GSR']
X_train = train_df[features].values
X_test = test_df[features].values

# Target: 0 = No Stress, 1 = Stress (Interruption / Time Pressure)
y_train = train_df['condition'].apply(lambda x: 0 if x == 'no stress' else 1).values
y_test = test_df['condition'].apply(lambda x: 0 if x == 'no stress' else 1).values

print("Training lightweight Random Forest for ESP32 (TinyML)...")
# Keep estimators low and depth restricted to fit in ESP32 SRAM
clf = RandomForestClassifier(n_estimators=15, max_depth=5, random_state=42)
clf.fit(X_train, y_train)

print("\n--- Model Evaluation ---")
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=['No Stress (0)', 'Stress (1)']))

print("Exporting model to pure C++ header (model.h)...")
c_code = port(clf, classname="RandomForestModel")

output_path = r"d:\NeuroSence\model.h"
with open(output_path, "w") as f:
    f.write(c_code)

print(f"Success! Model exported to {output_path}")
