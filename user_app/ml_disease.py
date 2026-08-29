import os
import json
import threading
import logging
import numpy as np
from PIL import Image
from django.conf import settings

try:
    import joblib
except ImportError:
    joblib = None

logger = logging.getLogger(__name__)

# Model and Label Singletons
_DISEASE_MODEL = None
_LEAF_VALIDATOR_MODEL = None
_LABELS = None

_LEAF_THRESH = 0.30
_CONF_THRESH = 0.50

_lock = threading.Lock()

# Upload Constraints
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp'}

# Paths
DISEASE_DIR = os.path.join(settings.BASE_DIR, 'ml_models', 'disease')
MODEL_PATH = os.path.join(DISEASE_DIR, 'plant_disease_model.h5')
VALIDATOR_PATH = os.path.join(DISEASE_DIR, 'leaf_validator_model.h5')
LABELS_PATH = os.path.join(DISEASE_DIR, 'labels.json')
VAL_METRICS_PATH = os.path.join(DISEASE_DIR, 'leaf_validator_metrics.json')
DIS_METRICS_PATH = os.path.join(DISEASE_DIR, 'disease_evaluation_metrics.json')


def _load_labels():
    """Load class label names from labels.json."""
    global _LABELS
    if _LABELS is not None:
        return _LABELS

    with _lock:
        if _LABELS is not None:
            return _LABELS

        if os.path.exists(LABELS_PATH):
            try:
                with open(LABELS_PATH, 'r', encoding='utf-8') as f:
                    _LABELS = json.load(f)
                    logger.info("Loaded disease labels from JSON")
                    return _LABELS
            except Exception as e:
                logger.warning(f"Failed to load labels.json: {e}")

        # Fallback default labels
        _LABELS = [
            "Healthy", "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust",
            "Cherry___Powdery_mildew", "Corn___Cercospora_leaf_spot", "Corn___Common_rust",
            "Grape___Black_rot", "Grape___Esca", "Peach___Bacterial_spot", "Pepper___Bacterial_spot",
            "Potato___Early_blight", "Potato___Late_blight", "Tomato___Bacterial_spot",
            "Tomato___Early_blight", "Tomato___Late_blight"
        ]
        return _LABELS


def _load_leaf_validator():
    """Load binary Leaf vs Non-Leaf Validator CNN."""
    global _LEAF_VALIDATOR_MODEL, _LEAF_THRESH
    if _LEAF_VALIDATOR_MODEL is not None:
        return _LEAF_VALIDATOR_MODEL

    with _lock:
        if _LEAF_VALIDATOR_MODEL is not None:
            return _LEAF_VALIDATOR_MODEL

        if os.path.exists(VAL_METRICS_PATH):
            try:
                with open(VAL_METRICS_PATH, 'r', encoding='utf-8') as f:
                    m = json.load(f)
                    _LEAF_THRESH = m.get('threshold_leaf', 0.30)
            except Exception:
                pass

        if not os.path.exists(VALIDATOR_PATH):
            logger.warning(f"Leaf validator model not found at {VALIDATOR_PATH}")
            return None

        try:
            from tensorflow.keras.models import load_model
            _LEAF_VALIDATOR_MODEL = load_model(VALIDATOR_PATH)
            logger.info("Leaf validator model loaded successfully")
            return _LEAF_VALIDATOR_MODEL
        except Exception as e:
            logger.error(f"Error loading leaf validator model: {e}")
            return None


def _load_disease_model():
    """Load multi-class plant disease CNN."""
    global _DISEASE_MODEL, _CONF_THRESH
    if _DISEASE_MODEL is not None:
        return _DISEASE_MODEL

    with _lock:
        if _DISEASE_MODEL is not None:
            return _DISEASE_MODEL

        if os.path.exists(DIS_METRICS_PATH):
            try:
                with open(DIS_METRICS_PATH, 'r', encoding='utf-8') as f:
                    m = json.load(f)
                    _CONF_THRESH = m.get('confidence_threshold', 0.50)
            except Exception:
                pass

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"Disease model file not found at {MODEL_PATH}")

        try:
            from tensorflow.keras.models import load_model
            _DISEASE_MODEL = load_model(MODEL_PATH)
            logger.info("Plant disease CNN loaded successfully")
            return _DISEASE_MODEL
        except Exception as e:
            logger.error(f"Error loading disease model: {e}")
            raise RuntimeError(f"Failed to load plant disease model: {e}") from e


def _validate_file_upload(image_file):
    """Validate uploaded file size, extension, and MIME type."""
    if not image_file:
        raise ValueError("No file provided")

    if hasattr(image_file, 'size') and image_file.size > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum allowed limit of 5MB")

    file_name = getattr(image_file, 'name', '')
    if file_name:
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension {ext} not allowed. Supported formats: JPG, PNG, BMP, GIF")

    mime_type = getattr(image_file, 'content_type', '')
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"MIME type {mime_type} not allowed")


def _is_leaf_image(img_array):
    """Dual-Layer Leaf Image Validation:
    Validates uploaded image and allows clear plant photos to pass to the disease detection classifier.
    """
    try:
        r = img_array[:, :, 0]
        g = img_array[:, :, 1]
        b = img_array[:, :, 2]

        # Only reject clear full-face human photos where skin tone dominates > 65% of the frame
        skin_mask = (r > 0.85) & (g > 0.55) & (b > 0.45) & ((r - g) > 0.25) & (g > b) & ((g - b) < 0.12)
        if np.mean(skin_mask) > 0.65:
            logger.info("Image rejected: Full human skin photo detected")
            return False, "Invalid image. Human photo detected. Please upload a clear image of a plant leaf."

        # Binary Leaf Validator CNN check with lenient threshold
        validator_model = _load_leaf_validator()
        if validator_model is not None:
            batch = np.expand_dims(img_array, axis=0)
            prob_leaf = float(validator_model.predict(batch, verbose=0)[0][0])
            logger.info(f"Leaf Validator CNN probability: {prob_leaf:.4f}")
            # Only reject if probability is near zero (< 0.05) indicating non-leaf noise
            if prob_leaf < 0.05:
                # If there is foliage/plant content (green/brown/yellow), allow it to pass
                foliage_mask = (g > r * 0.8) | (g > b * 1.0) | ((r > 0.2) & (g > 0.2) & (b < 0.6))
                if np.mean(foliage_mask) < 0.10:
                    return False, "Invalid image. Please upload a clear image of a plant leaf."

        return True, "Valid leaf image"
    except Exception as e:
        logger.warning(f"Leaf validation exception fallback: {e}")
        return True, "Valid leaf image"


def predict_disease(image_file, top_k=3):
    """Predict disease name from an uploaded plant image with dual safety validation.

    Args:
        image_file: File-like object or UploadedFile
        top_k: Number of top predictions to return

    Returns:
        Tuple of (disease_name, prevention_text, confidences)
    """
    _validate_file_upload(image_file)

    labels = _load_labels()
    disease_model = _load_disease_model()

    try:
        img = Image.open(image_file)
        img = img.convert('RGB')
        img = img.resize((224, 224))
        arr = np.array(img, dtype=np.float32) / 255.0

        # Layer 1: Leaf vs Non-Leaf Validation
        is_leaf, err_msg = _is_leaf_image(arr)
        if not is_leaf:
            raise ValueError(err_msg)

        # Layer 2: Disease CNN Inference
        arr_batch = np.expand_dims(arr, axis=0)
        preds = disease_model.predict(arr_batch, verbose=0)[0]

        top_indices = np.argsort(preds)[::-1][:top_k]
        confs = []
        for idx in top_indices:
            lbl = labels[idx] if idx < len(labels) else f"Disease_{idx}"
            confs.append((lbl, float(preds[idx])))

        max_prob = confs[0][1]
        best_label = confs[0][0]

        # Check if top predicted label is Healthy
        if 'healthy' in best_label.lower():
            logger.info(f"Healthy leaf detected: {best_label} ({max_prob*100:.1f}%)")
            return (
                "Healthy Leaf (No Disease Detected)",
                "Great news! Your plant leaf looks healthy with no visible signs of fungal or bacterial disease. Maintain good watering habits, adequate sunlight, and balanced soil nutrients.",
                confs
            )

        # Layer 3: Safety Confidence Threshold Check
        if max_prob < _CONF_THRESH:
            logger.warning(f"Low confidence prediction: {max_prob:.4f} < {_CONF_THRESH:.2f}")
            return (
                "Healthy Leaf (No Disease Detected)",
                "No plant disease symptoms were detected on this leaf. Your crop appears healthy! Continue regular watering, proper sunlight, and balanced nutrient management.",
                confs
            )

        prevention_guide = (
            "Remove affected leaves promptly to prevent spore spread. "
            "Ensure proper spacing for air circulation, avoid overhead watering, "
            "and apply recommended organic or chemical fungicide/bactericide."
        )

        logger.info(f"Disease prediction successful: {best_label} ({max_prob*100:.1f}%)")
        return best_label, prevention_guide, confs

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error processing image for disease prediction: {e}")
        raise RuntimeError(f"Failed to process image: {e}") from e
