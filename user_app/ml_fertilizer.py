import os
import warnings
import numpy as np
import threading
import logging
from django.conf import settings

try:
    import joblib
except ImportError:
    joblib = None

logger = logging.getLogger(__name__)

# Thread lock for thread-safe model loading
_lock = threading.Lock()

# Paths to artifacts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'fertilizer', 'fertilizer_recommendation_model.pkl')
ENCODER_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'fertilizer', 'fertilizer_encoder.pkl')
SOIL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'fertilizer', 'soil_encoder.pkl')

# Load encoders (class lists / lookups)
def _safe_load_file(file_path, fallback_list):
    """Safely load pickle/joblib file with fallback."""
    if not os.path.exists(file_path):
        return fallback_list
    
    try:
        if joblib:
            obj = joblib.load(file_path)
        else:
            import pickle
            with open(file_path, 'rb') as f:
                obj = pickle.load(f)
        
        # If it's a LabelEncoder, extract classes
        if hasattr(obj, 'classes_'):
            return list(obj.classes_)
        # If it's already a list or array
        if isinstance(obj, (list, tuple, np.ndarray)):
            return list(obj)
        return fallback_list
    except Exception as e:
        logger.warning(f'Error loading file {file_path}: {str(e)}, using fallback')
        return fallback_list

fertilizer_list = _safe_load_file(
    ENCODER_PATH,
    [
        'Balanced NPK Fertilizer', 'Compost', 'DAP', 'General Purpose Fertilizer',
        'Gypsum', 'Lime', 'Muriate of Potash', 'Organic Fertilizer', 'Urea',
        'Water Retaining Fertilizer'
    ]
)

soil_list = _safe_load_file(
    SOIL_PATH,
    ['Acidic Soil', 'Alkaline Soil', 'Loamy Soil', 'Neutral Soil', 'Peaty Soil']
)

# Lazy model and encoder loader
_MODEL = None
_SOIL_ENCODER = None

def _load_soil_encoder():
    global _SOIL_ENCODER
    if _SOIL_ENCODER is not None:
        return _SOIL_ENCODER
    
    if not os.path.exists(SOIL_PATH):
        return None
        
    try:
        if joblib:
            _SOIL_ENCODER = joblib.load(SOIL_PATH)
        else:
            import pickle
            with open(SOIL_PATH, 'rb') as f:
                _SOIL_ENCODER = pickle.load(f)
        return _SOIL_ENCODER
    except:
        return None


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    
    if not os.path.exists(MODEL_PATH):
        logger.warning(f'Fertilizer model not found at {MODEL_PATH}')
        return None
    
    with _lock:
        # Double-check after acquiring lock
        if _MODEL is not None:
            return _MODEL
        
        try:
            if joblib:
                candidate = joblib.load(MODEL_PATH)
            else:
                logger.warning('joblib not available, attempting pickle')
                import pickle
                with open(MODEL_PATH, 'rb') as f:
                    candidate = pickle.load(f)
        except Exception as e:
            logger.error(f'Failed to load fertilizer model: {e}')
            return None

        # If it's a sklearn estimator, it will have predict
        if hasattr(candidate, 'predict'):
            _MODEL = candidate
            logger.info('Fertilizer model loaded successfully')
            return _MODEL

        # If it's a numpy array of labels/headers, it's not a model
        if isinstance(candidate, (np.ndarray, list)):
            logger.warning('Loaded fertilizer artifact is not a model (numpy/list). Falling back to heuristic.')
            return None

        logger.warning('Unrecognized fertilizer model format; falling back to heuristic.')
        return None


def _use_model_predict(nitrogen, phosphorus, potassium, soil=None):
    model = _load_model()
    if not model:
        return None

    try:
        # Encode soil if provided
        soil_idx = 0
        if soil:
            encoder = _load_soil_encoder()
            if encoder:
                try:
                    if hasattr(encoder, 'transform'):
                        soil_idx = encoder.transform([soil])[0]
                    else:
                        soil_idx = soil_list.index(soil)
                except:
                    soil_idx = 0

        n_features = getattr(model, 'n_features_in_', 4)
        feat = np.zeros((1, n_features))
        
        # Populating features (standard order: N, P, K, Soil)
        if n_features >= 1: feat[0, 0] = nitrogen
        if n_features >= 2: feat[0, 1] = phosphorus
        if n_features >= 3: feat[0, 2] = potassium
        if n_features >= 4: feat[0, 3] = soil_idx
        
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(feat)[0]
            classes = model.classes_
            
            top_indices = np.argsort(probs)[::-1][:3]
            results = []
            for idx in top_indices:
                label = classes[idx]
                if isinstance(label, (int, np.integer)):
                    if 0 <= label < len(fertilizer_list):
                        label = fertilizer_list[label]
                results.append(str(label))
            return results
        else:
            pred = model.predict(feat)[0]
            if isinstance(pred, (int, np.integer)):
                if 0 <= pred < len(fertilizer_list):
                    pred = fertilizer_list[pred]
            return [str(pred)]
            
    except Exception as e:
        warnings.warn(f"Model prediction failed: {e}")
        return None


def predict_fertilizer(data):
    """Fertilizer recommendation.
    Attempts to use a trained model if present; otherwise falls back to heuristics.
    Returns list of top 3 recommendations.
    """
    try:
        nitrogen = float(data[0])
        phosphorus = float(data[1])
        potassium = float(data[2])
    except Exception:
        return [fertilizer_list[0]]

    soil = None
    if len(data) > 3:
        soil = data[3]

    # Try model first
    model_recs = _use_model_predict(nitrogen, phosphorus, potassium, soil=soil)
    if model_recs:
        return model_recs

    # Heuristics fallback
    if nitrogen < 50:
        rec = 'Urea' if 'Urea' in fertilizer_list else fertilizer_list[0]
    elif phosphorus < 40:
        rec = 'DAP' if 'DAP' in fertilizer_list else fertilizer_list[0]
    elif potassium < 40:
        rec = 'Muriate of Potash' if 'Muriate of Potash' in fertilizer_list else fertilizer_list[0]
    else:
        rec = 'Balanced NPK Fertilizer' if 'Balanced NPK Fertilizer' in fertilizer_list else fertilizer_list[0]

    # soil-based adjustments
    if soil:
        s = soil.lower()
        if 'acid' in s or 'acidic' in s:
            rec = 'Lime' if 'Lime' in fertilizer_list else rec
        if 'peat' in s or 'peaty' in s:
            rec = 'Compost' if 'Compost' in fertilizer_list else rec

    return [rec]
