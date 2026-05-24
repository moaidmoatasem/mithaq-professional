#!/usr/bin/env python3
"""
CHERENKOV — vLLM & Ollama Unified Client Interface
Provides a highly reliable, production-grade integration layer for agent inference.
Includes structured logging, retry mechanisms, and analytical metrics tracking.
"""

import time
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

# Setup logging with modern formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CherenkovLLMClient")


class LLMClientMetrics:
    """Tracks latency, token counts, and throughput metrics for auditing."""
    def __init__(self):
        self.total_requests = 0
        self.total_tokens_generated = 0
        self.total_latency_seconds = 0.0

    @property
    def avg_latency(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_latency_seconds / self.total_requests

    @property
    def avg_tokens_per_second(self) -> float:
        if self.total_latency_seconds == 0.0:
            return 0.0
        return self.total_tokens_generated / self.total_latency_seconds

    def record(self, tokens: int, latency: float):
        self.total_requests += 1
        self.total_tokens_generated += tokens
        self.total_latency_seconds += latency


class UnifiedLLMClient:
    """Unified client supporting both local vLLM servers and local Ollama instances."""
    
    def __init__(
        self,
        backend: str = "vllm",  # 'vllm' or 'ollama'
        base_url: Optional[str] = None,
        model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
        timeout: float = 60.0,
        max_retries: int = 3
    ):
        self.backend = backend.lower()
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.metrics = LLMClientMetrics()

        # Set default local ports based on backend type
        if base_url is None:
            if self.backend == "vllm":
                self.base_url = "http://localhost:8080/v1"
            else:
                self.base_url = "http://localhost:11434/v1"
        else:
            self.base_url = base_url

        logger.info(
            f"Initializing client | Backend: {self.backend.upper()} | Model: {self.model_name} | Endpoint: {self.base_url}"
        )
        
        # Instantiate OpenAI-compatible client wrapper
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="EMPTY" if self.backend == "vllm" else "ollama"
        )

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are Cherenkov TENSOR, a sovereign security analysis model. Be precise, strict, and perform comprehensive source-code vulnerability scanning.",
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:
        """Sends a completion request to the served local model with retry support."""
        start_time = time.time()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Sending inference request (Attempt {attempt}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                
                content = response.choices[0].message.content or ""
                latency = time.time() - start_time
                
                # Estimate token count (rough rule of thumb: ~4 characters per token)
                estimated_tokens = len(content) // 4
                self.metrics.record(estimated_tokens, latency)
                
                logger.info(
                    f"Request successful | Latency: {latency:.2f}s | Est. Tokens: {estimated_tokens} | "
                    f"Throughput: {estimated_tokens / latency:.1f} tok/sec"
                )
                return content

            except Exception as e:
                logger.warning(f"Inference attempt {attempt} failed: {str(e)}")
                last_error = e
                if attempt < self.max_retries:
                    # Exponential backoff: 1s, 2s, 4s...
                    sleep_time = 2 ** (attempt - 1)
                    time.sleep(sleep_time)

        logger.error(f"All inference attempts failed. Endpoint unreachable or overloaded.")
        raise last_error if last_error else RuntimeError("Inference failed")

    def get_performance_report(self) -> Dict[str, Any]:
        """Returns statistics for current session metrics."""
        return {
            "backend": self.backend,
            "model": self.model_name,
            "total_requests": self.metrics.total_requests,
            "total_tokens": self.metrics.total_tokens_generated,
            "total_latency_seconds": round(self.metrics.total_latency_seconds, 2),
            "avg_latency_seconds": round(self.metrics.avg_latency, 2),
            "avg_tokens_per_second": round(self.metrics.avg_tokens_per_second, 1)
        }


if __name__ == "__main__":
    # Self-test/runnable demonstration
    print("--- Cherenkov client Interface Self-Test ---")
    try:
        # Defaults to local vLLM. To test Ollama, switch backend="ollama"
        test_client = UnifiedLLMClient(backend="ollama", model_name="qwen2.5-coder:7b")
        
        test_prompt = "Identify potential security issues in this line of code: `user_input = input(); eval(user_input)`"
        print(f"Prompt: {test_prompt}\n")
        
        result = test_client.generate(prompt=test_prompt, max_tokens=256)
        print(f"Response:\n{result}\n")
        
        report = test_client.get_performance_report()
        print("Performance Report:")
        for k, v in report.items():
            print(f"  {k}: {v}")
            
    except Exception as err:
        print(f"\nSelf-test ended with expected exception (if local backend is offline): {err}")
        print("Start Ollama or vLLM to verify the loop connects.")
