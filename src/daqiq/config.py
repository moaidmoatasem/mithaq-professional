"""
DAQIQ Configuration
Hardware-optimized settings based on benchmarking results
"""

# Local Executor Configuration
DEFAULT_LOCAL_MODEL = "tinyllama"
LOCAL_MODEL_TIMEOUT = 30  # seconds (tinyllama averages 8s)
LOCAL_MODEL_MAX_RETRIES = 3

# Model Selection Strategy
# Based on benchmark results (May 3, 2026):
# - tinyllama: 8.47s (optimal for 7.5GB RAM)
# - qwen2.5-coder:3b: 97.98s (too slow)
# - Larger models: timeout on <8GB RAM

# Fallback chain (in order of preference)
FALLBACK_MODELS = [
    "tinyllama",  # Primary - tested and optimal
]

# Minimum hardware requirements
MIN_RAM_GB = 2.0  # For tinyllama
RECOMMENDED_RAM_GB = 8.0  # For future model upgrades
