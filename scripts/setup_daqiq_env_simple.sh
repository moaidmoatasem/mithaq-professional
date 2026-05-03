#!/bin/bash
set -e

echo "🚀 DAQIQ Simple Setup (Python 3.12)"
echo "===================================="

# Detect RAM
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
echo "📊 Detected RAM: ${RAM_GB}GB"

if [[ $RAM_GB -lt 8 ]]; then
    echo "⚠️  WARNING: Low RAM! Increase WSL2 to 12GB for best results"
    echo ""
fi

# Install Python 3.12
echo "📦 Installing Python 3.12..."
sudo apt-get update -qq
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev \
    build-essential curl wget nmap git

# Create venv
echo "🐍 Creating virtual environment..."
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install core dependencies
echo "📥 Installing Python packages..."
if [[ -f requirements.txt ]]; then
    pip install -r requirements.txt --quiet
else
    pip install pydantic pytest pytest-cov ruff bandit requests --quiet
fi

# Install Ollama
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama
if ! pgrep ollama > /dev/null; then
    mkdir -p logs
    nohup ollama serve > logs/ollama.log 2>&1 &
    sleep 5
fi

# Pull model based on RAM
if [[ $RAM_GB -ge 12 ]]; then
    MODEL="llama3.2:3b"
elif [[ $RAM_GB -ge 6 ]]; then
    MODEL="llama3.2:1b"
else
    MODEL="tinyllama"
    echo "⚠️  Using tinyllama (560MB) due to low RAM"
fi

echo "📥 Pulling model: $MODEL..."
ollama pull $MODEL

# Verification
echo ""
echo "✅ Setup Complete!"
echo "==================="
echo "Python: $(python --version)"
echo "Ollama Model: $MODEL"
echo ""
echo "🚀 Next: pytest --cov=daqiq"
echo ""

# Test Ollama
echo "🧪 Testing Ollama..."
ollama run $MODEL "Say 'DAQIQ is ready!' in one sentence" --verbose=false

echo ""
echo "✅ All systems operational!"
