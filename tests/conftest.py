def pytest_configure(config):
    # Declare custom marker for staging tests
    config.addinivalue_line(
        "markers", "staging"
    )
