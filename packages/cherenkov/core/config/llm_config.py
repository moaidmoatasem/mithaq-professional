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

# LiteLLM proxy configuration (all model calls route through this)
# See AGENTS.md section 9 rule 1: Never call Ollama directly from product code
LITELLM_PROXY_URL = "http://localhost:4000"

# Foundation-Sec-8B model alias (routed via LiteLLM proxy)
# The proxy maps this alias to foundation-sec-8b-reasoning backing model
FOUNDATION_SEC_MODEL = "architect"

# Ollama configuration (direct for CLI tools only, not product code)
OLLAMA_BASE_URL = "http://localhost:11434"
