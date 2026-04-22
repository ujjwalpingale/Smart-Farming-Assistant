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
            return list(joblib.load(file_path))
        else:
            import pickle
            with open(file_path, 'rb') as f:
                return list(pickle.load(f))
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

# Lazy model loader and cache
_MODEL = None


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

    # Prepare feature vector. Many historical artifacts expect features in a specific order.
    # We'll support common simple case: model expects [nitrogen, phosphorus, potassium] or accepts extra features.
    # If model.n_features_in_ is present, fill missing features with zeros.
    try:
        n_features = getattr(model, 'n_features_in_', None)
        if n_features is None:
            # Try to predict with minimal features
            feat = [[nitrogen, phosphorus, potassium]]
        else:
            # Create a vector of length n_features, fill with zeros and place known values in common positions
            feat = [np.zeros(n_features, dtype=float).tolist()]
            # heuristic placement: try to put N,P,K near the end if too many features
            if n_features >= 3:
                feat[0][0] = nitrogen
                feat[0][1] = phosphorus
                feat[0][2] = potassium
            else:
                # fallback: just fill first slots
                for i, v in enumerate([nitrogen, phosphorus, potassium][:n_features]):
                    feat[0][i] = v
        pred = model.predict(feat)
        # If prediction is numeric index, try to map to fertilizer_list
        try:
            if isinstance(pred, (list, tuple, np.ndarray)):
                pval = pred[0]
            else:
                pval = pred
            # If it's integer index
            if isinstance(pval, (int, np.integer)):
                idx = int(pval)
                if 0 <= idx < len(fertilizer_list):
                    return fertilizer_list[idx]
            # If it's already string
            if isinstance(pval, str):
                return pval
            # If it's array-like label
            return str(pval)
        except Exception:
            return str(pred)
    except Exception as e:
        warnings.warn(f"Model prediction failed: {e}")
        return None


def predict_fertilizer(data):
    """Fertilizer recommendation.

    Attempts to use a trained model if present; otherwise falls back to heuristics.
    data: [nitrogen, phosphorus, potassium, soil (optional string)]
    """
    try:
        nitrogen = float(data[0])
        phosphorus = float(data[1])
        potassium = float(data[2])
    except Exception:
        return fertilizer_list[0]

    soil = None
    if len(data) > 3:
        soil = data[3]

    # Try model first
    model_rec = _use_model_predict(nitrogen, phosphorus, potassium, soil=soil)
    if model_rec:
        return model_rec

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

    return rec
