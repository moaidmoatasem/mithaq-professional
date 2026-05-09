import pytest
from cherenkov.agents.local.code_analyzer import CodeAnalyzer
from cherenkov.agents.local.ollama_client import OllamaClient


@pytest.mark.integration
def test_ollama_availability():
    client = OllamaClient()
    if not client.is_available():
        pytest.skip("Ollama is not running")


@pytest.mark.integration
def test_code_analyzer():
    vulnerable_code = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
"""
    analyzer = CodeAnalyzer()
    findings = analyzer.analyze_code(vulnerable_code)
    assert isinstance(findings, list)
