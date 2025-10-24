"""
Pytest configuration for ML tests.

This file is automatically discovered by pytest and provides shared fixtures
and configuration for all tests in the ml/tests directory.
"""

import pytest
import sys
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def setup_python_path():
    """Ensure backend module is importable."""
    backend_path = Path(__file__).parent.parent.parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on class names."""
    for item in items:
        # Add 'smoke' marker if in TestClassificationSmoke or TestDetectionSmoke
        if "TestClassificationSmoke" in str(item.nodeid) or \
           "TestDetectionSmoke" in str(item.nodeid):
            item.add_marker(pytest.mark.smoke)
        
        # Add 'integration' marker if in TestIntegration
        if "TestIntegration" in str(item.nodeid):
            item.add_marker(pytest.mark.integration)
        
        # Add 'unit' marker if in other Test classes
        if "Test" in str(item.nodeid):
            item.add_marker(pytest.mark.unit)


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "smoke: smoke tests for basic functionality"
    )
    config.addinivalue_line(
        "markers", "unit: unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests for full pipeline"
    )
