import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages"))

import pytest


def pytest_runtest_setup(item):
    """Skip integration tests if using dummy API keys."""
    if "integration" in [mark.name for mark in item.iter_markers()]:
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        groq_key = os.environ.get("GROQ_API_KEY", "")
        if openai_key.startswith("dummy") or groq_key.startswith("dummy"):
            pytest.skip("Skipping integration test: Real API keys required.")
