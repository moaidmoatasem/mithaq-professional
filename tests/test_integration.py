#!/usr/bin/env python3
"""
CHERENKOV — Integration Test Suite
Validates the UnifiedLLMClient class connectivity, inference latency, 
and reasoning capability against local servers (Ollama or vLLM).
Supports mock execution when CI=true is set to run in isolated CI environments.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path
import pytest

# Add src to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from vllm_client import UnifiedLLMClient


@pytest.mark.integration
class TestLLMIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # We test with the Ollama backend by default, as it's the current control.
        # Can easily be changed to 'vllm' during the serving stage of the roadmap.
        cls.backend = "ollama"
        cls.model_name = "qwen2.5-coder:7b"
        cls.is_ci = os.environ.get("CI") == "true"
        
        print(f"\n[Test Setup] Initializing test client targeting backend: {cls.backend.upper()} (CI Mode: {cls.is_ci})")
        cls.client = UnifiedLLMClient(backend=cls.backend, model_name=cls.model_name, max_retries=2)
        
        if cls.is_ci:
            # Mock the chat completions creation endpoint
            mock_choice = MagicMock()
            mock_choice.message.content = "Cherenkov Online. I have audited this code. SQL Injection vulnerability discovered."
            
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            
            cls.client.client = MagicMock()
            cls.client.client.chat.completions.create = MagicMock(return_value=mock_response)

    def test_01_client_initialization(self):
        """Verify client initializes variables and configuration correctly."""
        self.assertEqual(self.client.backend, self.backend)
        self.assertEqual(self.client.model_name, self.model_name)
        self.assertIn("http://", self.client.base_url)

    def test_02_endpoint_connectivity_and_inference(self):
        """Test simple inference generation. Assumes local server is running or in CI."""
        print("\n[Running Integration Test 02: Simple Inference]")
        test_prompt = "Say only: 'Cherenkov Online'."
        
        try:
            response = self.client.generate(
                prompt=test_prompt,
                system_prompt="You are a helpful assistant.",
                max_tokens=64
            )
            print(f"      Server response: '{response.strip()}'")
            
            # Simple assertions on response
            self.assertIsNotNone(response)
            self.assertGreater(len(response), 0)
            self.assertIn("Cherenkov", response)
            
        except Exception as e:
            if self.is_ci:
                self.fail(f"Mocked inference failed in CI: {e}")
            else:
                self.fail(
                    f"Integration test failed to connect to local server: {e}\n"
                    f"Please ensure Ollama is serving on port 11434 with model '{self.model_name}' loaded."
                )

    def test_03_security_reasoning(self):
        """Test that the model returns expected security terms for insecure patterns."""
        print("\n[Running Integration Test 03: Security Reasoning validation]")
        insecure_snippet = "cursor.execute('SELECT * FROM users WHERE id = ' + user_id)"
        
        prompt = f"Does this code have a vulnerability? Explain why in 1 sentence: `{insecure_snippet}`"
        
        try:
            response = self.client.generate(
                prompt=prompt,
                max_tokens=128
            )
            print(f"      Reasoning response: '{response.strip()}'")
            
            # Convert response to lowercase to make checking robust
            lower_response = response.lower()
            
            # We expect the model to identify SQL Injection
            self.assertTrue(
                "sql" in lower_response or "injection" in lower_response or "vuln" in lower_response,
                f"Model failed to detect SQL injection in response: {response}"
            )
            
        except Exception as e:
            self.fail(f"Reasoning test failed: {e}")

    def test_04_metrics_tracking(self):
        """Verify metrics collection aggregates requests, latency, and throughput."""
        report = self.client.get_performance_report()
        self.assertGreaterEqual(report["total_requests"], 1)
        self.assertGreaterEqual(report["total_tokens"], 1)
        self.assertGreaterEqual(report["total_latency_seconds"], 0.0)
        self.assertGreaterEqual(report["avg_tokens_per_second"], 0.0)
        self.assertEqual(report["circuit_state"], "CLOSED")
        
        print("\n[Performance Metrics Collected in Session]")
        for k, v in report.items():
            print(f"      {k}: {v}")

    def test_05_ablation_redaction(self):
        """Verify that the AblationSanitizer correctly redacts sensitive patterns."""
        print("\n[Running Integration Test 05: ABLATION Redaction verification]")
        from ablation import AblationSanitizer
        
        raw_code = 'db_password = "MySuperSecretPassword123!"\nemail = "dev@sovereign.security"\nkey = "-----BEGIN RSA PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQD..."\n-----END RSA PRIVATE KEY-----'
        sanitized = AblationSanitizer.sanitize(raw_code)
        
        self.assertNotIn("MySuperSecretPassword123!", sanitized)
        self.assertNotIn("dev@sovereign.security", sanitized)
        self.assertNotIn("-----BEGIN RSA PRIVATE KEY-----", sanitized)
        
        self.assertIn("[REDACTED_DB_PASSWORD]", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertIn("[REDACTED_PRIVATE_KEY]", sanitized)
        print("      Ablation successfully redacted secret variable, email, and private key.")

    def test_06_circuit_breaker_transitions(self):
        """Test the state transitions of the simulated MEISSNER circuit breaker."""
        print("\n[Running Integration Test 06: MEISSNER Circuit Breaker transitions]")
        import time
        
        # Test client with low failure threshold for test control
        faulty_client = UnifiedLLMClient(
            backend="vllm",
            base_url="http://localhost:9999/v1",  # Invalid port to force failures
            max_retries=1,
            failure_threshold=2,
            cooldown_seconds=1.0
        )
        
        # Initially CLOSED
        self.assertEqual(faulty_client.breaker.state, "CLOSED")
        
        # Trigger failure 1 (threshold is 2)
        response1 = faulty_client.generate("Trigger SQL check")
        # Should drop to rule-based fallback since LLM call fails
        self.assertIn("[FALLBACK SCAN]", response1)
        self.assertIn("Potential SQL Injection Vulnerability", response1)
        self.assertEqual(faulty_client.breaker.state, "CLOSED")
        
        # Trigger failure 2 (circuit should trip to OPEN)
        response2 = faulty_client.generate("Trigger RCE system")
        self.assertIn("[FALLBACK SCAN]", response2)
        self.assertEqual(faulty_client.breaker.state, "OPEN")
        
        # When OPEN, a new request is immediately blocked and routed to fallback without calling OpenAI client
        response3 = faulty_client.generate("password check")
        self.assertIn("[FALLBACK SCAN]", response3)
        self.assertEqual(faulty_client.breaker.state, "OPEN")
        
        # Wait for cooldown to expire
        time.sleep(1.1)
        
        # State check should shift it to HALF_OPEN when calling generate
        response4 = faulty_client.generate("normal scan")
        # Because the port is still down, the attempt in HALF_OPEN fails, and immediately trips back to OPEN
        self.assertIn("[FALLBACK SCAN]", response4)
        self.assertEqual(faulty_client.breaker.state, "OPEN")
        print("      Circuit breaker successfully transitioned CLOSED -> OPEN -> HALF_OPEN -> OPEN and routed to Fallback.")

    def test_07_frida_sanitization(self):
        """Verify that the FridaInputSanitizer successfully strips malicious characters."""
        print("\n[Running Integration Test 07: FRIDA Hook Input Sanitization verification]")
        from frida_sanitizer import FridaInputSanitizer
        
        malicious_hooks = [
            "com.bank.app.LoginClass.submit\"; alert('INJECTED'); //",
            "com.bank.app.RootCheck.isDeviceRooted"
        ]
        
        script = FridaInputSanitizer.generate_safe_frida_script("android", malicious_hooks)
        
        # Verify that the injection attempt is neutralized
        self.assertNotIn("submit\"; alert('INJECTED'); //", script)
        # Check that it's stripped to clean safe chars
        self.assertIn("submitalertINJECTED", script)
        self.assertIn("com.bank.app.RootCheck.isDeviceRooted", script)
        print("      Frida sanitizer successfully stripped injection characters and built a safe script.")

    def test_08_health_diagnostics(self):
        """Verify that the AutonomicHealthGateway correctly performs diagnostics checks."""
        print("\n[Running Integration Test 08: Autonomic Health & Readiness Diagnostics verification]")
        from health_diagnostics import AutonomicHealthGateway
        
        diag_engine = AutonomicHealthGateway()
        
        # Test 1: Liveness check
        live_ok, live_details = diag_engine.check_liveness()
        self.assertTrue(live_ok)
        self.assertIn("uptime_seconds", live_details)
        self.assertIn("pid", live_details)
        
        # Test 2: Readiness check
        ready_ok, ready_details = diag_engine.check_readiness()
        self.assertTrue(ready_ok)
        self.assertEqual(ready_details["database"]["status"], "OK")
        self.assertEqual(ready_details["inference_runtime"]["status"], "OK")
        print("      Liveness and Readiness checks completed with verified OK statuses.")

    def test_09_security_gateway(self):
        """Verify that the security gateway middleware correctly enforces limits and authenticates websockets."""
        print("\n[Running Integration Test 09: Autonomic Security Gateway Middleware verification]")
        from security_gateway import SlidingWindowRateLimiter, WebSocketAuthenticator
        import jwt
        
        # 1. Rate limiter test
        limiter = SlidingWindowRateLimiter(limit=2, window_seconds=2.0)
        ok1, rem1 = limiter.is_allowed("10.0.0.5")
        self.assertTrue(ok1)
        self.assertEqual(rem1, 1)
        
        ok2, rem2 = limiter.is_allowed("10.0.0.5")
        self.assertTrue(ok2)
        self.assertEqual(rem2, 0)
        
        ok3, rem3 = limiter.is_allowed("10.0.0.5")
        self.assertFalse(ok3)
        self.assertEqual(rem3, 0)
        
        # 2. WebSocket authenticator test
        auth = WebSocketAuthenticator()
        payload = {"sub": "admin_test", "role": "admin"}
        token = jwt.encode(payload, auth.secret_key, algorithm=auth.algorithm)
        
        # Validate query string extraction
        auth_ok, user_payload = auth.validate_connection(f"token={token}")
        self.assertTrue(auth_ok)
        self.assertEqual(user_payload["sub"], "admin_test")
        
        # Validate header extraction
        auth_ok2, user_payload2 = auth.validate_connection("", headers={"Authorization": f"Bearer {token}"})
        self.assertTrue(auth_ok2)
        self.assertEqual(user_payload2["sub"], "admin_test")
        print("      Rate limiter blocked excess requests and WebSocket successfully verified JWTs.")


if __name__ == "__main__":
    unittest.main()
