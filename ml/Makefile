# Haski ML Pipeline Makefile
# ============================================================================
# Make targets for common ML development tasks:
# - Environment setup
# - Model training (classification & detection)
# - Model export
# - Testing
# 
# Usage: make <target>
# Examples:
#   make prep              # Setup environment
#   make train-classifier  # Train skin/hair classifier
#   make export           # Export trained models
#   make test             # Run all tests
# ============================================================================

.PHONY: help prep clean train-classifier train-detector export test lint format install-torch install-yolo

# ============================================================================
# Variables
# ============================================================================

PYTHON := python
PIP := pip
VENV_DIR := venv
DATA_DIR := ml/data/skin_classification
TRAINING_DIR := ml/training
EXPORT_DIR := ml/exports
TEST_DIR := ml/tests
NOTEBOOKS_DIR := ml/notebooks

# Model training defaults (can be overridden: make train-classifier EPOCHS=100)
MODEL := efficientnet_b0
EPOCHS := 50
BATCH_SIZE := 32
LEARNING_RATE := 0.001
OUTPUT_DIR := ml/exports/checkpoints

# Python command with venv activation (Windows)
ifeq ($(OS),Windows_NT)
    ACTIVATE := $(VENV_DIR)\Scripts\activate
    SEP := \
else
    ACTIVATE := . $(VENV_DIR)/bin/activate
    SEP := /
endif

# ============================================================================
# HELP TARGET
# ============================================================================

help:
	@echo "╔════════════════════════════════════════════════════════════════════════╗"
	@echo "║                    Haski ML Pipeline - Makefile                        ║"
	@echo "║                                                                        ║"
	@echo "║ Available targets:                                                     ║"
	@echo "╠════════════════════════════════════════════════════════════════════════╣"
	@echo "║                                                                        ║"
	@echo "║ ENVIRONMENT SETUP                                                      ║"
	@echo "│ ─────────────────────────────────────────────────────────────────────  ║"
	@echo "│ prep              Create venv & install dependencies                   ║"
	@echo "│ install-torch     Install PyTorch (CPU/GPU)                            ║"
	@echo "│ install-yolo      Install YOLOv8 for detection tasks                   ║"
	@echo "│ clean             Remove venv and cache files                          ║"
	@echo "│                                                                        ║"
	@echo "║ TRAINING                                                               ║"
	@echo "│ ─────────────────────────────────────────────────────────────────────  ║"
	@echo "│ train-classifier  Train skin/hair type classifier                      ║"
	@echo "│ train-detector    Train condition detection model (YOLOv8)             ║"
	@echo "│ train-quick       Quick 1-epoch smoke test                             ║"
	@echo "│ train-tuning      Hyperparameter tuning run                            ║"
	@echo "│                                                                        ║"
	@echo "║ MODEL EXPORT                                                           ║"
	@echo "│ ─────────────────────────────────────────────────────────────────────  ║"
	@echo "│ export            Export trained models (ONNX + TFLite)                ║"
	@echo "│                                                                        ║"
	@echo "║ TESTING & VALIDATION                                                   ║"
	@echo "│ ─────────────────────────────────────────────────────────────────────  ║"
	@echo "│ test              Run all tests with pytest                            ║"
	@echo "│ test-smoke        Run smoke tests (quick validation)                   ║"
	@echo "│ test-coverage     Run tests with coverage report                       ║"
	@echo "│ lint              Check code with pylint/flake8                        ║"
	@echo "│ format            Format code with black                               ║"
	@echo "│                                                                        ║"
	@echo "║ UTILITIES                                                              ║"
	@echo "│ ─────────────────────────────────────────────────────────────────────  ║"
	@echo "│ notebook          Run training notebook (Jupyter)                      ║"
	@echo "│ status            Check environment status                             ║"
	@echo "│                                                                        ║"
	@echo "║ EXAMPLES:                                                              ║"
	@echo "│ ─────────────────────────────────────────────────────────────────────  ║"
	@echo "│ make prep                                                              ║"
	@echo "│ make train-classifier EPOCHS=100 BATCH_SIZE=64                        ║"
	@echo "│ make train-detector                                                    ║"
	@echo "│ make export                                                            ║"
	@echo "│ make test                                                              ║"
	@echo "│                                                                        ║"
	@echo "╚════════════════════════════════════════════════════════════════════════╝"

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

prep: venv install
	@echo "✅ Environment setup complete!"
	@echo "📌 To activate virtual environment, run:"
	@echo "   Windows: $(VENV_DIR)\Scripts\activate"
	@echo "   Linux/Mac: source $(VENV_DIR)/bin/activate"

venv:
	@echo "🔧 Creating virtual environment..."
ifeq ($(OS),Windows_NT)
	python -m venv $(VENV_DIR)
	@echo "✅ Virtual environment created at $(VENV_DIR)"
else
	python3 -m venv $(VENV_DIR)
	@echo "✅ Virtual environment created at $(VENV_DIR)"
endif

install:
	@echo "📦 Installing base dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r ml/requirements.txt
	@echo "✅ Base dependencies installed"

install-torch:
	@echo "🔥 Installing PyTorch..."
	@echo "   Options:"
	@echo "   - make install-torch-cu118  (CUDA 11.8 - recommended for NVIDIA GPU)"
	@echo "   - make install-torch-cu121  (CUDA 12.1 - for newer NVIDIA GPU)"
	@echo "   - make install-torch-cpu    (CPU only)"
	@echo "   - make install-torch-mps    (Apple Metal Performance Shaders)"
	@echo ""
	@echo "   Running default (CPU)..."
	$(PIP) install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

install-torch-cu118:
	@echo "🔥 Installing PyTorch with CUDA 11.8 support..."
	$(PIP) install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
	@echo "✅ PyTorch CUDA 11.8 installed"

install-torch-cu121:
	@echo "🔥 Installing PyTorch with CUDA 12.1 support..."
	$(PIP) install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
	@echo "✅ PyTorch CUDA 12.1 installed"

install-torch-cpu:
	@echo "🔥 Installing PyTorch CPU version..."
	$(PIP) install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
	@echo "✅ PyTorch CPU installed"

install-torch-mps:
	@echo "🔥 Installing PyTorch with Metal Performance Shaders (Apple)..."
	$(PIP) install torch torchvision torchaudio
	@echo "✅ PyTorch MPS installed"

install-yolo:
	@echo "🎯 Installing YOLOv8 for detection tasks..."
	$(PIP) install ultralytics
	@echo "✅ YOLOv8 installed"
	@echo "   Usage: yolo detect train data=path/to/data.yaml model=yolov8n.pt epochs=100"

# ============================================================================
# TRAINING TARGETS
# ============================================================================

train-classifier:
	@echo "🎓 Training skin/hair classifier..."
	@echo "   Model: $(MODEL)"
	@echo "   Epochs: $(EPOCHS)"
	@echo "   Batch size: $(BATCH_SIZE)"
	@echo "   Learning rate: $(LEARNING_RATE)"
	@echo "   Data directory: $(DATA_DIR)"
	@echo ""
	$(PYTHON) $(TRAINING_DIR)/train_classifier.py \
		--data-dir $(DATA_DIR) \
		--model $(MODEL) \
		--epochs $(EPOCHS) \
		--batch-size $(BATCH_SIZE) \
		--learning-rate $(LEARNING_RATE) \
		--output-dir $(OUTPUT_DIR)
	@echo "✅ Training complete! Checkpoints saved to $(OUTPUT_DIR)"

train-classifier-quick:
	@echo "⚡ Running quick 1-epoch smoke test..."
	$(PYTHON) $(TRAINING_DIR)/train_classifier.py \
		--data-dir $(DATA_DIR) \
		--model $(MODEL) \
		--epochs 1 \
		--batch-size 16 \
		--output-dir $(OUTPUT_DIR)
	@echo "✅ Smoke test complete!"

train-classifier-resnet:
	@echo "🎓 Training with ResNet50 architecture..."
	$(MAKE) train-classifier MODEL=resnet50

train-classifier-tuning:
	@echo "🔬 Running hyperparameter tuning..."
	@echo "   This will try multiple configurations:"
	@echo "   - Batch sizes: 16, 32, 64"
	@echo "   - Learning rates: 0.0001, 0.001, 0.01"
	@echo "   - Expected time: 2-4 hours"
	@echo ""
	$(PYTHON) $(TRAINING_DIR)/train_classifier.py \
		--data-dir $(DATA_DIR) \
		--model $(MODEL) \
		--epochs $(EPOCHS) \
		--batch-size 32 \
		--learning-rate 0.001 \
		--output-dir $(OUTPUT_DIR) \
		--tune-hyperparams
	@echo "✅ Hyperparameter tuning complete!"

train-detector:
	@echo "🎯 Training condition detection model with YOLOv8..."
	@echo "   Prerequisites:"
	@echo "   1. Install YOLOv8: make install-yolo"
	@echo "   2. Prepare YOLO dataset at: ml/data/yolo/"
	@echo "   3. Dataset should have structure:"
	@echo "      ml/data/yolo/images/train/, ml/data/yolo/images/val/"
	@echo "      ml/data/yolo/labels/train/, ml/data/yolo/labels/val/"
	@echo "      ml/data/yolo/data.yaml (with class names)"
	@echo ""
	@echo "   Running YOLOv8 training..."
	@echo "   (This command requires YOLOv8 CLI installed)"
	@echo ""
	yolo detect train data=ml/data/yolo/data.yaml model=yolov8n.pt epochs=100 imgsz=640 device=0
	@echo "✅ Detection model training complete!"

train-detector-cpu:
	@echo "🎯 Training condition detection model on CPU..."
	yolo detect train data=ml/data/yolo/data.yaml model=yolov8n.pt epochs=100 imgsz=640 device=cpu
	@echo "✅ Detection model training complete (CPU)!"

# ============================================================================
# MODEL EXPORT
# ============================================================================

export:
	@echo "📦 Exporting trained models to ONNX and TFLite..."
	@echo "   This will:"
	@echo "   1. Load trained model from checkpoints"
	@echo "   2. Export to ONNX format (cross-platform)"
	@echo "   3. Export to TFLite format (mobile optimization)"
	@echo "   4. Generate metadata files"
	@echo ""
	$(PYTHON) $(EXPORT_DIR)/export_models.py \
		--checkpoint-dir $(OUTPUT_DIR) \
		--output-dir $(EXPORT_DIR)
	@echo "✅ Models exported!"
	@echo "   📍 Outputs:"
	@echo "   - ONNX models: $(EXPORT_DIR)/*.onnx"
	@echo "   - TFLite models: $(EXPORT_DIR)/*.tflite"
	@echo "   - Metadata: $(EXPORT_DIR)/*_metadata.json"

export-onnx:
	@echo "📦 Exporting to ONNX format only..."
	$(PYTHON) $(EXPORT_DIR)/export_models.py \
		--checkpoint-dir $(OUTPUT_DIR) \
		--output-dir $(EXPORT_DIR) \
		--format onnx
	@echo "✅ ONNX export complete!"

export-tflite:
	@echo "📦 Exporting to TFLite format only..."
	$(PYTHON) $(EXPORT_DIR)/export_models.py \
		--checkpoint-dir $(OUTPUT_DIR) \
		--output-dir $(EXPORT_DIR) \
		--format tflite
	@echo "✅ TFLite export complete!"

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

test:
	@echo "🧪 Running all tests..."
	$(PYTHON) -m pytest $(TEST_DIR)/ -v --tb=short
	@echo "✅ All tests complete!"

test-smoke:
	@echo "💨 Running smoke tests (quick validation)..."
	$(PYTHON) -m pytest $(TEST_DIR)/test_inference_smoke.py -v
	@echo "✅ Smoke tests complete!"

test-coverage:
	@echo "📊 Running tests with coverage report..."
	$(PYTHON) -m pytest $(TEST_DIR)/ \
		--cov=ml \
		--cov-report=html \
		--cov-report=term-missing \
		-v
	@echo "✅ Coverage report generated: htmlcov/index.html"

test-verbose:
	@echo "🧪 Running all tests with verbose output..."
	$(PYTHON) -m pytest $(TEST_DIR)/ -vv --tb=long
	@echo "✅ Tests complete!"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:
	@echo "🔍 Checking code quality with pylint..."
	@echo "   Checking training code..."
	$(PYTHON) -m pylint $(TRAINING_DIR)/*.py --disable=all --enable=E,F || true
	@echo ""
	@echo "   Checking export code..."
	$(PYTHON) -m pylint $(EXPORT_DIR)/*.py --disable=all --enable=E,F || true
	@echo ""
	@echo "✅ Lint check complete!"

format:
	@echo "🎨 Formatting code with black..."
	$(PYTHON) -m black $(TRAINING_DIR)/ --line-length 100
	$(PYTHON) -m black $(EXPORT_DIR)/ --line-length 100
	$(PYTHON) -m black $(TEST_DIR)/ --line-length 100
	@echo "✅ Code formatting complete!"

# ============================================================================
# JUPYTER NOTEBOOK
# ============================================================================

notebook:
	@echo "📓 Starting Jupyter notebook..."
	@echo "   Training notebook: $(NOTEBOOKS_DIR)/train_classifier_starter.py"
	@echo ""
	jupyter notebook $(NOTEBOOKS_DIR)/
	@echo ""

# ============================================================================
# UTILITY TARGETS
# ============================================================================

status:
	@echo "📊 Environment Status Report"
	@echo "════════════════════════════════════════════"
	@echo ""
	@echo "Python version:"
	@which python
	python --version
	@echo ""
	@echo "PyTorch installation:"
	$(PYTHON) -c "import torch; print(f'Version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.device(\"cuda\" if torch.cuda.is_available() else \"cpu\")}')" || echo "PyTorch not installed"
	@echo ""
	@echo "Installed packages (ML-related):"
	$(PIP) list | grep -E "torch|numpy|opencv|scikit|matplotlib" || echo "Use 'make prep' to install dependencies"
	@echo ""
	@echo "Data directories:"
	@ls -la $(DATA_DIR) 2>/dev/null || echo "   $(DATA_DIR) not found"
	@echo ""
	@echo "Checkpoint directories:"
	@ls -la $(OUTPUT_DIR) 2>/dev/null || echo "   $(OUTPUT_DIR) not found"
	@echo ""
	@echo "✅ Status check complete!"

clean:
	@echo "🧹 Cleaning up..."
	@echo "   Removing __pycache__..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "   Removing .pytest_cache..."
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "   Removing .coverage..."
	find . -name .coverage -delete 2>/dev/null || true
	@echo ""
	@echo "🗑️  Full cleanup - remove virtual environment:"
	@echo "   make clean-full"

clean-full: clean
	@echo "🗑️  Removing virtual environment..."
ifeq ($(OS),Windows_NT)
	rmdir /s /q $(VENV_DIR) 2>/dev/null || echo "   $(VENV_DIR) not found"
else
	rm -rf $(VENV_DIR)
endif
	@echo "✅ Full cleanup complete! Run 'make prep' to set up again."

# ============================================================================
# ADVANCED WORKFLOWS
# ============================================================================

full-pipeline: prep install-torch train-classifier export test
	@echo ""
	@echo "🎉 Full ML pipeline complete!"
	@echo "   ✅ Environment ready"
	@echo "   ✅ Classifier trained"
	@echo "   ✅ Models exported"
	@echo "   ✅ All tests passed"

quick-start: prep train-classifier-quick test-smoke
	@echo ""
	@echo "🚀 Quick start complete!"
	@echo "   Next steps:"
	@echo "   1. Prepare your dataset at: $(DATA_DIR)"
	@echo "   2. Run full training: make train-classifier EPOCHS=50"
	@echo "   3. Export models: make export"

dev-setup: prep lint format
	@echo ""
	@echo "👨‍💻 Development environment ready!"
	@echo "   Code formatted and linted"
	@echo "   Ready for development"

# ============================================================================
# DEFAULT TARGET
# ============================================================================

.DEFAULT_GOAL := help

# ============================================================================
# END OF MAKEFILE
# ============================================================================
