from django.test import TestCase, override_settings
from . import ml_fertilizer
from .ml_fertilizer import predict_fertilizer
import pickle
import tempfile
import os


class FertilizerPredictionTests(TestCase):
    def test_predict_returns_string(self):
        res = predict_fertilizer([30, 40, 50, 'Acidic Soil'])
        self.assertIsInstance(res, str)

    def test_predict_logic_nitrogen_low(self):
        res = predict_fertilizer([10, 100, 100, None])
        self.assertIn('Urea', res)

    def test_model_integration_when_model_present(self):
        # Create a tiny sklearn model and pickle it to a temp path, then ensure predict_fertilizer picks it up
        try:
            from sklearn.tree import DecisionTreeClassifier
            import numpy as np
        except Exception:
            self.skipTest('sklearn not available')

        X = np.array([[10, 1, 1], [100, 100, 100]])
        y = np.array([8, 0])  # indices into fertilizer list (8 -> 'Urea', 0 -> 'Balanced NPK Fertilizer')
        clf = DecisionTreeClassifier().fit(X, y)

        fd, path = tempfile.mkstemp(suffix='.pkl')
        os.close(fd)
        with open(path, 'wb') as f:
            pickle.dump(clf, f)

        # Point module to this model
        old_path = ml_fertilizer.MODEL_PATH
        old_model = getattr(ml_fertilizer, '_MODEL', None)
        try:
            ml_fertilizer.MODEL_PATH = path
            ml_fertilizer._MODEL = None
            res = predict_fertilizer([10, 1, 1])
            self.assertIsInstance(res, str)
            self.assertIn('Urea', res)
        finally:
            # restore
            ml_fertilizer.MODEL_PATH = old_path
            ml_fertilizer._MODEL = old_model
            os.remove(path)


class DiseaseModelTests(TestCase):
    def test_predict_disease_returns_tuple(self):
        try:
            from user_app.ml_disease import _load_model
        except Exception:
            self.skipTest('TensorFlow or disease model not available')

        # create a small dummy image
        from PIL import Image
        import io
        img = Image.new('RGB', (128,128), color=(255,255,255))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        from user_app.ml_disease import predict_disease
        best, prevention, confs = predict_disease(buf, top_k=3)
        self.assertIsInstance(best, str)
        self.assertIsInstance(prevention, str)
        self.assertIsInstance(confs, list)


    def test_saved_model_file_works_if_present(self):
        # If a saved model exists in the project path, ensure it predicts something sensible for typical inputs.
        model = ml_fertilizer._load_model()
        if model is None:
            self.skipTest('No saved fertilizer model present')
        # test representative inputs
        res = predict_fertilizer([10, 50, 50])
        self.assertIsInstance(res, str)
        res2 = predict_fertilizer([100, 10, 100])
        self.assertIsInstance(res2, str)

