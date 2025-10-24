"""
Quick start examples for using exported skin classifier models.

This file shows practical examples of how to use ONNX and TFLite models
in real applications.
"""

# ============================================================================
# EXAMPLE 1: ONNX Model - Desktop/Server Deployment
# ============================================================================

def example_onnx_desktop():
    """Use ONNX model on desktop or server."""
    import onnxruntime as rt
    import numpy as np
    from PIL import Image
    
    # Load model
    session = rt.InferenceSession('ml/exports/skin_classifier.onnx')
    
    # Load and preprocess image
    image = Image.open('photo.jpg').convert('RGB')
    image = image.resize((224, 224))
    image_array = np.array(image, dtype=np.float32) / 255.0
    
    # Normalize (ImageNet)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_array = (image_array - mean) / std
    
    # Add batch dimension (1, 3, 224, 224)
    image_array = np.expand_dims(image_array, axis=0).transpose(0, 3, 1, 2)
    
    # Predict
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    logits = session.run([output_name], {input_name: image_array})[0]
    
    # Get class and confidence
    class_id = np.argmax(logits[0])
    confidence = np.exp(logits[0][class_id]) / np.sum(np.exp(logits[0]))
    
    print(f"Predicted class: {class_id}")
    print(f"Confidence: {confidence:.2%}")


# ============================================================================
# EXAMPLE 2: TFLite Model - Mobile/Edge Deployment (Python)
# ============================================================================

def example_tflite_python():
    """Use TFLite model in Python (mobile/edge)."""
    import tensorflow as tf
    import numpy as np
    from PIL import Image
    
    # Load model
    interpreter = tf.lite.Interpreter(model_path='ml/exports/skin_classifier.tflite')
    interpreter.allocate_tensors()
    
    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Load and preprocess image
    image = Image.open('photo.jpg').convert('RGB')
    image = image.resize((224, 224))
    image_array = np.array(image, dtype=np.float32) / 255.0
    
    # Normalize
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_array = (image_array - mean) / std
    image_array = np.expand_dims(image_array, axis=0)
    
    # Handle quantization (if int8)
    input_dtype = input_details[0]['dtype']
    if input_dtype == np.uint8:
        image_array = ((image_array * 127.5) + 128).astype(np.uint8)
    
    # Run inference
    interpreter.set_tensor(input_details[0]['index'], image_array.astype(input_dtype))
    interpreter.invoke()
    
    # Get output
    output = interpreter.get_tensor(output_details[0]['index'])
    class_id = np.argmax(output[0])
    
    print(f"Predicted class: {class_id}")


# ============================================================================
# EXAMPLE 3: Android (Kotlin) - Mobile Deployment
# ============================================================================

ANDROID_KOTLIN_CODE = """
// Add to build.gradle
dependencies {
    implementation 'org.tensorflow:tensorflow-lite:2.10.0'
    implementation 'org.tensorflow:tensorflow-lite-support:0.4.3'
}

// Usage in Activity/ViewModel
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.ops.ResizeOp
import org.tensorflow.lite.support.image.ops.NormalizeOp
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.common.TensorProcessor
import android.graphics.Bitmap
import java.nio.MappedByteBuffer
import java.io.FileInputStream
import java.nio.channels.FileChannel

class SkinClassifier(private val context: Context) {
    private lateinit var interpreter: Interpreter
    private val labels = listOf("class_0", "class_1", ..., "class_9")
    
    init {
        loadModel()
    }
    
    private fun loadModel() {
        val assetFileDescriptor = context.assets.openFd("skin_classifier.tflite")
        val fileInputStream = FileInputStream(assetFileDescriptor.fileDescriptor)
        val fileChannel = fileInputStream.channel
        
        val startOffset = assetFileDescriptor.startOffset
        val declaredLength = assetFileDescriptor.declaredLength
        
        val modelBuffer = fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
        
        interpreter = Interpreter(modelBuffer)
    }
    
    fun predict(bitmap: Bitmap): Prediction {
        // Preprocess
        val processor = ImageProcessor.Builder()
            .add(ResizeOp(224, 224, ResizeOp.ResizeMethod.BILINEAR))
            .add(NormalizeOp(floatArrayOf(0.485f, 0.456f, 0.406f),
                           floatArrayOf(0.229f, 0.224f, 0.225f)))
            .build()
        
        var tensorImage = TensorImage(DataType.FLOAT32)
        tensorImage.load(bitmap)
        tensorImage = processor.process(tensorImage)
        
        // Inference
        val output = Array(1) { FloatArray(10) }
        interpreter.run(tensorImage.buffer, output)
        
        // Postprocess
        val classId = output[0].withIndex().maxByOrNull { it.value }?.index ?: 0
        val confidence = output[0][classId]
        
        return Prediction(
            classId = classId,
            className = labels[classId],
            confidence = confidence
        )
    }
    
    data class Prediction(
        val classId: Int,
        val className: String,
        val confidence: Float
    )
}

// Usage
val classifier = SkinClassifier(this)
val bitmap = ... // Load image as Bitmap
val result = classifier.predict(bitmap)
println("Predicted: ${result.className} (${result.confidence * 100}%)")
"""


# ============================================================================
# EXAMPLE 4: iOS (Swift) - Mobile Deployment
# ============================================================================

IOS_SWIFT_CODE = """
import TensorFlowLite

class SkinClassifier {
    var interpreter: Interpreter
    let inputSize = CGSize(width: 224, height: 224)
    
    init() throws {
        guard let modelPath = Bundle.main.path(forResource: "skin_classifier", 
                                               ofType: "tflite") else {
            throw NSError(domain: "ModelError", code: -1, 
                         userInfo: ["description": "Model not found"])
        }
        
        interpreter = try Interpreter(modelPath: modelPath)
        try interpreter.allocateTensors()
    }
    
    func predict(image: UIImage) throws -> Prediction {
        // Preprocess
        guard let cgImage = image.cgImage else { throw NSError() }
        
        let buffer = try convertToTensor(cgImage: cgImage)
        
        // Inference
        let inputIndex = 0
        try interpreter.copy(buffer, toInputAt: inputIndex)
        try interpreter.invoke()
        
        // Get output
        let outputIndex = 0
        let output = try interpreter.output(at: outputIndex)
        
        // Postprocess
        let confidences = extractConfidences(output: output)
        let classId = confidences.withIndex().max(by: { $0.element < $1.element })?.offset ?? 0
        let confidence = confidences[classId]
        
        return Prediction(classId: classId, confidence: confidence)
    }
    
    private func convertToTensor(cgImage: CGImage) throws -> Data {
        let width = Int(inputSize.width)
        let height = Int(inputSize.height)
        
        var buffer = [UInt8](repeating: 0, count: 1 * 3 * width * height)
        
        // Normalize and copy pixel data
        // (Implementation depends on color space and format)
        
        return Data(buffer)
    }
    
    private func extractConfidences(output: Tensor) -> [Float] {
        let data = output.data
        let count = output.shape.dimensions.reduce(1, *)
        let floatArray = [Float](unsafeUninitializedCapacity: count) {
            _ in data.copyBytes(to: &$0)
        }
        return floatArray
    }
    
    struct Prediction {
        let classId: Int
        let confidence: Float
    }
}

// Usage
let classifier = try SkinClassifier()
let result = try classifier.predict(image: uiImage)
print("Predicted: \\(result.classId) (\\(result.confidence * 100)%)")
"""


# ============================================================================
# EXAMPLE 5: FastAPI Backend - Server Deployment
# ============================================================================

def example_fastapi_backend():
    """Use ONNX model in FastAPI backend."""
    from fastapi import FastAPI, UploadFile, File
    from pydantic import BaseModel
    import onnxruntime as rt
    import numpy as np
    from PIL import Image
    import io
    
    app = FastAPI()
    
    class PredictionResponse(BaseModel):
        class_id: int
        confidence: float
        probabilities: list
    
    # Load model once at startup
    session = rt.InferenceSession('ml/exports/skin_classifier.onnx')
    
    @app.post("/predict", response_model=PredictionResponse)
    async def predict(file: UploadFile = File(...)):
        """Predict skin type from uploaded image."""
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Preprocess
        image = image.resize((224, 224))
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_array = (image_array - mean) / std
        image_array = np.expand_dims(image_array, axis=0).transpose(0, 3, 1, 2)
        
        # Predict
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        logits = session.run([output_name], {input_name: image_array})[0]
        
        # Softmax
        exp_logits = np.exp(logits[0] - np.max(logits[0]))
        probabilities = exp_logits / np.sum(exp_logits)
        
        return PredictionResponse(
            class_id=int(np.argmax(logits[0])),
            confidence=float(probabilities.max()),
            probabilities=probabilities.tolist()
        )
    
    # Usage: curl -X POST -F "file=@photo.jpg" http://localhost:8000/predict


# ============================================================================
# EXAMPLE 6: Flask Web App
# ============================================================================

FLASK_APP_CODE = """
from flask import Flask, request, jsonify
import onnxruntime as rt
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Load model
session = rt.InferenceSession('ml/exports/skin_classifier.onnx')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    image = Image.open(io.BytesIO(file.read())).convert('RGB')
    
    # Preprocess
    image = image.resize((224, 224))
    image_array = np.array(image, dtype=np.float32) / 255.0
    
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_array = (image_array - mean) / std
    image_array = np.expand_dims(image_array, axis=0).transpose(0, 3, 1, 2)
    
    # Predict
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    logits = session.run([output_name], {input_name: image_array})[0]
    
    # Response
    class_id = int(np.argmax(logits[0]))
    confidence = float(np.exp(logits[0][class_id]) / np.sum(np.exp(logits[0])))
    
    return jsonify({
        'class_id': class_id,
        'confidence': confidence
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
"""


# ============================================================================
# EXAMPLE 7: Command Line Batch Processing
# ============================================================================

BATCH_PROCESSING_CODE = """
import os
import onnxruntime as rt
import numpy as np
from PIL import Image
import csv

# Load model
session = rt.InferenceSession('ml/exports/skin_classifier.onnx')
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# Process directory
image_dir = 'photos/'
output_file = 'predictions.csv'

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['filename', 'class_id', 'confidence'])
    
    for filename in os.listdir(image_dir):
        if not filename.endswith(('.jpg', '.png')):
            continue
        
        # Load and preprocess
        image_path = os.path.join(image_dir, filename)
        image = Image.open(image_path).convert('RGB')
        image = image.resize((224, 224))
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_array = (image_array - mean) / std
        image_array = np.expand_dims(image_array, axis=0).transpose(0, 3, 1, 2)
        
        # Predict
        logits = session.run([output_name], {input_name: image_array})[0]
        class_id = np.argmax(logits[0])
        confidence = np.exp(logits[0][class_id]) / np.sum(np.exp(logits[0]))
        
        # Write results
        writer.writerow([filename, class_id, float(confidence)])
        print(f'{filename}: Class {class_id} ({confidence:.2%})')
"""


# ============================================================================
# EXAMPLE 8: Docker Container - Production Deployment
# ============================================================================

DOCKERFILE_CODE = """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/exports/skin_classifier.onnx .
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
"""

DOCKER_COMPOSE_CODE = """
version: '3.8'

services:
  skin_classifier:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MODEL_PATH=/app/skin_classifier.onnx
    restart: always
"""


# ============================================================================
# USAGE GUIDE
# ============================================================================

USAGE_GUIDE = """
Quick Start Guide for Exported Models

1. ONNX Model (ml/exports/skin_classifier.onnx)
   - Best for: Desktop, server, web backends
   - Platform: CPU/GPU, Windows/Linux/Mac
   - Dependencies: onnxruntime
   - Speed: Fast, cross-platform

2. TFLite Model (ml/exports/skin_classifier.tflite)
   - Best for: Mobile, embedded, edge devices
   - Platform: iOS, Android, Raspberry Pi
   - Dependencies: TensorFlow Lite runtime (lightweight)
   - Speed: Very fast, optimized for mobile

Export your trained model:

    python ml/exports/export_models.py \\
        --checkpoint ml/exports/skin_classifier.pth \\
        --format both \\
        --quantize float16

Test the exports:

    python ml/exports/example_inference.py \\
        --image test_photo.jpg \\
        --mode benchmark

Quick predictions:

    # ONNX (server)
    python ml/exports/example_inference.py --onnx skin_classifier.onnx --image photo.jpg

    # TFLite (mobile)
    python ml/exports/example_inference.py --tflite skin_classifier.tflite --image photo.jpg

Integration examples:
- Desktop: See example_onnx_desktop() in this file
- Mobile Android: See ANDROID_KOTLIN_CODE
- Mobile iOS: See IOS_SWIFT_CODE
- Web Backend (FastAPI): See example_fastapi_backend()
- Web Backend (Flask): See FLASK_APP_CODE
- Batch Processing: See BATCH_PROCESSING_CODE
- Docker: See DOCKERFILE_CODE and DOCKER_COMPOSE_CODE
"""

if __name__ == '__main__':
    print(USAGE_GUIDE)
    print("\nFor detailed information, see EXPORT_GUIDE.md")
