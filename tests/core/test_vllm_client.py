import pytest
from cherenkov.core.vllm_client import UnifiedLLMClient


def test_fallback_triage_benign():
    client = UnifiedLLMClient()

    # Benign texts that contain substrings but are not actual vulnerabilities
    benign_texts = [
        "The mysql library was updated.",
        "We are using a new selector for the UI.",
        "Systemic issues in the evalution process were noted.",
        "I need a password_generator feature.",
        "The new keyboard is nice.",
        "The secretary handles the mail.",
        "The evaluate_performance function is fast.",
        "We updated the sql_alchemy dependency.",
    ]

    for text in benign_texts:
        result = client._fallback_triage(text)
        assert "Critical" not in result, f"Benign text '{text}' flagged as Critical"
        assert "High" not in result, f"Benign text '{text}' flagged as High"


def test_fallback_triage_malicious():
    client = UnifiedLLMClient()

    # Texts that should trigger findings
    malicious_texts = [
        "SELECT * FROM users WHERE id = '1' OR '1'='1';",
        "os.system('rm -rf /');",
        'eval(\'__import__("os").system("ls")\')',
        "password = 'admin'",
    ]

    for text in malicious_texts:
        result = client._fallback_triage(text)
        assert "Finding" in result, f"Malicious text '{text}' not flagged"
