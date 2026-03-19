import pandas as pd
import os

data_path = "d:/NeuroSence/data/hrv dataset/data/final/train.csv"

# Check if file exists
if not os.path.exists(data_path):
    print(f"File not found: {data_path}")
    exit(1)

df = pd.read_csv(data_path)

print("--- Dataset Exploration ---")
print("Dataset Shape:", df.shape)
print("\nTarget Variable 'condition' Distribution:")
print(df['condition'].value_counts())

# Mapping to binary Stress vs No Stress
# The paper usually uses 'no stress', 'time pressure', 'interruption'
df['stress_label'] = df['condition'].apply(lambda x: 0 if 'no stress' in str(x).lower() else 1)

print("\nBinary Target 'stress_label' Distribution:")
print(df['stress_label'].value_counts())

print("\nMissing Values:")
missing = df.isnull().sum()
if missing[missing > 0].empty:
    print("No missing values found.")
else:
    print(missing[missing > 0])

print("\nKey HRV Features Info:")
features = ['MEAN_RR', 'SDRR', 'RMSSD', 'pNN50', 'VLF', 'LF', 'HF', 'LF_HF_ratio', 'LF_HF']
# Let's see if these exist
available_features = [f for f in features if f in df.columns]
print("Available Key Features:", available_features)

print("\nOverview of Key Features:")
print(df[available_features].describe())

# Save preprocessed version
output_path = "d:/NeuroSence/data/hrv dataset/data/final/train_binary.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved binary-labeled dataset to: {output_path}")
