import os
import numpy as np
import threading
import logging
from django.conf import settings

try:
    import joblib
except ImportError:
    # Fallback if joblib not available
    joblib = None

logger = logging.getLogger(__name__)

# Thread lock for thread-safe model loading
_lock = threading.Lock()

MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    'ml_models',
    'crop',
    'crop_recommendation_model.pkl'
)

ENCODER_PATH = os.path.join(
    settings.BASE_DIR,
    'ml_models',
    'crop',
    'crop_encoder.pkl'
)

# Load artifacts
_crop_model = None
_crop_encoder = None

def _load_model():
    global _crop_model
    if _crop_model is not None:
        return _crop_model
    
    if not os.path.exists(MODEL_PATH):
        logger.warning(f'Crop model not found at {MODEL_PATH}')
        return None
    
    with _lock:
        # Double-check after acquiring lock
        if _crop_model is not None:
            return _crop_model
        
        try:
            if joblib:
                obj = joblib.load(MODEL_PATH)
            else:
                logger.warning('joblib not available, attempting pickle')
                import pickle
                with open(MODEL_PATH, 'rb') as f:
                    obj = pickle.load(f)
            
            # Check if it's a trained sklearn model
            if hasattr(obj, 'predict'):
                _crop_model = obj
                logger.info('Crop model loaded successfully')
                return _crop_model
            else:
                logger.error('Loaded object is not a valid model')
        except Exception as e:
            logger.error(f'Error loading crop model: {str(e)}')
    
    return None

def _load_encoder():
    global _crop_encoder
    if _crop_encoder is not None:
        return _crop_encoder
    
    if not os.path.exists(ENCODER_PATH):
        logger.warning(f'Crop encoder not found at {ENCODER_PATH}')
        return None
    
    with _lock:
        # Double-check after acquiring lock
        if _crop_encoder is not None:
            return _crop_encoder
        
        try:
            if joblib:
                obj = joblib.load(ENCODER_PATH)
            else:
                logger.warning('joblib not available, attempting pickle')
                import pickle
                with open(ENCODER_PATH, 'rb') as f:
                    obj = pickle.load(f)
            
            # Check if it's a LabelEncoder with inverse_transform
            if hasattr(obj, 'inverse_transform'):
                _crop_encoder = obj
                logger.info('Crop encoder loaded successfully')
                return _crop_encoder
            else:
                logger.error('Loaded object is not a valid encoder')
        except Exception as e:
            logger.error(f'Error loading crop encoder: {str(e)}')
    
    return None

def predict_crop(data):
    """Crop recommendation using trained model.
    
    Args:
        data: List of 7 features [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
    
    Returns:
        Recommended crop name (str)
    """
    if not isinstance(data, (list, tuple)) or len(data) != 7:
        logger.error('Invalid data format for crop prediction')
        raise ValueError('Expected 7 features for crop prediction')
    
    model = _load_model()
    encoder = _load_encoder()
    
    if model is None or encoder is None:
        logger.warning('Model or encoder not available, using fallback')
        return 'Rice'  # Fallback
    
    try:
        # Validate input types
        data = [float(x) for x in data]
        
        # Prepare input as 2D array for sklearn model
        X = np.array([data]).reshape(1, -1)
        prediction = model.predict(X)
        # Use encoder to get readable label
        result = encoder.inverse_transform(prediction)[0]
        return result
    except Exception as e:
        logger.error(f'Crop prediction error: {str(e)}')
        return 'Rice'  # Fallback
