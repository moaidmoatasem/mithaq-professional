#!/usr/bin/env python3
"""
CHERENKOV — Backend API Integration Tests
Asserts server health routes, authorization status updates, credential rotation limits,
JWT token signatures, and rate limiting rules.
"""

import sys
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add packages to path
sys.path.append(str(Path(__file__).parent.parent / "packages"))
sys.path.append(str(Path(__file__).parent.parent))

from cherenkov.meissner.server import app
from cherenkov.credentials import DefaultCredentialsManager


class TestCherenkovAPIServer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        os.environ["CI"] = "true"
        os.environ["CHERENKOV_FORCE_ROTATION"] = "true"
        cls.client = TestClient(app)

    def test_01_health_diagnostics_route(self):
        """Verify the diagnostics endpoints serve correct operational state."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("rotation_required", data)
        self.assertIn("liveness", data)
        self.assertIn("readiness", data)
        self.assertEqual(data["readiness"]["database"]["status"], "OK")

    def test_02_credentials_status_route(self):
        """Assert the credentials status reports blocker active."""
        response = self.client.get("/api/auth/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rotation_required"], True)

    def test_03_token_generation_route(self):
        """Assert JWT tokens can be signed correctly."""
        response = self.client.post("/api/auth/token", json={"username": "admin"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_04_credentials_rotation_flow(self):
        """Assert that rotating password unlocks the platform."""
        # 1. Trigger scan while locked -> raises 403 Forbidden
        response_scan_locked = self.client.post("/api/scan", json={"code": "db.query()"})
        self.assertEqual(response_scan_locked.status_code, 403)
        self.assertIn("FIRST-RUN BLOCKER", response_scan_locked.json()["detail"])

        # 2. Perform rotation
        response_rotate = self.client.post("/api/auth/rotate", json={"hash": "sha256_mocked_hash"})
        self.assertEqual(response_rotate.status_code, 200)
        self.assertEqual(response_rotate.json()["status"], "SUCCESS")

        # 3. Check status is now false
        response_status = self.client.get("/api/auth/status")
        self.assertEqual(response_status.json()["rotation_required"], False)

        # 4. Trigger scan after unlocked -> successfully proceeds
        response_scan_unlocked = self.client.post("/api/scan", json={"code": "safe_method()", "backend": "ollama"})
        self.assertEqual(response_scan_unlocked.status_code, 200)
        self.assertEqual(response_scan_unlocked.json()["status"], "SUCCESS")

    def test_05_rate_limiting(self):
        """Assert rate limiter correctly intercepts excessive spamming scan attempts."""
        # Clean request state
        from cherenkov.meissner.server import rate_limiter
        rate_limiter.requests.clear()

        
        # Make 10 allowed requests (limit is 10)
        for i in range(10):
            response = self.client.post("/api/scan", json={"code": "safe_method()"})
            self.assertEqual(response.status_code, 200)

        # 11th request triggers 429 Too Many Requests
        response_spam = self.client.post("/api/scan", json={"code": "spam_method()"})
        self.assertEqual(response_spam.status_code, 429)
        self.assertIn("Rate limit exceeded", response_spam.json()["detail"])

if __name__ == "__main__":
    unittest.main()
