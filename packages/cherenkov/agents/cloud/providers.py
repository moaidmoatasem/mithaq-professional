"""
LLM Provider Abstraction
Handles communication with different cloud LLM providers (Groq, Gemini).
"""

import os
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# Conditional imports
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        pass


class GroqProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        if Groq is None:
            raise ImportError("groq package is not installed")
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        self.client = Groq(api_key=self.api_key)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=2048,
        )
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "model": self.model,
        }


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        if genai is None:
            raise ImportError("google-generativeai package is not installed")
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        # Combine system and user prompts for Gemini if needed, 
        # but Gemini 1.5 supports system_instruction in constructor or as first message
        chat = self.model.start_chat(history=[])
        
        # Using a simple combined prompt if system_instruction wasn't set in __init__
        # but let's assume we want to be explicit
        full_prompt = f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}"
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        
        # Note: token counting in Gemini is separate
        return {
            "content": response.text,
            "tokens_used": 0, # To be implemented via response.usage_metadata
            "model": self.model_name,
        }


def get_provider(provider_name: str = "groq", **kwargs) -> LLMProvider:
    if provider_name.lower() == "groq":
        return GroqProvider(**kwargs)
    elif provider_name.lower() == "gemini":
        return GeminiProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
