import time
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to PYTHONPATH
sys.path.insert(0, os.path.abspath("src"))

# Mock requests before importing scanner
import sys
import types
mock_requests = types.ModuleType("requests")
mock_exceptions = types.ModuleType("exceptions")
mock_requests.exceptions = mock_exceptions
mock_requests.exceptions.ConnectionError = Exception
mock_requests.exceptions.Timeout = Exception
mock_requests.exceptions.SSLError = Exception

def mock_request(method, url, timeout=5):
    time.sleep(1) # simulate network delay
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    return mock_resp

def mock_get(url, timeout=5):
    time.sleep(1)
    mock_resp = MagicMock()
    mock_resp.headers = {}
    return mock_resp

mock_requests.request = mock_request
mock_requests.get = mock_get
sys.modules["requests"] = mock_requests

from mithaq.scanners.header_scanner import SimpleScanner

def test_performance():
    scanner = SimpleScanner("https://example.com")

    start_time = time.time()
    scanner.scan_http_methods()
    end_time = time.time()

    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    test_performance()
