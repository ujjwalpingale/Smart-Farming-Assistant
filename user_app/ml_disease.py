import os
from PIL import Image
import numpy as np
import json
import threading
import logging

try:
    import joblib
except ImportError:
    joblib = None

logger = logging.getLogger(__name__)

_MODEL = None
_MODEL_PATH = None
_LABELS = None
_LABELS_PATHS = [
    ('json', 'ml_models/disease/labels.json'),
    ('pkl', 'ml_models/disease/labels.pkl'),
    ('npy', 'ml_models/disease/classes.npy'),
]

# Thread lock for thread-safe model loading
_lock = threading.Lock()

# File upload constraints
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp'}

try:
    from django.conf import settings
    _MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'disease', 'plant_disease_model.h5')
    _LABEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models', 'disease')
except Exception:
    _MODEL_PATH = None
    _LABEL_DIR = None


def _load_labels():
    """Load label names for disease model if available, otherwise generate defaults and write a JSON file."""
    global _LABELS
    if _LABELS is not None:
        return _LABELS
    
    with _lock:
        # Double-check after acquiring lock
        if _LABELS is not None:
            return _LABELS
        
        # try multiple formats
        if _LABEL_DIR:
            # json
            json_path = os.path.join(_LABEL_DIR, 'labels.json')
            pkl_path = os.path.join(_LABEL_DIR, 'labels.pkl')
            npy_path = os.path.join(_LABEL_DIR, 'classes.npy')
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        _LABELS = json.load(f)
                        logger.info('Labels loaded from JSON')
                        return _LABELS
                except Exception as e:
                    logger.warning(f'Error loading labels from JSON: {e}')
            
            if os.path.exists(pkl_path):
                try:
                    if joblib:
                        _LABELS = list(joblib.load(pkl_path))
                    else:
                        import pickle
                        with open(pkl_path, 'rb') as f:
                            _LABELS = list(pickle.load(f))
                    logger.info('Labels loaded from pickle/joblib')
                    return _LABELS
                except Exception as e:
                    logger.warning(f'Error loading labels from pickle: {e}')
            
            if os.path.exists(npy_path):
                try:
                    _LABELS = list(np.load(npy_path, allow_pickle=True))
                    logger.info('Labels loaded from numpy array')
                    return _LABELS
                except Exception as e:
                    logger.warning(f'Error loading labels from numpy: {e}')

        # As a fallback, infer class count from model output shape if model is present
        try:
            model = _load_model()
            out_shape = getattr(model, 'output_shape', None)
            if isinstance(out_shape, tuple) and len(out_shape) >= 2:
                n_classes = out_shape[1]
            else:
                n_classes = 1
        except Exception:
            n_classes = 1

        _LABELS = [f'Disease_{i}' for i in range(n_classes)]
        # write JSON for future convenience
        try:
            if _LABEL_DIR:
                json_path = os.path.join(_LABEL_DIR, 'labels.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(_LABELS, f, indent=2)
        except Exception as e:
            logger.warning(f'Error writing labels to JSON: {e}')

        return _LABELS


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    
    with _lock:
        # Double-check after acquiring lock
        if _MODEL is not None:
            return _MODEL
        
        try:
            # try to import keras (tensorflow)
            from tensorflow.keras.models import load_model
        except Exception as e:
            raise RuntimeError('TensorFlow/Keras is not available in the environment. Install tensorflow to use disease prediction.') from e
        
        if not _MODEL_PATH or not os.path.exists(_MODEL_PATH):
            raise RuntimeError('Disease model file not found at expected location.')
        
        try:
            _MODEL = load_model(_MODEL_PATH)
            logger.info('Disease model loaded successfully')
            return _MODEL
        except Exception as e:
            logger.error(f'Error loading disease model: {e}')
            raise


def _validate_file_upload(image_file):
    """Validate uploaded file before processing.
    
    Args:
        image_file: Uploaded file object
    
    Raises:
        ValueError: If file validation fails
    """
    if not image_file:
        raise ValueError('No file provided')
    
    # Check file size
    if hasattr(image_file, 'size') and image_file.size > MAX_FILE_SIZE:
        raise ValueError(f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB')
    
    # Check file extension
    file_name = getattr(image_file, 'name', '')
    if file_name:
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f'File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}')
    
    # Check MIME type if available
    mime_type = getattr(image_file, 'content_type', '')
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f'MIME type {mime_type} not allowed')


def predict_disease(image_file, top_k=3):
    """Predict disease name from an uploaded image file-like object.

    Args:
        image_file: File-like object or UploadedFile
        top_k: Number of top predictions to return

    Returns:
        Tuple of (disease_name, prevention_text, confidences)
        disease_name: best-guess label (string)
        prevention_text: human-friendly text
        confidences: list of (label, probability) for top_k
    
    Raises:
        ValueError: If file validation fails
        RuntimeError: If model loading or prediction fails
    """
    # Validate file upload
    _validate_file_upload(image_file)
    
    model = None
    try:
        model = _load_model()
    except RuntimeError:
        logger.error('Failed to load disease model')
        raise

    labels = _load_labels()

    # preprocess image to model expected size
    try:
        img = Image.open(image_file)
        img = img.convert('RGB')
        target_size = (224, 224)
        try:
            shape = model.input_shape
            if isinstance(shape, tuple) and len(shape) >= 4:
                target_size = (shape[1], shape[2])
        except Exception:
            pass
        img = img.resize(target_size)
        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, 0)
        preds = model.predict(arr)
        probs = preds[0]
        # top-k
        top_idx = np.argsort(probs)[-top_k:][::-1]
        confs = []
        for i in top_idx:
            label = labels[i] if i < len(labels) else f'Disease_{i}'
            confs.append((label, float(probs[i])))
        best = confs[0][0] if confs else 'Unknown'
        prevention = 'Refer to extension services or consult agricultural specialist for prevention steps.'
        logger.info(f'Disease prediction completed: {best}')
        return best, prevention, confs
    except Exception as e:
        logger.error(f'Error during disease prediction: {str(e)}')
        raise RuntimeError('Failed to preprocess image or predict disease: ' + str(e)) from e
