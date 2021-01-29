import os
import sys
import pytest
# Add parent directory as module search path
sys.path.append(os.path.dirname(__file__) + "/..")


# Prepare flask for testing
from main import app as _app # noqa
_app.config['TESTING'] = True

@pytest.fixture
def app():
    return _app


def pytest_configure(config):
    # Declare custom marker for staging tests
    config.addinivalue_line(
        "markers", "staging"
    )
