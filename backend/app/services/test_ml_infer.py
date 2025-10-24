"""
Test suite for ML inference service.
Tests analyze_image and analyze_image_local functions.
"""

import tempfile
from pathlib import Path
import os
import sys

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from PIL import Image
from services import ml_infer


def test_class_mappings():
    """Test that class mappings are defined correctly."""
    print("\n" + "="*60)
    print("TEST: Class Mappings")
    print("="*60)
    
    print(f"Skin types: {ml_infer.SKIN_TYPE_CLASSES}")
    print(f"Hair types: {ml_infer.HAIR_TYPE_CLASSES}")
    print(f"Conditions: {ml_infer.CONDITIONS_CLASSES}")
    
    assert len(ml_infer.SKIN_TYPE_CLASSES) == 5
    assert len(ml_infer.HAIR_TYPE_CLASSES) == 4
    assert len(ml_infer.CONDITIONS_CLASSES) == 5
    print("[PASS] Class mappings valid")


def test_analyze_image_bytes():
    """Test analyze_image with image bytes."""
    print("\n" + "="*60)
    print("TEST: Analyze Image (Bytes)")
    print("="*60)
    
    test_image = Image.new('RGB', (224, 224), color=(100, 150, 200))
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        test_image.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, 'rb') as f:
            image_bytes = f.read()
        
        result = ml_infer.analyze_image(image_bytes)
        
        print(f"Skin type: {result['skin_type']}")
        print(f"Hair type: {result['hair_type']}")
        print(f"Model type: {result['model_type']}")
        
        assert 'skin_type' in result
        assert 'hair_type' in result
        assert 'conditions_detected' in result
        assert 'confidence_scores' in result
        assert 'model_type' in result
        assert result['skin_type'] in ml_infer.SKIN_TYPE_CLASSES
        print("[PASS] Bytes input test passed")
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def test_analyze_image_path():
    """Test analyze_image with file path."""
    print("\n" + "="*60)
    print("TEST: Analyze Image (File Path)")
    print("="*60)
    
    test_image = Image.new('RGB', (224, 224), color=(50, 100, 150))
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        test_image.save(tmp.name)
        image_path = tmp.name
    
    try:
        result = ml_infer.analyze_image(image_path)
        print(f"Skin type: {result['skin_type']}")
        print(f"Hair type: {result['hair_type']}")
        assert isinstance(result, dict)
        print("[PASS] File path test passed")
    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def test_analyze_image_local():
    """Test analyze_image_local function."""
    print("\n" + "="*60)
    print("TEST: Analyze Local Image")
    print("="*60)
    
    test_image = Image.new('RGB', (224, 224), color=(75, 125, 175))
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        test_image.save(tmp.name)
        image_path = tmp.name
    
    try:
        result = ml_infer.analyze_image_local(image_path)
        print(f"Skin type: {result['skin_type']}")
        print(f"Model type: {result['model_type']}")
        assert isinstance(result, dict)
        print("[PASS] Local analysis test passed")
    finally:
        try:
            os.unlink(image_path)
        except:
            pass


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ML Inference Service Test Suite")
    print("="*60)
    
    try:
        test_class_mappings()
        test_analyze_image_bytes()
        test_analyze_image_path()
        test_analyze_image_local()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)
        print("\nService is ready for production deployment.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
