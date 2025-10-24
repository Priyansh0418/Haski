#!/usr/bin/env python3
"""
Test ML Inference integration with backend API.

Tests:
1. Model loading
2. Image inference
3. API compatibility
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.ml_infer import analyze_image_local, get_model_info


def test_model_loading():
    """Test that models load correctly."""
    print("\n" + "="*70)
    print("TEST 1: Model Loading")
    print("="*70)
    
    info = get_model_info()
    print(json.dumps(info, indent=2))
    
    if info.get('pytorch', {}).get('status') == 'loaded':
        print("✅ PyTorch model loaded successfully!")
        return True
    elif info.get('tflite', {}).get('status') == 'loaded':
        print("⚠️  PyTorch not available, using TFLite fallback")
        return True
    else:
        print("❌ No models loaded")
        return False


def test_inference():
    """Test inference on a sample image."""
    print("\n" + "="*70)
    print("TEST 2: Image Inference")
    print("="*70)
    
    # Find a test image
    test_images = [
        Path("ml/data/training/test/dry/image_1_0.jpg"),
        Path("ml/data/training/test/normal/image_0_0.jpg"),
        Path("test_image.jpg"),
        Path("sample.jpg"),
    ]
    
    image_path = None
    for img in test_images:
        if img.exists():
            image_path = img
            break
    
    if not image_path:
        print("⚠️  No test image found, skipping inference test")
        return False
    
    print(f"Using test image: {image_path}")
    
    try:
        result = analyze_image_local(str(image_path))
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            print(f"✅ Inference successful!")
            print(f"   Predicted: {result.get('class_name')}")
            print(f"   Confidence: {result.get('confidence'):.2%}")
            print(f"   Model: {result.get('model_type')}")
            return True
        else:
            print("❌ Inference failed")
            return False
    
    except Exception as e:
        print(f"❌ Inference error: {e}")
        return False


def test_api_compatibility():
    """Test API response format compatibility."""
    print("\n" + "="*70)
    print("TEST 3: API Response Format")
    print("="*70)
    
    # Create a dummy image for testing
    from PIL import Image
    import tempfile
    
    # Create test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (224, 224), color='blue')
        img.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        result = analyze_image_local(tmp_path)
        
        # Check required fields
        required_fields = ['class_id', 'class_name', 'confidence', 'model_type']
        missing_fields = [f for f in required_fields if f not in result]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        print(f"✅ All required fields present:")
        for field in required_fields:
            print(f"   • {field}: {result[field]}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  ML INFERENCE BACKEND INTEGRATION TEST".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Model Loading": test_model_loading(),
        "Image Inference": test_inference(),
        "API Compatibility": test_api_compatibility(),
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Integration is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
