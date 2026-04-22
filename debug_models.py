import pickle
import numpy as np
import os

os.chdir('D:\\Smart_Farming_Assistant\\smart_farming')

# Check crop model
print("=== CROP MODEL ===")
with open('ml_models/crop/crop_recommendation_model.pkl', 'rb') as f:
    crop_model = pickle.load(f)
    print(f"Type: {type(crop_model)}")
    if isinstance(crop_model, np.ndarray):
        print(f"Shape: {crop_model.shape}")
        print(f"Content (first 5): {crop_model[:5] if len(crop_model) >= 5 else crop_model}")
    else:
        print(f"Has predict: {hasattr(crop_model, 'predict')}")
        print(f"Dir: {[x for x in dir(crop_model) if not x.startswith('_')][:10]}")

# Check encoder
print("\n=== CROP ENCODER ===")
with open('ml_models/crop/crop_encoder.pkl', 'rb') as f:
    encoder = pickle.load(f)
    print(f"Type: {type(encoder)}")
    if isinstance(encoder, np.ndarray):
        print(f"Shape: {encoder.shape}")
        print(f"Content (first 5): {encoder[:5] if len(encoder) >= 5 else encoder}")
    else:
        print(f"Has inverse_transform: {hasattr(encoder, 'inverse_transform')}")
        print(f"Dir: {[x for x in dir(encoder) if not x.startswith('_')][:10]}")
