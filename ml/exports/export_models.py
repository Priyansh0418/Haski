"""
Export PyTorch skin classifier models to ONNX and TFLite formats.

Supported conversions:
- PyTorch → ONNX (with dynamic axes)
- PyTorch → TFLite (via ONNX → TensorFlow SavedModel → TFLite)
- Post-training quantization (float16, int8)

Usage:
    # Export to ONNX
    python export_models.py --checkpoint ml/exports/skin_classifier.pth --format onnx

    # Export to TFLite with quantization
    python export_models.py --checkpoint ml/exports/skin_classifier.pth --format tflite --quantize int8

    # Export both formats
    python export_models.py --checkpoint ml/exports/skin_classifier.pth --format both --quantize float16
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import tempfile
import shutil

import numpy as np
import torch
import torch.nn as nn
from torch.onnx import export as onnx_export
from torchvision import models as torch_models
from PIL import Image

# Import representative data generator
try:
    from representative_data import RepresentativeDataGenerator
except ImportError:
    RepresentativeDataGenerator = None

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class PyTorchClassifier(nn.Module):
    """Wrapper for PyTorch classifier model (EfficientNet or ResNet)."""
    
    def __init__(self, num_classes: int = 10, model_arch: str = 'efficientnet_b0'):
        super().__init__()
        self.num_classes = num_classes
        self.model_arch = model_arch
        
        # Load backbone
        if model_arch == 'efficientnet_b0':
            self.backbone = torch_models.efficientnet_b0(pretrained=True)
            in_features = 1280
        elif model_arch == 'resnet50':
            self.backbone = torch_models.resnet50(pretrained=True)
            in_features = 2048
        else:
            raise ValueError(f"Unsupported architecture: {model_arch}")
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning class logits."""
        x = self.backbone.features(x)
        x = self.backbone.avgpool(x)
        x = x.flatten(1)
        x = self.classifier(x)
        return x


class ONNXExporter:
    """Export PyTorch models to ONNX format."""
    
    def __init__(self, model: nn.Module, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.model.eval()
    
    def export(
        self,
        output_path: str,
        input_size: Tuple[int, int] = (224, 224),
        batch_size: int = 1,
        opset_version: int = 11
    ) -> str:
        """
        Export PyTorch model to ONNX format.
        
        Args:
            output_path: Path to save ONNX model
            input_size: Input image size (H, W)
            batch_size: Batch size for export (usually 1, but use -1 for dynamic)
            opset_version: ONNX opset version (11, 12, 13, etc.)
        
        Returns:
            Path to exported ONNX model
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exporting to ONNX (opset={opset_version})...")
        
        # Create dummy input
        dummy_input = torch.randn(
            batch_size,
            3,
            input_size[0],
            input_size[1],
            device=self.device
        )
        
        # Define input/output names
        input_names = ['image']
        output_names = ['logits']
        
        # Dynamic axes: batch dimension (0) and spatial dimensions (2, 3)
        dynamic_axes = {
            'image': {0: 'batch_size', 2: 'height', 3: 'width'},
            'logits': {0: 'batch_size'}
        }
        
        try:
            with torch.no_grad():
                onnx_export(
                    self.model,
                    dummy_input,
                    str(output_path),
                    input_names=input_names,
                    output_names=output_names,
                    dynamic_axes=dynamic_axes,
                    opset_version=opset_version,
                    do_constant_folding=True,
                    verbose=False
                )
            
            logger.info(f"✓ ONNX export successful: {output_path}")
            
            # Verify ONNX model
            self._verify_onnx(str(output_path), input_size, batch_size)
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"✗ ONNX export failed: {e}")
            raise
    
    @staticmethod
    def _verify_onnx(onnx_path: str, input_size: Tuple[int, int], batch_size: int = 1):
        """Verify ONNX model loads correctly."""
        try:
            import onnx
            model = onnx.load(onnx_path)
            onnx.checker.check_model(model)
            logger.info(f"✓ ONNX model verification passed")
        except ImportError:
            logger.warning("ONNX library not available for verification")
        except Exception as e:
            logger.warning(f"ONNX verification warning: {e}")


class TFLiteExporter:
    """Export models to TFLite format via ONNX → TensorFlow SavedModel → TFLite."""
    
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self._check_dependencies()
    
    @staticmethod
    def _check_dependencies():
        """Check if required packages are installed."""
        try:
            import tensorflow
            logger.info(f"✓ TensorFlow {tensorflow.__version__} detected")
        except ImportError:
            logger.error("✗ TensorFlow not installed. Install with: pip install tensorflow")
            raise
    
    def export_from_onnx(
        self,
        onnx_path: str,
        output_path: str,
        input_size: Tuple[int, int] = (224, 224),
        quantize: Optional[str] = None,
        representative_data_gen=None
    ) -> str:
        """
        Export ONNX model to TFLite format.
        
        Args:
            onnx_path: Path to ONNX model
            output_path: Path to save TFLite model
            input_size: Input image size (H, W)
            quantize: Quantization type: None, 'float16', 'int8'
            representative_data_gen: Generator for int8 quantization calibration
        
        Returns:
            Path to exported TFLite model
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Converting ONNX → TensorFlow SavedModel → TFLite...")
        
        try:
            import tensorflow as tf
            
            # Step 1: ONNX → TensorFlow SavedModel
            saved_model_path = self._onnx_to_saved_model(onnx_path, input_size)
            
            # Step 2: TensorFlow SavedModel → TFLite
            converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_path)
            
            # Apply quantization
            if quantize == 'float16':
                logger.info("Applying float16 quantization...")
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_types = [tf.float16]
            
            elif quantize == 'int8':
                logger.info("Applying int8 quantization...")
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_ops = [
                    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
                ]
                converter.inference_input_type = tf.uint8
                converter.inference_output_type = tf.uint8
                
                # Use representative dataset if provided
                if representative_data_gen is not None:
                    converter.representative_dataset = representative_data_gen
                    logger.info("Using representative dataset for int8 calibration")
                else:
                    logger.warning("No representative dataset for int8 - using default calibration")
            
            # Convert
            tflite_model = converter.convert()
            
            # Save
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"✓ TFLite export successful: {output_path}")
            logger.info(f"  Model size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            # Cleanup temporary SavedModel
            if Path(saved_model_path).exists():
                shutil.rmtree(saved_model_path)
            
            return str(output_path)
        
        except ImportError as e:
            logger.error(f"✗ TensorFlow not available: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ TFLite export failed: {e}")
            raise
    
    @staticmethod
    def _onnx_to_saved_model(onnx_path: str, input_size: Tuple[int, int]) -> str:
        """
        Convert ONNX model to TensorFlow SavedModel.
        
        Uses one of two methods:
        1. onnx-tf package (recommended, more reliable)
        2. tf.experimental.onnx.import_onnx_model (if available)
        
        Args:
            onnx_path: Path to ONNX model
            input_size: Input image size (H, W)
        
        Returns:
            Path to TensorFlow SavedModel directory
        """
        import tensorflow as tf
        
        temp_dir = tempfile.mkdtemp()
        saved_model_path = str(Path(temp_dir) / 'tf_model')
        
        try:
            # Method 1: Try onnx-tf (most reliable)
            try:
                import onnx
                from onnx_tf.backend import prepare
                
                logger.info("Using onnx-tf for ONNX → TensorFlow conversion...")
                
                onnx_model = onnx.load(onnx_path)
                tf_rep = prepare(onnx_model)
                tf_rep.export_graph(saved_model_path)
                
                logger.info(f"✓ ONNX → TensorFlow conversion successful")
                return saved_model_path
            
            except (ImportError, ModuleNotFoundError):
                logger.warning("onnx-tf not available, trying tf.experimental.onnx...")
                
                # Method 2: Try tf.experimental.onnx (may not be available in all TF versions)
                if hasattr(tf.experimental, 'onnx'):
                    import onnx as onnx_pkg
                    onnx_model = onnx_pkg.load(onnx_path)
                    concrete_func = tf.function(
                        lambda x: tf.experimental.onnx.import_onnx_model(
                            onnx_path,
                            input_signature=[
                                tf.TensorSpec(
                                    shape=[None, 3, input_size[0], input_size[1]],
                                    dtype=tf.float32
                                )
                            ]
                        )
                    )
                    
                    concrete_func = concrete_func.get_concrete_function(
                        tf.TensorSpec(shape=[1, 3, input_size[0], input_size[1]], dtype=tf.float32)
                    )
                    
                    tf.saved_model.save(concrete_func, saved_model_path)
                    logger.info(f"✓ ONNX → TensorFlow conversion successful")
                    return saved_model_path
                
                else:
                    raise ImportError(
                        "Neither onnx-tf nor tf.experimental.onnx available. "
                        "Install with: pip install onnx-tf or update TensorFlow"
                    )
        
        except Exception as e:
            logger.error(f"✗ ONNX → TensorFlow conversion failed: {e}")
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
            raise


class RepresentativeDataGenerator:
    """Generate representative dataset for int8 quantization."""
    
    def __init__(
        self,
        image_dir: Optional[str] = None,
        num_samples: int = 100,
        input_size: Tuple[int, int] = (224, 224)
    ):
        """
        Initialize data generator.
        
        Args:
            image_dir: Directory with calibration images
            num_samples: Number of samples to use
            input_size: Input image size (H, W)
        """
        self.image_dir = image_dir
        self.num_samples = num_samples
        self.input_size = input_size
        self.image_files = []
        
        if image_dir:
            self._load_image_paths()
    
    def _load_image_paths(self):
        """Load image paths from directory."""
        image_dir = Path(self.image_dir)
        self.image_files = list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))
        self.image_files = self.image_files[:self.num_samples]
        
        if not self.image_files:
            logger.warning(f"No images found in {self.image_dir}")
        else:
            logger.info(f"Loaded {len(self.image_files)} calibration images")
    
    def __call__(self):
        """Generate representative dataset batches."""
        import tensorflow as tf
        
        if not self.image_files:
            logger.warning("No representative data available")
            return
        
        # Normalize ImageNet statistics
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        
        for image_path in self.image_files:
            try:
                # Load and preprocess image
                image = Image.open(image_path).convert('RGB')
                image = image.resize(self.input_size)
                image_array = np.array(image, dtype=np.float32) / 255.0
                
                # Normalize
                image_array = (image_array - mean) / std
                
                # Add batch dimension and convert to uint8 for TFLite
                image_array = np.expand_dims(image_array, axis=0)
                image_array = (image_array * 127.5 + 128).astype(np.uint8)
                
                yield [tf.constant(image_array)]
            
            except Exception as e:
                logger.warning(f"Failed to load {image_path}: {e}")
                continue


class ModelExporter:
    """Main exporter orchestrating ONNX and TFLite export."""
    
    def __init__(
        self,
        checkpoint_path: str,
        num_classes: int = 10,
        device: str = 'cpu'
    ):
        """
        Initialize exporter.
        
        Args:
            checkpoint_path: Path to PyTorch checkpoint
            num_classes: Number of classification classes
            device: Device to use ('cpu' or 'cuda')
        """
        self.checkpoint_path = checkpoint_path
        self.num_classes = num_classes
        self.device = device
        self.model = None
        self.metadata = {}
    
    def load_checkpoint(self) -> Dict[str, Any]:
        """Load PyTorch checkpoint."""
        logger.info(f"Loading checkpoint from {self.checkpoint_path}...")
        
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        
        # Extract model config
        if 'config' in checkpoint:
            config = checkpoint['config']
            self.num_classes = config.get('num_classes', 10)
            model_arch = config.get('model_arch', 'efficientnet_b0')
        else:
            logger.warning("Config not found in checkpoint, using defaults")
            model_arch = 'efficientnet_b0'
        
        # Create and load model
        self.model = PyTorchClassifier(
            num_classes=self.num_classes,
            model_arch=model_arch
        )
        
        # Load state dict
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
        
        self.model.load_state_dict(state_dict)
        self.model.eval()
        
        # Store metadata
        self.metadata = {
            'num_classes': self.num_classes,
            'model_arch': model_arch,
            'input_size': 224,
            'input_channels': 3,
            'checkpoint': str(self.checkpoint_path)
        }
        
        logger.info(f"✓ Checkpoint loaded: {model_arch} with {self.num_classes} classes")
        
        return self.metadata
    
    def export_to_onnx(
        self,
        output_path: str,
        input_size: Tuple[int, int] = (224, 224),
        opset_version: int = 11
    ) -> str:
        """Export to ONNX format."""
        if self.model is None:
            self.load_checkpoint()
        
        exporter = ONNXExporter(self.model, device=self.device)
        return exporter.export(output_path, input_size, opset_version=opset_version)
    
    def export_to_tflite(
        self,
        onnx_path: str,
        output_path: str,
        input_size: Tuple[int, int] = (224, 224),
        quantize: Optional[str] = None,
        calibration_image_dir: Optional[str] = None
    ) -> str:
        """Export to TFLite format."""
        exporter = TFLiteExporter(device=self.device)
        
        # Create representative dataset generator for int8 quantization
        representative_data_gen = None
        if quantize == 'int8':
            generator = RepresentativeDataGenerator(
                image_dir=calibration_image_dir,
                num_samples=100,
                input_size=input_size
            )
            representative_data_gen = generator
        
        return exporter.export_from_onnx(
            onnx_path,
            output_path,
            input_size=input_size,
            quantize=quantize,
            representative_data_gen=representative_data_gen
        )
    
    def export_all(
        self,
        output_dir: str = 'ml/exports',
        onnx_filename: str = 'skin_classifier.onnx',
        tflite_filename: str = 'skin_classifier.tflite',
        quantize: Optional[str] = None,
        calibration_image_dir: Optional[str] = None,
        input_size: Tuple[int, int] = (224, 224),
        representative_data_gen=None
    ) -> Dict[str, str]:
        """
        Export model to all formats.
        
        Args:
            output_dir: Output directory for exports
            onnx_filename: ONNX output filename
            tflite_filename: TFLite output filename
            quantize: Quantization type for TFLite ('float16', 'int8', or None)
            calibration_image_dir: Directory with images for int8 calibration
            input_size: Input image size (H, W)
            representative_data_gen: Generator for int8 quantization calibration
        
        Returns:
            Dictionary with export paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {'metadata': self.metadata}
        
        try:
            # Export ONNX
            onnx_path = str(output_dir / onnx_filename)
            logger.info(f"\n{'='*60}")
            logger.info("ONNX Export")
            logger.info(f"{'='*60}")
            onnx_path = self.export_to_onnx(onnx_path, input_size=input_size)
            results['onnx'] = onnx_path
        
        except Exception as e:
            logger.error(f"ONNX export failed: {e}")
            results['onnx'] = None
        
        try:
            # Export TFLite
            tflite_path = str(output_dir / tflite_filename)
            logger.info(f"\n{'='*60}")
            logger.info("TFLite Export")
            logger.info(f"{'='*60}")
            tflite_path = self.export_to_tflite(
                onnx_path=onnx_path,
                output_path=tflite_path,
                input_size=input_size,
                quantize=quantize,
                representative_data_gen=representative_data_gen
            )
            results['tflite'] = tflite_path
        
        except Exception as e:
            logger.error(f"TFLite export failed: {e}")
            results['tflite'] = None
        
        # Save metadata
        metadata_path = str(output_dir / 'export_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        results['metadata_file'] = metadata_path
        
        logger.info(f"\n{'='*60}")
        logger.info("Export Summary")
        logger.info(f"{'='*60}")
        for key, value in results.items():
            if value:
                logger.info(f"✓ {key}: {value}")
            else:
                logger.error(f"✗ {key}: Failed")
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Export PyTorch skin classifier to ONNX and TFLite formats'
    )
    parser.add_argument(
        '--checkpoint',
        type=str,
        required=True,
        help='Path to PyTorch checkpoint'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['onnx', 'tflite', 'both'],
        default='both',
        help='Export format'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='ml/exports',
        help='Output directory'
    )
    parser.add_argument(
        '--quantize',
        type=str,
        choices=[None, 'float16', 'int8'],
        default=None,
        help='TFLite quantization type'
    )
    parser.add_argument(
        '--calibration-dir',
        type=str,
        default=None,
        help='Directory with calibration images for int8 quantization'
    )
    parser.add_argument(
        '--dataset-dir',
        type=str,
        default='ml/data',
        help='Path to prepared dataset for representative data generation'
    )
    parser.add_argument(
        '--dataset-type',
        type=str,
        choices=['classification', 'detection'],
        default='classification',
        help='Type of dataset for representative data'
    )
    parser.add_argument(
        '--num-calib-samples',
        type=int,
        default=100,
        help='Number of samples for int8 calibration'
    )
    parser.add_argument(
        '--input-size',
        type=int,
        default=224,
        help='Input image size'
    )
    parser.add_argument(
        '--device',
        type=str,
        choices=['cpu', 'cuda'],
        default='cuda' if torch.cuda.is_available() else 'cpu',
        help='Device to use'
    )
    parser.add_argument(
        '--num-classes',
        type=int,
        default=10,
        help='Number of classes'
    )
    
    args = parser.parse_args()
    
    # Initialize exporter
    exporter = ModelExporter(
        checkpoint_path=args.checkpoint,
        num_classes=args.num_classes,
        device=args.device
    )
    
    # Load checkpoint
    exporter.load_checkpoint()
    
    # Prepare representative dataset for int8 quantization
    representative_data_gen = None
    if args.quantize == 'int8':
        if RepresentativeDataGenerator is None:
            logger.warning("representative_data module not available")
        else:
            logger.info("Generating representative dataset for int8 quantization...")
            try:
                dataset_gen = RepresentativeDataGenerator(
                    data_dir=args.dataset_dir,
                    dataset_type=args.dataset_type,
                    num_samples=args.num_calib_samples,
                    batch_size=1,
                    input_size=(args.input_size, args.input_size)
                )
                dataset_gen.print_summary()
                
                # Create generator function for TFLite converter
                def representative_data_gen():
                    return dataset_gen.generate_tflite_batches()
                
                logger.info("Representative dataset ready for quantization")
            except Exception as e:
                logger.warning(f"Failed to create representative dataset: {e}")
    
    # Export
    if args.format == 'onnx':
        exporter.export_to_onnx(
            output_path=str(Path(args.output_dir) / 'skin_classifier.onnx'),
            input_size=(args.input_size, args.input_size)
        )
    
    elif args.format == 'tflite':
        # Need to create ONNX first
        onnx_path = str(Path(args.output_dir) / 'skin_classifier.onnx')
        exporter.export_to_onnx(
            output_path=onnx_path,
            input_size=(args.input_size, args.input_size)
        )
        exporter.export_to_tflite(
            onnx_path=onnx_path,
            output_path=str(Path(args.output_dir) / 'skin_classifier.tflite'),
            input_size=(args.input_size, args.input_size),
            quantize=args.quantize,
            representative_data_gen=representative_data_gen
        )
    
    elif args.format == 'both':
        exporter.export_all(
            output_dir=args.output_dir,
            quantize=args.quantize,
            calibration_image_dir=args.calibration_dir,
            input_size=(args.input_size, args.input_size),
            representative_data_gen=representative_data_gen
        )


if __name__ == '__main__':
    main()
