"""Device-aware LLM model selector.

Detects local hardware (RAM, VRAM, GPU) and recommends appropriate
Ollama models per role (embed, autocomplete, code, architect).
Generates LiteLLM proxy configuration for the recommended models.
"""

import logging
import platform
import subprocess  # nosec B404

import psutil

logger = logging.getLogger(__name__)

MODEL_CATALOG = [
    {
        "name": "embed",
        "ollama_tag": "nomic-embed-text",
        "size_gb": 0.3,
        "role": "embed",
        "quality": "high",
        "description": "Best local embeddings. 768-dim. 8K context.",
        "recommended_for": "all",
    },
    {
        "name": "code-fast",
        "ollama_tag": "qwen2.5-coder:1.5b",
        "size_gb": 1.0,
        "role": "autocomplete",
        "quality": "fast",
        "description": "Instant tab completion. Low quality but very fast.",
        "recommended_for": "low",
    },
    {
        "name": "code-fast",
        "ollama_tag": "qwen2.5-coder:3b",
        "size_gb": 2.0,
        "role": "autocomplete",
        "quality": "medium",
        "description": "Good autocomplete. Balanced speed/quality.",
        "recommended_for": "medium",
    },
    {
        "name": "code-smart",
        "ollama_tag": "qwen2.5-coder:7b",
        "size_gb": 5.0,
        "role": "code",
        "quality": "high",
        "description": "Best coding model under 8GB. Primary choice.",
        "recommended_for": "medium",
    },
    {
        "name": "code-smart",
        "ollama_tag": "qwen2.5-coder:14b",
        "size_gb": 9.0,
        "role": "code",
        "quality": "high",
        "description": "Higher quality code. Needs 10GB+ VRAM.",
        "recommended_for": "high",
    },
    {
        "name": "architect",
        "ollama_tag": "deepseek-r1:8b",
        "size_gb": 5.5,
        "role": "architect",
        "quality": "high",
        "description": "Chain-of-thought reasoning. Good for planning.",
        "recommended_for": "medium",
    },
    {
        "name": "architect",
        "ollama_tag": "hf.co/FoundationAI/Foundation-Sec-8B-Reasoning-GGUF",
        "size_gb": 5.5,
        "role": "architect",
        "quality": "high",
        "description": "Security-specialized reasoning. Best for CHERENKOV.",
        "recommended_for": "medium",
    },
    {
        "name": "architect",
        "ollama_tag": "deepseek-r1:14b",
        "size_gb": 9.5,
        "role": "architect",
        "quality": "very-high",
        "description": "Best local reasoning. Needs 10GB+ VRAM.",
        "recommended_for": "high",
    },
    {
        "name": "red-team",
        "ollama_tag": "hf.co/WhiteRabbitNeo/WhiteRabbitNeo-V2-7B-GGUF",
        "size_gb": 5.0,
        "role": "offensive",
        "quality": "high",
        "description": "Security-specialized. No refusal blocks.",
        "recommended_for": "medium",
    },
]


def detect_hardware() -> dict:
    hw = {
        "ram_gb": round(psutil.virtual_memory().total / 1e9, 1),
        "cpu_cores": psutil.cpu_count(logical=False) or 0,
        "platform": platform.system(),
        "vram_gb": 0.0,
        "has_gpu": False,
        "gpu_name": "None",
    }
    try:
        import shutil

        nvidia_smi = shutil.which("nvidia-smi")
        if nvidia_smi:
            result = subprocess.run(  # nosec B603
                [nvidia_smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        if result.returncode == 0:
            line = result.stdout.strip().split("\n")[0]
            parts = line.split(", ")
            if len(parts) >= 2:
                hw["gpu_name"] = parts[0].strip()
                hw["vram_gb"] = round(float(parts[1]) / 1024, 1)
                hw["has_gpu"] = True
    except Exception as e:
        logger.debug("Failed to detect GPU: %s", e)

    effective = hw["vram_gb"] + (hw["ram_gb"] * 0.4) if hw["has_gpu"] else hw["ram_gb"] * 0.4
    if effective >= 10:
        hw["tier"] = "high"
    elif effective >= 5:
        hw["tier"] = "medium"
    else:
        hw["tier"] = "low"
    return hw


def recommend_models(hw: dict = None) -> dict:
    if hw is None:
        hw = detect_hardware()
    effective = hw["vram_gb"] + (hw["ram_gb"] * 0.4) if hw["has_gpu"] else hw["ram_gb"] * 0.4
    tier = hw["tier"]
    recommendations = {
        "hardware": hw,
        "tier": tier,
        "effective_memory_gb": effective,
        "selected": {},
        "alternatives": [],
        "pull_commands": [],
    }
    roles = ["embed", "autocomplete", "code", "architect"]
    for role in roles:
        if role == "architect":
            candidates = [
                m
                for m in MODEL_CATALOG
                if m["role"] == role
                and m["size_gb"] <= effective * 0.8
                and "Foundation-Sec" in m["ollama_tag"]
            ]
            if not candidates:
                candidates = [
                    m
                    for m in MODEL_CATALOG
                    if m["role"] == role and m["size_gb"] <= effective * 0.8
                ]
        else:
            candidates = [
                m for m in MODEL_CATALOG if m["role"] == role and m["size_gb"] <= effective * 0.8
            ]
        if candidates:
            best = max(candidates, key=lambda m: m["size_gb"])
            recommendations["selected"][role] = {
                "name": best["name"],
                "model": best["ollama_tag"],
                "size_gb": best["size_gb"],
                "description": best["description"],
            }
            recommendations["pull_commands"].append(f"ollama pull {best['ollama_tag']}")
    if tier == "low":
        recommendations["advice"] = (
            "Limited memory. Use 3B models only. Consider Groq free tier for architect tasks."
        )
    elif tier == "medium":
        recommendations["advice"] = (
            "Good balance. 7B models run well. Foundation-Sec-8B recommended for architect."
        )
    else:
        recommendations["advice"] = (
            "High-end hardware. 14B models available. Run architect + code model simultaneously."
        )
    return recommendations


def generate_litellm_config(recommendations: dict) -> str:
    selected = recommendations["selected"]
    lines = ["model_list:"]
    role_map = {
        "embed": "embed",
        "autocomplete": "code-fast",
        "code": "code-smart",
        "architect": "architect",
    }
    for role, alias in role_map.items():
        if role in selected:
            model = selected[role]["model"]
            lines.append(f"  - model_name: {alias}")
            lines.append("    litellm_params:")
            lines.append(f"      model: ollama/{model}")
            lines.append("      api_base: http://localhost:11434")
    lines += [
        "",
        "  # Free cloud fallback",
        "  - model_name: cloud-fallback",
        "    litellm_params:",
        "      model: groq/llama-3.1-8b-instant",
        "      api_key: os.environ/GROQ_API_KEY",
        "",
        "general_settings:",
        "  master_key: sk-local-dev",
        "  drop_params: true",
        "",
        "litellm_settings:",
        "  fallbacks:",
        "    - architect:",
        "        - cloud-fallback",
        "    - code-smart:",
        "        - cloud-fallback",
    ]
    return "\n".join(lines)
