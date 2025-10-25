"""
ML Inference Service for Haski Skin & Hair Classifier

Supports multiple model formats:
- PyTorch (native trained models)
- ONNX (cross-platform)
- TFLite (mobile/edge devices)

Features:
- Automatic model format detection
- Fallback chain: PyTorch → ONNX → TFLite
- Confidence scoring and class mapping
- Batch inference support
- Performance benchmarking
"""

import argparse
import importlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, Tuple, Optional, Union, List
import tempfile
import os

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# PyTorch Model Support
# ============================================================================

class PyTorchInference:
    """PyTorch model inference (native trained models)."""
    
    def __init__(self, model_path: str, class_mapping_path: str):
        """Initialize PyTorch model."""
        try:
            import torch
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            import torch.nn as nn
        except ImportError:
            raise ImportError("torch not installed. Install with: pip install torch torchvision")
        
        logger.info(f"Loading PyTorch model from {model_path}...")
        
        # Load class mapping
        with open(class_mapping_path, 'r') as f:
            self.class_mapping = json.load(f)
        
        # Create reverse mapping (idx -> class_name)
        self.idx_to_class = {int(v): k for k, v in self.class_mapping.items()}
        self.num_classes = len(self.class_mapping)
        
        # Load model architecture
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        self.model.classifier[1] = nn.Linear(1280, self.num_classes)
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"✓ PyTorch model loaded")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  Classes: {self.num_classes}")
    
    def predict(self, image_path: str) -> Dict:
        """
        Run inference on image.
        
        Args:
            image_path: Path to image
        
        Returns:
            Prediction dictionary
        """
        import torch
        from torchvision import transforms
        
        # Load and preprocess image
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = predicted.item()
        class_name = self.idx_to_class[predicted_class]
        confidence_val = confidence.item()
        
        return {
            'predicted_class': predicted_class,
            'class_name': class_name,
            'confidence': confidence_val,
            'probabilities': probabilities[0].cpu().numpy().tolist()
        }
    
    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """Batch inference."""
        results = []
        for path in image_paths:
            results.append(self.predict(path))
        return results
    
    def benchmark(self, image_path: str, num_iterations: int = 100) -> Dict:
        """Benchmark inference speed."""
        import torch
        from torchvision import transforms
        
        logger.info(f"Benchmarking PyTorch inference ({num_iterations} iterations)...")
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0).to(self.device)
        
        # Warmup
        with torch.no_grad():
            for _ in range(5):
                self.model(image_tensor)
        
        # Benchmark
        times = []
        with torch.no_grad():
            for _ in range(num_iterations):
                start = time.perf_counter()
                self.model(image_tensor)
                times.append(time.perf_counter() - start)
        
        times = np.array(times) * 1000  # Convert to ms
        
        return {
            'mean_latency_ms': float(np.mean(times)),
            'median_latency_ms': float(np.median(times)),
            'min_latency_ms': float(np.min(times)),
            'max_latency_ms': float(np.max(times)),
            'std_latency_ms': float(np.std(times)),
            'throughput_img_per_sec': float(1000 / np.mean(times))
        }


# ============================================================================
# Image Preprocessing & Postprocessing
# ============================================================================

def preprocess_image(
    image_path: str,
    input_size: Tuple[int, int] = (224, 224)
) -> np.ndarray:
    """
    Preprocess image for inference.
    
    Args:
        image_path: Path to image file
        input_size: Target image size (H, W)
    
    Returns:
        Preprocessed image array (1, 3, H, W) ready for inference
    """
    # Load image
    image = Image.open(image_path).convert('RGB')
    
    # Resize
    image = image.resize(input_size)
    
    # Convert to array and normalize to [0, 1]
    image_array = np.array(image, dtype=np.float32) / 255.0
    
    # Normalize using ImageNet statistics
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_array = (image_array - mean) / std
    
    # Add batch dimension and transpose to (1, 3, H, W)
    image_array = np.expand_dims(image_array, axis=0).transpose(0, 3, 1, 2)
    
    return image_array.astype(np.float32)


def postprocess_output(logits: np.ndarray) -> Dict[str, any]:
    """
    Postprocess model output.
    
    Args:
        logits: Model output logits (batch_size, num_classes)
    
    Returns:
        Dictionary with predictions
    """
    # Softmax
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probabilities = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    
    # Get top-5 predictions
    top5_indices = np.argsort(-probabilities[0])[:5]
    
    return {
        'predicted_class': int(np.argmax(logits[0])),
        'confidence': float(probabilities[0].max()),
        'probabilities': probabilities[0].tolist(),
        'top5': [
            {
                'class_id': int(idx),
                'confidence': float(probabilities[0, idx])
            }
            for idx in top5_indices
        ]
    }


class ONNXInference:
    """ONNX model inference."""
    
    def __init__(self, model_path: str):
        """Initialize ONNX inference."""
        try:
            rt = importlib.import_module("onnxruntime")
        except ImportError as exc:
            raise ImportError("onnxruntime not installed. Install with: pip install onnxruntime") from exc
        
        logger.info(f"Loading ONNX model from {model_path}...")
        self.session = rt.InferenceSession(model_path)
        
        # Get input/output names
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        logger.info(f"✓ ONNX model loaded")
        logger.info(f"  Input: {self.input_name}")
        logger.info(f"  Output: {self.output_name}")
    
    def predict(self, image_path: str) -> Dict:
        """
        Run inference on image.
        
        Args:
            image_path: Path to image
        
        Returns:
            Prediction dictionary
        """
        image_array = preprocess_image(image_path)
        
        # Infer
        logits = self.session.run(
            [self.output_name],
            {self.input_name: image_array}
        )[0]
        
        return postprocess_output(logits)
    
    def predict_batch(self, image_paths: list) -> list:
        """Batch inference."""
        results = []
        for path in image_paths:
            results.append(self.predict(path))
        return results
    
    def benchmark(self, image_path: str, num_iterations: int = 100) -> Dict:
        """Benchmark inference speed."""
        logger.info(f"Benchmarking ONNX inference ({num_iterations} iterations)...")
        
        image_array = preprocess_image(image_path)
        
        # Warmup
        for _ in range(5):
            self.session.run([self.output_name], {self.input_name: image_array})
        
        # Benchmark
        times = []
        for _ in range(num_iterations):
            start = time.perf_counter()
            self.session.run([self.output_name], {self.input_name: image_array})
            times.append(time.perf_counter() - start)
        
        times = np.array(times) * 1000  # Convert to ms
        
        return {
            'mean_latency_ms': float(np.mean(times)),
            'median_latency_ms': float(np.median(times)),
            'min_latency_ms': float(np.min(times)),
            'max_latency_ms': float(np.max(times)),
            'std_latency_ms': float(np.std(times)),
            'throughput_img_per_sec': float(1000 / np.mean(times))
        }


class TFLiteInference:
    """TFLite model inference."""
    
    def __init__(self, model_path: str):
        """Initialize TFLite inference."""
        try:
            self._tf = importlib.import_module("tensorflow")
        except ImportError as exc:
            raise ImportError("tensorflow not installed. Install with: pip install tensorflow") from exc
        
        logger.info(f"Loading TFLite model from {model_path}...")
        self.interpreter = self._tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Get input/output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        logger.info(f"✓ TFLite model loaded")
        logger.info(f"  Input shape: {self.input_details[0]['shape']}")
        logger.info(f"  Output shape: {self.output_details[0]['shape']}")
    
    def predict(self, image_path: str) -> Dict:
        """
        Run inference on image.
        
        Args:
            image_path: Path to image
        
        Returns:
            Prediction dictionary
        """
        image_array = preprocess_image(image_path)
        
        # Handle int8 quantization if needed
        input_dtype = self.input_details[0]['dtype']
        if input_dtype == np.uint8:
            # Convert to uint8 for quantized models
            image_array = ((image_array * 127.5) + 128).astype(np.uint8)
        
        # Set input
        self.interpreter.set_tensor(
            self.input_details[0]['index'],
            image_array.astype(input_dtype)
        )
        
        # Infer
        self.interpreter.invoke()
        
        # Get output
        logits = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Handle int8 quantization if needed
        output_dtype = self.output_details[0]['dtype']
        if output_dtype == np.uint8:
            # Dequantize
            scale, zero_point = (
                self.output_details[0]['quantization'][0],
                self.output_details[0]['quantization'][1]
            )
            logits = (logits - zero_point) * scale
        
        return postprocess_output(logits)
    
    def predict_batch(self, image_paths: list) -> list:
        """Batch inference."""
        results = []
        for path in image_paths:
            results.append(self.predict(path))
        return results
    
    def benchmark(self, image_path: str, num_iterations: int = 100) -> Dict:
        """Benchmark inference speed."""
        logger.info(f"Benchmarking TFLite inference ({num_iterations} iterations)...")
        
        image_array = preprocess_image(image_path)
        
        # Handle quantization
        input_dtype = self.input_details[0]['dtype']
        if input_dtype == np.uint8:
            image_array = ((image_array * 127.5) + 128).astype(np.uint8)
        
        # Warmup
        for _ in range(5):
            self.interpreter.set_tensor(self.input_details[0]['index'], image_array)
            self.interpreter.invoke()
        
        # Benchmark
        times = []
        for _ in range(num_iterations):
            start = time.perf_counter()
            self.interpreter.set_tensor(self.input_details[0]['index'], image_array)
            self.interpreter.invoke()
            times.append(time.perf_counter() - start)
        
        times = np.array(times) * 1000  # Convert to ms
        
        return {
            'mean_latency_ms': float(np.mean(times)),
            'median_latency_ms': float(np.median(times)),
            'min_latency_ms': float(np.min(times)),
            'max_latency_ms': float(np.max(times)),
            'std_latency_ms': float(np.std(times)),
            'throughput_img_per_sec': float(1000 / np.mean(times))
        }


class ModelComparison:
    """Compare predictions from different model formats."""
    
    def __init__(self, onnx_model: Optional[str] = None, tflite_model: Optional[str] = None):
        """Initialize models."""
        self.onnx_inference = None
        self.tflite_inference = None
        
        if onnx_model:
            self.onnx_inference = ONNXInference(onnx_model)
        
        if tflite_model:
            self.tflite_inference = TFLiteInference(tflite_model)
    
    def compare_predictions(self, image_path: str) -> Dict:
        """Compare predictions from both models."""
        logger.info(f"\nComparing predictions on {image_path}...")
        
        results = {}
        
        if self.onnx_inference:
            logger.info("  Running ONNX inference...")
            results['onnx'] = self.onnx_inference.predict(image_path)
        
        if self.tflite_inference:
            logger.info("  Running TFLite inference...")
            results['tflite'] = self.tflite_inference.predict(image_path)
        
        # Compare outputs
        if len(results) == 2:
            logger.info("\nComparison Results:")
            
            onnx_class = results['onnx']['predicted_class']
            tflite_class = results['tflite']['predicted_class']
            
            logger.info(f"  ONNX predicted class: {onnx_class} (confidence: {results['onnx']['confidence']:.4f})")
            logger.info(f"  TFLite predicted class: {tflite_class} (confidence: {results['tflite']['confidence']:.4f})")
            
            if onnx_class == tflite_class:
                logger.info("  ✓ Predictions agree!")
            else:
                logger.warning("  ✗ Predictions differ!")
            
            # Calculate confidence difference
            conf_diff = abs(
                results['onnx']['confidence'] - results['tflite']['confidence']
            )
            logger.info(f"  Confidence difference: {conf_diff:.4f}")
        
        return results
    
    def compare_performance(self, image_path: str, num_iterations: int = 100) -> Dict:
        """Compare performance of both models."""
        logger.info(f"\nBenchmarking models ({num_iterations} iterations)...")
        
        results = {}
        
        if self.onnx_inference:
            logger.info("\nONNX Benchmark:")
            results['onnx'] = self.onnx_inference.benchmark(image_path, num_iterations)
            logger.info(f"  Mean latency: {results['onnx']['mean_latency_ms']:.2f} ms")
            logger.info(f"  Throughput: {results['onnx']['throughput_img_per_sec']:.1f} img/s")
        
        if self.tflite_inference:
            logger.info("\nTFLite Benchmark:")
            results['tflite'] = self.tflite_inference.benchmark(image_path, num_iterations)
            logger.info(f"  Mean latency: {results['tflite']['mean_latency_ms']:.2f} ms")
            logger.info(f"  Throughput: {results['tflite']['throughput_img_per_sec']:.1f} img/s")
        
        if len(results) == 2:
            speedup = (
                results['onnx']['mean_latency_ms'] /
                results['tflite']['mean_latency_ms']
            )
            logger.info(f"\nTFLite is {speedup:.2f}x faster than ONNX")
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Example usage of exported skin classifier models'
    )
    parser.add_argument(
        '--image',
        type=str,
        required=False,
        help='Path to test image'
    )
    parser.add_argument(
        '--onnx',
        type=str,
        default='ml/exports/skin_classifier.onnx',
        help='Path to ONNX model'
    )
    parser.add_argument(
        '--tflite',
        type=str,
        default='ml/exports/skin_classifier.tflite',
        help='Path to TFLite model'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['predict', 'compare', 'benchmark'],
        default='predict',
        help='Inference mode'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of benchmark iterations'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['onnx', 'tflite', 'both'],
        default='both',
        help='Which model to use'
    )
    
    args = parser.parse_args()
    
    # Create test image if not provided
    if args.image is None:
        logger.info("No test image provided, creating dummy image...")
        image = Image.new('RGB', (224, 224), color='blue')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            image.save(f.name)
            args.image = f.name
        logger.info(f"Created test image: {args.image}")
    
    # Initialize models
    onnx_path = Path(args.onnx)
    tflite_path = Path(args.tflite)
    
    onnx_model = str(onnx_path) if onnx_path.exists() and args.format in ['onnx', 'both'] else None
    tflite_model = str(tflite_path) if tflite_path.exists() and args.format in ['tflite', 'both'] else None
    
    if not onnx_model and not tflite_model:
        logger.error("No models found. Please export models first using export_models.py")
        return
    
    # Run inference
    if args.mode == 'predict':
        if onnx_model:
            logger.info("\n" + "="*60)
            logger.info("ONNX Inference")
            logger.info("="*60)
            onnx_inf = ONNXInference(onnx_model)
            result = onnx_inf.predict(args.image)
            logger.info(f"Prediction: Class {result['predicted_class']}")
            logger.info(f"Confidence: {result['confidence']:.4f}")
        
        if tflite_model:
            logger.info("\n" + "="*60)
            logger.info("TFLite Inference")
            logger.info("="*60)
            tflite_inf = TFLiteInference(tflite_model)
            result = tflite_inf.predict(args.image)
            logger.info(f"Prediction: Class {result['predicted_class']}")
            logger.info(f"Confidence: {result['confidence']:.4f}")
    
    elif args.mode == 'compare':
        logger.info("\n" + "="*60)
        logger.info("Model Comparison")
        logger.info("="*60)
        comparator = ModelComparison(onnx_model, tflite_model)
        comparator.compare_predictions(args.image)
    
    elif args.mode == 'benchmark':
        logger.info("\n" + "="*60)
        logger.info("Performance Benchmark")
        logger.info("="*60)
        comparator = ModelComparison(onnx_model, tflite_model)
        comparator.compare_performance(args.image, args.iterations)


# ============================================================================
# Backend API Integration
# ============================================================================

import os
from typing import Union

# Class mappings for skin analysis
SKIN_TYPE_CLASSES = ["normal", "dry", "oily", "combination", "sensitive"]
HAIR_TYPE_CLASSES = ["straight", "wavy", "curly", "coily"]
CONDITIONS_CLASSES = ["healthy", "mild_acne", "severe_acne", "eczema", "psoriasis"]

# Global model instances
_pytorch_inference = None
_onnx_inference = None
_tflite_inference = None


def _initialize_models():
    """Initialize models, preferring PyTorch > ONNX > TFLite."""
    global _pytorch_inference, _onnx_inference, _tflite_inference
    
    # Find the project root by going up from this file
    # __file__ = backend/app/services/ml_infer.py
    # Go up 4 levels to reach project root
    current_dir = Path(__file__).parent  # services
    app_dir = current_dir.parent  # app
    backend_dir = app_dir.parent  # backend
    base_dir = backend_dir.parent  # project root
    
    logger.info(f"Project root: {base_dir}")
    
    # Try PyTorch first (best for training & fine-tuning)
    pytorch_model_path = base_dir / "ml" / "exports" / "skin_classifier_best.pth"
    pytorch_mapping_path = base_dir / "ml" / "exports" / "class_mapping.json"
    
    logger.info(f"Looking for PyTorch model at: {pytorch_model_path}")
    logger.info(f"Looking for class mapping at: {pytorch_mapping_path}")
    
    if pytorch_model_path.exists() and pytorch_mapping_path.exists():
        try:
            _pytorch_inference = PyTorchInference(
                str(pytorch_model_path),
                str(pytorch_mapping_path)
            )
            logger.info("✓ PyTorch model loaded (primary)")
            return True
        except Exception as e:
            logger.warning(f"Failed to load PyTorch model: {e}")
    
    # Try TFLite next (efficient for inference)
    tflite_path = base_dir / "ml" / "exports" / "skin_classifier.tflite"
    if tflite_path.exists():
        try:
            _tflite_inference = TFLiteInference(str(tflite_path))
            logger.info("✓ TFLite model loaded (fallback)")
            return True
        except Exception as e:
            logger.warning(f"Failed to load TFLite: {e}")
    
    # Try ONNX as last resort
    onnx_path = base_dir / "ml" / "exports" / "skin_classifier.onnx"
    if onnx_path.exists():
        try:
            _onnx_inference = ONNXInference(str(onnx_path))
            logger.info("✓ ONNX model loaded (fallback)")
            return True
        except Exception as e:
            logger.warning(f"Failed to load ONNX: {e}")
    
    logger.warning("⚠️  No ML models available - using mock responses")
    return False


def _logits_to_predictions(logits: np.ndarray) -> Dict:
    """Convert model logits to structured predictions."""
    logits = logits[0]  # Remove batch dimension
    
    # Apply softmax
    exp_logits = np.exp(logits - np.max(logits))
    probabilities = exp_logits / np.sum(exp_logits)
    
    # Split probabilities by class type
    num_skin_types = len(SKIN_TYPE_CLASSES)
    num_hair_types = len(HAIR_TYPE_CLASSES)
    
    skin_probs = probabilities[:num_skin_types]
    hair_probs = probabilities[num_skin_types:num_skin_types + num_hair_types]
    condition_probs = probabilities[num_skin_types + num_hair_types:]
    
    # Get argmax predictions
    skin_type_id = int(np.argmax(skin_probs))
    hair_type_id = int(np.argmax(hair_probs))
    condition_id = int(np.argmax(condition_probs))
    
    # Map to class names
    skin_type = SKIN_TYPE_CLASSES[skin_type_id]
    hair_type = HAIR_TYPE_CLASSES[hair_type_id]
    condition = CONDITIONS_CLASSES[condition_id]
    
    # Construct confidence scores
    confidence_scores = {
        "skin_type": float(skin_probs[skin_type_id]),
        "hair_type": float(hair_probs[hair_type_id]),
        "condition": float(condition_probs[condition_id]),
    }
    
    return {
        "skin_type": skin_type,
        "hair_type": hair_type,
        "condition": condition,
        "confidence_scores": confidence_scores,
    }


def analyze_image(image: Union[bytes, str]) -> Dict:
    """
    Analyze an image using available ML models.
    
    Tries PyTorch first (trained model), falls back to TFLite/ONNX.
    
    Args:
        image: File path (str) or image bytes
    
    Returns:
        Dictionary with analysis results:
        {
            "class_id": int,
            "class_name": str,
            "confidence": float,
            "probabilities": list,
            "model_type": str  # "pytorch", "tflite", "onnx", or "mock"
        }
    """
    # Initialize models on first call
    global _pytorch_inference, _onnx_inference, _tflite_inference
    if _pytorch_inference is None and _onnx_inference is None and _tflite_inference is None:
        _initialize_models()
    
    # Handle image input
    image_path = None
    cleanup_temp = False
    
    if isinstance(image, str):
        if not os.path.exists(image):
            raise FileNotFoundError(f"Image not found: {image}")
        image_path = image
    else:
        # image is bytes
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image)
            image_path = tmp.name
            cleanup_temp = True
    
    try:
        # Try inference with available models in priority order
        result = None
        model_type = "mock"
        
        if _pytorch_inference:
            try:
                logger.info("Using PyTorch model for inference")
                result = _pytorch_inference.predict(image_path)
                model_type = "pytorch"
                logger.info(
                    f"PyTorch inference: {result['class_name']} "
                    f"(confidence: {result['confidence']:.4f})"
                )
            except Exception as e:
                logger.error(f"PyTorch inference failed: {e}")
        
        if result is None and _tflite_inference:
            try:
                logger.info("Using TFLite model for inference (PyTorch fallback)")
                result = _tflite_inference.predict(image_path)
                model_type = "tflite"
            except Exception as e:
                logger.error(f"TFLite inference failed: {e}")
        
        if result is None and _onnx_inference:
            try:
                logger.info("Using ONNX model for inference (PyTorch fallback)")
                result = _onnx_inference.predict(image_path)
                model_type = "onnx"
            except Exception as e:
                logger.error(f"ONNX inference failed: {e}")
        
        # Fallback to mock response
        if result is None:
            logger.warning("No models available, using mock response")
            result = {
                'predicted_class': 0,
                'class_name': 'normal',
                'confidence': 0.75,
                'probabilities': [0.75, 0.25]
            }
            model_type = "mock"
        
        # Format response
        response = {
            "class_id": result.get('predicted_class', 0),
            "class_name": result.get('class_name', 'unknown'),
            "confidence": float(result.get('confidence', 0.0)),
            "probabilities": result.get('probabilities', []),
            "model_type": model_type,
            "status": "success"
        }
        
        logger.info(
            f"✓ Analysis complete ({model_type}): "
            f"{response['class_name']} (conf: {response['confidence']:.2%})"
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {
            "error": str(e),
            "status": "error",
            "model_type": "none"
        }
    
    finally:
        if cleanup_temp and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except Exception:
                pass


def analyze_image_local(image_path: str) -> Dict:
    """Convenience wrapper for local image file analysis."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    return analyze_image(image_path)


def get_model_info() -> Dict:
    """Get information about loaded models."""
    global _pytorch_inference, _onnx_inference, _tflite_inference
    
    if _pytorch_inference is None and _onnx_inference is None and _tflite_inference is None:
        _initialize_models()
    
    models_info = {}
    
    if _pytorch_inference:
        models_info['pytorch'] = {
            'status': 'loaded',
            'num_classes': _pytorch_inference.num_classes,
            'device': _pytorch_inference.device
        }
    
    if _tflite_inference:
        models_info['tflite'] = {'status': 'loaded'}
    
    if _onnx_inference:
        models_info['onnx'] = {'status': 'loaded'}
    
    if not models_info:
        models_info['status'] = 'no_models_loaded'
    
    return models_info


if __name__ == '__main__':
    main()
