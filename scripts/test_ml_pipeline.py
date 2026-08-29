import os
import io
import sys
import numpy as np
from PIL import Image

# Add project root directory to path & setup Django settings
sys.path.insert(0, 'D:\\Smart_Farming_Assistant\\smart_farming')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_farming.settings')

import django
django.setup()

from user_app.ml_crop import predict_crop
from user_app.ml_fertilizer import predict_fertilizer
from user_app.ml_disease import predict_disease

def test_crop_pipeline():
    print("\n--- 1. Testing Crop Recommendation Pipeline ---")
    sample_inputs = [
        [90, 42, 43, 20.8, 82.0, 6.5, 202.9], # Expected Rice/Jute
        [20, 60, 80, 18.5, 16.0, 7.0, 75.0],   # Expected Chickpea
        [100, 40, 20, 25.0, 80.0, 6.5, 75.0]   # Expected Cotton/Maize
    ]
    
    for idx, inp in enumerate(sample_inputs, 1):
        top3 = predict_crop(inp)
        print(f"Sample {idx} Input: {inp}")
        print(f" -> Top 3 Crop Predictions: {top3}")
        assert isinstance(top3, list) and len(top3) == 3, "Crop prediction output must return top 3 crops"
    print("[PASS] Crop Recommendation Pipeline Verified!")

def test_fertilizer_pipeline():
    print("\n--- 2. Testing Fertilizer Recommendation Pipeline ---")
    samples = [
        ([30, 50, 50, 'Acidic'], "Acidic Soil sample"),
        ([80, 20, 50, 'Neutral'], "High Nitrogen sample"),
        ([30, 30, 80, 'Loamy'], "High Potassium sample"),
        ([70, 70, 70, 'Loamy'], "Balanced NPK sample")
    ]
    
    for data, desc in samples:
        recs = predict_fertilizer(data)
        print(f"Test ({desc}): {data} => Recommendations: {recs}")
        assert isinstance(recs, list) and len(recs) > 0, "Fertilizer prediction must return recommendations"
    print("[PASS] Fertilizer Recommendation Pipeline Verified!")

def test_disease_pipeline():
    print("\n--- 3. Testing Plant Disease & Leaf Validation Pipeline ---")
    
    # Helper to create memory image byte stream
    def make_img_bytes(img_arr):
        buf = io.BytesIO()
        img = Image.fromarray((img_arr * 255).astype(np.uint8))
        img.save(buf, format='JPEG')
        buf.seek(0)
        buf.name = 'test_image.jpg'
        return buf

    # Case A: Valid Green Leaf Image
    leaf_arr = np.zeros((224, 224, 3), dtype=np.float32)
    leaf_arr[:, :, 0] = 0.2  # Low Red
    leaf_arr[:, :, 1] = 0.85 # Dominant Green
    leaf_arr[:, :, 2] = 0.15 # Low Blue
    # Add brown spot (Late Blight pattern)
    leaf_arr[80:120, 80:120, 0] = 0.6
    leaf_arr[80:120, 80:120, 1] = 0.3
    
    buf_leaf = make_img_bytes(leaf_arr)
    best, prev, confs = predict_disease(buf_leaf)
    print(f"Valid Leaf Test Result => Best: '{best}' | Confs: {confs[:2]}")
    assert best != "Unknown", "Valid leaf image should return disease prediction"

    # Case B: Human Face / Skin Tone Image (Non-Leaf Rejection Test)
    skin_arr = np.zeros((224, 224, 3), dtype=np.float32)
    skin_arr[:, :, 0] = 0.85 # High Red
    skin_arr[:, :, 1] = 0.65 # Med Green
    skin_arr[:, :, 2] = 0.50 # Low Blue
    
    buf_skin = make_img_bytes(skin_arr)
    try:
        predict_disease(buf_skin)
        assert False, "Non-leaf human image should have been rejected!"
    except ValueError as ve:
        print(f"Rejection Success (Human Face/Skin): '{ve}'")

    # Case C: Blue Sky / Metallic Car Image (Non-Leaf Rejection Test)
    blue_arr = np.zeros((224, 224, 3), dtype=np.float32)
    blue_arr[:, :, 0] = 0.2
    blue_arr[:, :, 1] = 0.5
    blue_arr[:, :, 2] = 0.95 # Dominant Blue Sky
    
    buf_blue = make_img_bytes(blue_arr)
    try:
        predict_disease(buf_blue)
        assert False, "Non-leaf blue background image should have been rejected!"
    except ValueError as ve:
        print(f"Rejection Success (Blue Sky/Car): '{ve}'")

    print("[PASS] Plant Disease & Dual-Layer Leaf Validation Verified!")

def main():
    print("==================================================")
    print("  Smart Farming Assistant - End-to-End ML Tests")
    print("==================================================")
    test_crop_pipeline()
    test_fertilizer_pipeline()
    test_disease_pipeline()
    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == '__main__':
    main()
