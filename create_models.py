"""
Generate dummy/trained ML models for crop and fertilizer recommendation.
This creates the missing trained models using scikit-learn.
"""
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

os.chdir('D:\\Smart_Farming_Assistant\\smart_farming')

# ============ CROP MODEL ============
print("Creating crop recommendation model...")

# Training data - synthetic but realistic
X_train = np.array([
    [60, 60, 60, 20, 70, 7.0, 100],    # Nitrogen, Phosphorus, Potassium, Temp, Humidity, pH, Rainfall
    [50, 40, 50, 18, 75, 6.5, 120],
    [80, 50, 40, 25, 60, 8.0, 80],
    [40, 50, 60, 22, 80, 5.5, 110],
    [60, 60, 60, 20, 70, 7.0, 100],
    [50, 40, 50, 18, 75, 6.5, 120],
    [80, 50, 40, 25, 60, 8.0, 80],
    [40, 50, 60, 22, 80, 5.5, 110],
])

# Crop labels
crop_labels = np.array(['Rice', 'Maize', 'Wheat', 'Chickpea', 'Rice', 'Maize', 'Wheat', 'Chickpea'])

# Train model
crop_model = RandomForestClassifier(n_estimators=10, random_state=42)
crop_model.fit(X_train, crop_labels)

# Save model
os.makedirs('ml_models/crop', exist_ok=True)
with open('ml_models/crop/crop_recommendation_model.pkl', 'wb') as f:
    pickle.dump(crop_model, f)
print("✓ Crop model saved")

# Encoder for labels
encoder = LabelEncoder()
encoder.fit(crop_labels)
with open('ml_models/crop/crop_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)
print("✓ Crop encoder saved")

# ============ FERTILIZER MODEL ============
print("\nCreating fertilizer recommendation model...")

# Fertilizer training data
X_fert_train = np.array([
    [60, 40, 50, 0],    # N, P, K, soil_idx
    [50, 40, 50, 1],
    [80, 50, 40, 2],
    [40, 50, 60, 3],
    [60, 40, 50, 4],
    [50, 40, 50, 0],
    [80, 50, 40, 1],
    [40, 50, 60, 2],
])

# Fertilizer labels
fertilizer_labels = np.array([
    'Balanced NPK Fertilizer',
    'Compost',
    'Urea',
    'DAP',
    'Organic Fertilizer',
    'Balanced NPK Fertilizer',
    'Gypsum',
    'Muriate of Potash'
])

# Train model
fertilizer_model = RandomForestClassifier(n_estimators=10, random_state=42)
fertilizer_model.fit(X_fert_train, fertilizer_labels)

# Save model
os.makedirs('ml_models/fertilizer', exist_ok=True)
with open('ml_models/fertilizer/fertilizer_recommendation_model.pkl', 'wb') as f:
    pickle.dump(fertilizer_model, f)
print("✓ Fertilizer model saved")

# Save fertilizer encoder
fert_encoder = LabelEncoder()
fert_encoder.fit(fertilizer_labels)
with open('ml_models/fertilizer/fertilizer_encoder.pkl', 'wb') as f:
    pickle.dump(fert_encoder, f)
print("✓ Fertilizer encoder saved")

# Save soil encoder
soil_types = np.array(['Acidic', 'Alkaline', 'Loamy', 'Neutral', 'Peaty'])
soil_encoder = LabelEncoder()
soil_encoder.fit(soil_types)
with open('ml_models/fertilizer/soil_encoder.pkl', 'wb') as f:
    pickle.dump(soil_encoder, f)
print("✓ Soil encoder saved")

print("\n✓ All models created successfully!")
