"""
Configuration file for pytest
"""

import pytest
import warnings


def pytest_configure(config):
    """Configure pytest"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture(autouse=True)
def reset_warnings():
    """Reset warnings for each test"""
    warnings.simplefilter("always")
    yield
    warnings.simplefilter("default")


@pytest.fixture
def suppress_warnings():
    """Suppress warnings in specific tests if needed"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield
