import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "packages")))

# Must be set before any test module imports auth.py (module-level guard raises RuntimeError otherwise)
os.environ.setdefault("CHERENKOV_JWT_SECRET", "test-only-secret-key-not-for-production")
os.environ.setdefault("GROQ_API_KEY", "mock_key")

import pytest


def pytest_runtest_setup(item):
    """Skip integration tests if using dummy API keys."""
    if "integration" in [mark.name for mark in item.iter_markers()]:
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        groq_key = os.environ.get("GROQ_API_KEY", "")
        if openai_key.startswith("dummy") or groq_key.startswith("dummy") or groq_key == "mock_key":
            pytest.skip("Skipping integration test: Real API keys required.")
