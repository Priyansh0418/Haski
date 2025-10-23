import os
from typing import Union
import json


def analyze_image(image: Union[bytes, str]) -> dict:
    """Analyze an image and return classification results.

    Args:
        image: either raw image bytes or a filesystem path to an image file

    Returns:
        dict with analysis result (mock for Phase 0)

    TODO:
    - Replace mock with model loading and inference (PyTorch/TensorFlow)
    - Normalize input (resize, crop) and perform augmentation if needed
    - Return structured confidences and condition localization where available
    """
    # Accept path or bytes. If path provided, read bytes (for compatibility).
    if isinstance(image, str):
        if not os.path.exists(image):
            raise FileNotFoundError(f"Image path not found: {image}")
        with open(image, 'rb') as f:
            data = f.read()
    else:
        data = image

    # Mock response for now
    result = {
        "skin_type": "combination",
        "hair_type": "wavy",
        "conditions_detected": ["mild_acne"],
        "confidence_scores": {"skin_type": 0.84, "hair_type": 0.76, "mild_acne": 0.67},
    }

    # Keep for future: persist result to JSON file for debugging
    try:
        debug_dir = os.getenv('ML_DEBUG_DIR')
        if debug_dir:
            os.makedirs(debug_dir, exist_ok=True)
            with open(os.path.join(debug_dir, 'last_analysis.json'), 'w') as fh:
                json.dump(result, fh)
    except Exception:
        pass

    return result


def analyze_image_local(image_path: str) -> dict:
    """Analyze an image file on local disk and return a mock analysis.

    This is a simple local-only stub used by the frontend/backend integration while
    real model inference is developed.

    Returns the following JSON structure (mock):
    {
      "skin_type": "combination",
      "hair_type": "wavy",
      "conditions_detected": ["mild_acne"],
      "confidence_scores": {"skin_type": 0.84, "hair_type": 0.76, "mild_acne": 0.67},
      "model_version": "v0-mock"
    }
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image path not found: {image_path}")

    # In future replace with actual model inference using the file at image_path
    mock = {
        "skin_type": "combination",
        "hair_type": "wavy",
        "conditions_detected": ["mild_acne"],
        "confidence_scores": {"skin_type": 0.84, "hair_type": 0.76, "mild_acne": 0.67},
        "model_version": "v0-mock",
    }

    # Optionally write debug output
    try:
        debug_dir = os.getenv("ML_DEBUG_DIR")
        if debug_dir:
            os.makedirs(debug_dir, exist_ok=True)
            with open(os.path.join(debug_dir, "last_analysis_local.json"), "w") as fh:
                json.dump(mock, fh)
    except Exception:
        pass

    return mock
