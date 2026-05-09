"""LLM configuration for cherenkov framework."""

# Default LLM model for all agents (using smallest model to fit in memory)
DEFAULT_LLM_MODEL = "ollama/qwen2.5:3b"

# Alternative models
ALTERNATIVE_MODELS = {
    "fast": "ollama/qwen2.5:3b",
    "coder": "ollama/qwen2.5-coder:7b",  # Requires 4.3 GB RAM
    "reasoning": "ollama/deepseek-coder-v2:16b",  # Requires 8+ GB RAM
    "balanced": "ollama/qwen3.5:latest",  # Requires 6+ GB RAM
}

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
