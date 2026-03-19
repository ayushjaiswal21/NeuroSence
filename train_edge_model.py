import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from micromlgen import port
import os

data_path = "d:/NeuroSence/data/hrv dataset/data/final/train_binary.csv"
print(f"Loading data from {data_path}...")
df = pd.read_csv(data_path)

# Downsample to avoid memory issues and speed up
if len(df) > 50000:
    df = df.sample(50000, random_state=42)

# Selected features: time-domain only for easy embedded calculation
# MEAN_RR directly corresponds to BPM
# RMSSD is standard HRV metric easily calculated on ESP32
features = ['MEAN_RR', 'RMSSD']
X = df[features]
y = df['stress_label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Edge AI Random Forest...")
# Keep it small for memory constraints on ESP32
# Low estimators and constrained max depth ensure the C++ file fits in flash memory
clf = RandomForestClassifier(n_estimators=10, max_depth=8, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print(f"Edge Model Accuracy (Time-Domain Only): {accuracy:.4f}")

print("Exporting model to C++ using micromlgen...")
# Convert to C++
cpp_code = port(clf)

model_path = "d:/NeuroSence/model.h"
with open(model_path, "w") as f:
    f.write(cpp_code)
    
print(f"Successfully generated {model_path}!")
