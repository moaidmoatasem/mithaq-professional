"""Unit tests for the device-aware model selector."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_no_gpu():
    with (
        patch("psutil.virtual_memory") as mock_mem,
        patch("subprocess.run") as mock_run,
    ):
        mock_mem.return_value.total = 8e9
        mock_run.side_effect = FileNotFoundError("nvidia-smi not found")
        yield


@pytest.fixture
def mock_high_end_gpu():
    with (
        patch("psutil.virtual_memory") as mock_mem,
        patch("subprocess.run") as mock_run,
    ):
        mock_mem.return_value.total = 32e9
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "NVIDIA RTX 4090, 24576\n"
        mock_run.return_value = mock_proc
        yield


def test_detect_hardware_no_gpu(mock_no_gpu):
    from cherenkov.ai.model_selector import detect_hardware

    hw = detect_hardware()
    assert hw["has_gpu"] is False
    assert hw["vram_gb"] == 0.0
    assert hw["ram_gb"] == 8.0
    assert hw["tier"] == "low"


def test_detect_hardware_high_end_gpu(mock_high_end_gpu):
    from cherenkov.ai.model_selector import detect_hardware

    hw = detect_hardware()
    assert hw["has_gpu"] is True
    assert hw["vram_gb"] == 24.0
    assert hw["gpu_name"] == "NVIDIA RTX 4090"
    assert hw["tier"] == "high"


def test_recommend_models_low_tier(mock_no_gpu):
    from cherenkov.ai.model_selector import recommend_models

    hw = {
        "ram_gb": 4.0,
        "vram_gb": 0.0,
        "has_gpu": False,
        "tier": "low",
        "gpu_name": "None",
        "cpu_cores": 2,
        "platform": "Linux",
    }
    recs = recommend_models(hw)
    assert recs["tier"] == "low"
    assert recs["effective_memory_gb"] == 1.6
    assert "embed" in recs["selected"]
    assert "advice" in recs
    assert "Limited memory" in recs["advice"]


def test_recommend_models_medium_tier():
    from cherenkov.ai.model_selector import recommend_models

    hw = {
        "ram_gb": 16.0,
        "vram_gb": 6.0,
        "has_gpu": True,
        "tier": "medium",
        "gpu_name": "RTX 3060",
        "cpu_cores": 8,
        "platform": "Linux",
    }
    recs = recommend_models(hw)
    assert recs["tier"] == "medium"
    assert recs["effective_memory_gb"] == 6.0
    # 6GB VRAM * 0.8 = 4.8GB budget → 7B code model (5GB) doesn't fit
    assert "code" not in recs["selected"]
    # Foundation-Sec-8B at 5.5GB doesn't fit either, but deepseek-r1:8b at 5.5GB also doesn't
    assert "architect" not in recs["selected"]


def test_recommend_models_high_tier():
    from cherenkov.ai.model_selector import recommend_models

    hw = {
        "ram_gb": 64.0,
        "vram_gb": 24.0,
        "has_gpu": True,
        "tier": "high",
        "gpu_name": "RTX 4090",
        "cpu_cores": 16,
        "platform": "Linux",
    }
    recs = recommend_models(hw)
    assert recs["tier"] == "high"
    assert "code" in recs["selected"]
    assert "architect" in recs["selected"]
    # Foundation-Sec preferred over deepseek-r1:14b when both fit
    assert "Foundation-Sec" in recs["selected"]["architect"]["model"]
    assert len(recs["pull_commands"]) == 4


def test_recommend_models_fallback_no_gpu():
    from cherenkov.ai.model_selector import recommend_models

    hw = {
        "ram_gb": 32.0,
        "vram_gb": 0.0,
        "has_gpu": False,
        "tier": "medium",
        "gpu_name": "None",
        "cpu_cores": 8,
        "platform": "Linux",
    }
    recs = recommend_models(hw)
    assert recs["tier"] == "medium"
    assert recs["effective_memory_gb"] == 12.8
    assert "architect" in recs["selected"]


def test_generate_litellm_config():
    from cherenkov.ai.model_selector import generate_litellm_config

    recs = {
        "selected": {
            "embed": {
                "name": "embed",
                "model": "nomic-embed-text",
                "size_gb": 0.3,
                "description": "test",
            },
            "code": {
                "name": "code-smart",
                "model": "qwen2.5-coder:7b",
                "size_gb": 5.0,
                "description": "test",
            },
            "architect": {
                "name": "architect",
                "model": "deepseek-r1:8b",
                "size_gb": 5.5,
                "description": "test",
            },
        }
    }
    config = generate_litellm_config(recs)
    assert "model_list:" in config
    assert "ollama/nomic-embed-text" in config
    assert "ollama/qwen2.5-coder:7b" in config
    assert "ollama/deepseek-r1:8b" in config
    assert "cloud-fallback" in config
    assert "groq/llama-3.1-8b-instant" in config
    assert "master_key: sk-local-dev" in config


def test_generate_litellm_config_empty():
    from cherenkov.ai.model_selector import generate_litellm_config

    config = generate_litellm_config({"selected": {}})
    assert config.startswith("model_list:")
    assert "cloud-fallback" in config


def test_model_catalog_has_known_entries():
    from cherenkov.ai.model_selector import MODEL_CATALOG

    roles = {m["role"] for m in MODEL_CATALOG}
    assert "embed" in roles
    assert "autocomplete" in roles
    assert "code" in roles
    assert "architect" in roles
    assert "offensive" in roles
    names = {m["name"] for m in MODEL_CATALOG}
    assert "embed" in names
    assert "code-fast" in names
    assert "code-smart" in names
    assert "architect" in names
    assert "red-team" in names
