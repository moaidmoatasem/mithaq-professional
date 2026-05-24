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

# Add src to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from vllm_client import UnifiedLLMClient


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
        self.assertGreater(report["total_latency_seconds"], 0)
        self.assertGreater(report["avg_tokens_per_second"], 0)
        
        print("\n[Performance Metrics Collected in Session]")
        for k, v in report.items():
            print(f"      {k}: {v}")


if __name__ == "__main__":
    unittest.main()
