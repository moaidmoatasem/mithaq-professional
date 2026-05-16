"""
Ollama Local LLM Client
Handles communication with local Ollama models for privileged operations.
"""

import json
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field


class OllamaConfig(BaseModel):
    """Configuration for Ollama client"""

    base_url: str = Field(default="http://localhost:11434")
    model: str = Field(default="qwen2.5:3b")
    temperature: float = Field(default=0.2)
    timeout: int = Field(default=120)


class OllamaResponse(BaseModel):
    """Response from Ollama"""

    response: str
    model: str
    total_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None


class OllamaClient:
    """
    Local Ollama LLM client for security analysis.
    Runs 100% locally - never sends data externally.
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.base_url = self.config.base_url
        self.model = self.config.model

    def is_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> OllamaResponse:
        """
        Generate completion from Ollama.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            OllamaResponse with generated text
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature or self.config.temperature},
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()

            return OllamaResponse(
                response=data.get("response", ""),
                model=data.get("model", self.model),
                total_duration=data.get("total_duration"),
                prompt_eval_count=data.get("prompt_eval_count"),
                eval_count=data.get("eval_count"),
            )

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

    def analyze_code(
        self, code: str, language: str = "python", focus: str = "security"
    ) -> Dict[str, Any]:
        """
        Analyze code for security issues.

        Args:
            code: Source code to analyze
            language: Programming language
            focus: Analysis focus (security, quality, performance)

        Returns:
            Analysis results
        """

        system_prompt = f"""You are a security code reviewer specializing in {language}.
Analyze code for vulnerabilities, insecure patterns, and security risks.
Focus on: SQL injection, XSS, hardcoded secrets, insecure crypto, auth issues.
Provide specific findings with severity levels."""

        user_prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code}
```

Provide findings in this format:
1. Vulnerability type
2. Severity (Critical/High/Medium/Low)
3. Line numbers affected
4. Description
5. Remediation advice
"""

        response = self.generate(user_prompt, system_prompt=system_prompt)

        return {
            "findings": response.response,
            "model": response.model,
            "language": language,
            "focus": focus,
            "eval_tokens": response.eval_count,
        }

    def analyze_threat_model(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate threat model for given context.

        Args:
            context: Application context information

        Returns:
            Threat model analysis
        """

        system_prompt = """You are a threat modeling expert using STRIDE methodology.
Analyze applications for: Spoofing, Tampering, Repudiation,
Information Disclosure, Denial of Service, Elevation of Privilege."""

        context_str = json.dumps(context, indent=2)

        user_prompt = f"""Create a threat model for this application:

{context_str}

Identify top 5 threats using STRIDE, each with:
1. Threat category
2. Attack scenario
3. Impact assessment
4. Mitigation strategy
"""

        response = self.generate(user_prompt, system_prompt=system_prompt)

        return {
            "threat_model": response.response,
            "model": response.model,
            "methodology": "STRIDE",
            "eval_tokens": response.eval_count,
        }
