from mithaq.agents.local.ollama_client import OllamaClient
from mithaq.agents.local.code_analyzer import CodeAnalyzer

print("="*70)
print("🧪 TESTING LOCAL OLLAMA AGENT")
print("="*70)

# Test 1: Check Ollama availability
print("\n📡 Test 1: Checking Ollama availability...")
client = OllamaClient()

if client.is_available():
    print("   ✅ Ollama is running")
    models = client.list_models()
    print(f"   📋 Available models: {', '.join(models)}")
else:
    print("   ❌ Ollama is not running!")
    print("   Start it with: ollama serve")
    exit(1)

# Test 2: Simple code analysis
print("\n🔍 Test 2: Analyzing vulnerable code snippet...")

vulnerable_code = '''
import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    return cursor.fetchone()

# Hardcoded credentials
API_KEY = "sk_live_1234567890abcdefghij"
DB_PASSWORD = "admin123"
'''

analyzer = CodeAnalyzer()
result = analyzer.quick_scan(vulnerable_code, language="python")

print("\n📋 Security Findings:")
print("="*70)
print(result)
print("="*70)

print("\n✅ Local agent test complete!")

