"""
Pytest configuration for the Haski project.

This conftest.py sets up pytest to properly handle imports across the project.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path so absolute imports work
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Also add the main directory
main_dir = Path(__file__).parent
sys.path.insert(0, str(main_dir))
