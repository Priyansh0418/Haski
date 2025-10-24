"""Inference Module - Unified skin analysis interface"""

from .detector_infer import ConditionDetector, Detection, analyze_detections
from .classifier_infer import SkinTypeClassifier

__all__ = [
    'ConditionDetector',
    'SkinTypeClassifier',
    'Detection',
    'analyze_detections',
]
