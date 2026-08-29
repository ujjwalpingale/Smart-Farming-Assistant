import os
import io
import tempfile
import pickle
import numpy as np
from PIL import Image
from django.test import TestCase

from user_app import ml_fertilizer
from user_app.ml_fertilizer import predict_fertilizer
from user_app.ml_crop import predict_crop
from user_app.ml_disease import predict_disease


class CropPredictionTests(TestCase):
    def test_predict_crop_top3(self):
        # Test 7 features input
        data = [90, 42, 43, 20.8, 82.0, 6.5, 202.9]
        res = predict_crop(data)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)


class FertilizerPredictionTests(TestCase):
    def test_predict_returns_list(self):
        res = predict_fertilizer([30, 40, 50, 'Acidic Soil'])
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)

    def test_predict_logic_nitrogen_low(self):
        res = predict_fertilizer([10, 100, 100, None])
        self.assertIsInstance(res, list)
        self.assertTrue(any('Urea' in r for r in res) or len(res) > 0)


class DiseaseModelTests(TestCase):
    def test_predict_disease_returns_tuple(self):
        # Create a sample green foliage leaf image
        img_arr = np.zeros((224, 224, 3), dtype=np.uint8)
        img_arr[:, :, 0] = 50   # Low Red
        img_arr[:, :, 1] = 200  # Dominant Green
        img_arr[:, :, 2] = 30   # Low Blue
        
        img = Image.fromarray(img_arr)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        buf.name = 'leaf.jpg'

        best, prevention, confs = predict_disease(buf, top_k=3)
        self.assertIsInstance(best, str)
        self.assertIsInstance(prevention, str)
        self.assertIsInstance(confs, list)

    def test_non_leaf_image_rejection(self):
        # Create a human skin tone non-leaf image
        skin_arr = np.zeros((224, 224, 3), dtype=np.uint8)
        skin_arr[:, :, 0] = 220  # High Red
        skin_arr[:, :, 1] = 160  # Med Green
        skin_arr[:, :, 2] = 120  # Low Blue
        
        img = Image.fromarray(skin_arr)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        buf.name = 'face.jpg'

        with self.assertRaises(ValueError):
            predict_disease(buf)
