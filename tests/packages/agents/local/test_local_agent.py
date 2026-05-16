from unittest.mock import patch

import pytest
from cherenkov.agents.local.code_analyzer import CodeAnalyzer
from cherenkov.agents.local.ollama_client import OllamaClient


@pytest.mark.integration
def test_ollama_availability():
    client = OllamaClient()
    if not client.is_available():
        pytest.skip("Ollama is not running")


@pytest.mark.integration
@patch("cherenkov.agents.local.ollama_client.OllamaClient.is_available", return_value=True)
@patch("cherenkov.agents.local.ollama_client.OllamaClient.analyze_code")
def test_code_analyzer(mock_make_request, mock_check):
    vulnerable_code = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
"""
    mock_make_request.return_value = {"findings": "Mock security findings"}
    analyzer = CodeAnalyzer()
    findings = analyzer.quick_scan(vulnerable_code)
    assert isinstance(findings, str)
