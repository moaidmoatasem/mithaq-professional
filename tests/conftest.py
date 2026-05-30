import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "packages")))

# Must be set before any test module imports auth.py (module-level guard raises RuntimeError otherwise)
os.environ.setdefault("CHERENKOV_JWT_SECRET", "test-only-secret-key-not-for-production")

import pytest
import sqlite3
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_sqlite_connect(tmp_path):
    test_db = tmp_path / "cherenkov_test.db"
    original_connect = sqlite3.connect

    def mock_connect(database, *args, **kwargs):
        if isinstance(database, (str, os.PathLike)) and (
            "results.db" in str(database)
            or "test_api.db" in str(database)
            or "cherenkov" in str(database)
            or "test.db" in str(database)
        ):
            return original_connect(str(test_db), *args, **kwargs)
        return original_connect(database, *args, **kwargs)

    with patch("sqlite3.connect", side_effect=mock_connect):
        yield


def pytest_runtest_setup(item):
    """Skip integration tests if using dummy API keys."""
    if "integration" in [mark.name for mark in item.iter_markers()]:
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        groq_key = os.environ.get("GROQ_API_KEY", "")
        if openai_key.startswith("dummy") or groq_key.startswith("dummy"):
            pytest.skip("Skipping integration test: Real API keys required.")
