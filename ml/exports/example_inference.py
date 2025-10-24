"""
Example usage of exported skin classifier models in different formats.

Demonstrates:
- ONNX inference with ONNX Runtime
- TFLite inference with TensorFlow Lite
- Model output comparison
- Performance benchmarking
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Tuple, Optional
import tempfile

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


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
            import onnxruntime as rt
        except ImportError:
            raise ImportError("onnxruntime not installed. Install with: pip install onnxruntime")
        
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
            import tensorflow as tf
        except ImportError:
            raise ImportError("tensorflow not installed. Install with: pip install tensorflow")
        
        logger.info(f"Loading TFLite model from {model_path}...")
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
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


if __name__ == '__main__':
    main()
