#!/bin/bash
# ============================================
# DAQIQ Environment Setup Script
# Hardware-Agnostic | Auto-Detection | Production-Ready
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p logs
LOG_FILE="logs/setup_daqiq_env.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================
# STEP 1: DETECT PLATFORM
# ============================================
log "🔍 Detecting platform..."

OS_TYPE=$(uname -s)
ARCH=$(uname -m)
RAM_GB=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || sysctl -n hw.memsize 2>/dev/null | awk '{print int($1/1024/1024/1024)}')

log "Platform: $OS_TYPE"
log "Architecture: $ARCH"
log "Total RAM: ${RAM_GB}GB"

# ⚠️ WARNING: Low RAM detected
if [[ $RAM_GB -lt 8 ]]; then
    warn "⚠️ WARNING: Only ${RAM_GB}GB RAM detected!"
    warn "   DAQIQ works best with 8GB+. Performance may be limited."
    warn "   Consider increasing WSL2 memory allocation in .wslconfig"
fi

# Determine package manager
if [[ "$OS_TYPE" == "Darwin" ]]; then
    PKG_MGR="brew"
    PYTHON_CMD="python3.11"
elif [[ -f /etc/debian_version ]]; then
    PKG_MGR="apt"
    PYTHON_CMD="python3.11"
else
    error "Unsupported operating system: $OS_TYPE"
fi

log "Package manager: $PKG_MGR"

# ============================================
# STEP 2: CHECK PREREQUISITES
# ============================================
log "📦 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    warn "Docker not found. Some features may not work."
else
    log "✅ Docker found: $(docker --version)"
fi

# Check git
if ! command -v git &> /dev/null; then
    error "Git is required but not found. Please install git first."
else
    log "✅ Git found: $(git --version)"
fi

# ============================================
# STEP 3: ADD DEADSNAKES PPA (for Python 3.11 on Ubuntu/Debian)
# ============================================
if [[ "$PKG_MGR" == "apt" ]]; then
    log "📥 Adding deadsnakes PPA for Python 3.11..."
    
    # Check if already added
    if ! grep -q "deadsnakes" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
        sudo add-apt-repository ppa:deadsnakes/ppa -y 2>&1 | tee -a "$LOG_FILE"
        log "✅ Deadsnakes PPA added"
    else
        log "✅ Deadsnakes PPA already added"
    fi
fi

# ============================================
# STEP 4: INSTALL SYSTEM PACKAGES
# ============================================
log "📥 Installing system packages..."

if [[ "$PKG_MGR" == "apt" ]]; then
    log "Updating package lists..."
    sudo apt-get update -qq
    
    log "Installing Python 3.11 and dependencies..."
    sudo apt-get install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        build-essential \
        curl \
        wget \
        nmap \
        git \
        software-properties-common
    
    log "✅ System packages installed (apt)"

elif [[ "$PKG_MGR" == "brew" ]]; then
    log "Installing Python 3.11 and dependencies..."
    brew install python@3.11 curl wget nmap git 2>&1 | tee -a "$LOG_FILE"
    
    log "✅ System packages installed (brew)"
fi

# Verify Python 3.11
if command -v python3.11 &> /dev/null; then
    log "✅ Python 3.11 installed: $(python3.11 --version)"
else
    error "Python 3.11 installation failed!"
fi

# ============================================
# STEP 5: SETUP PYTHON VIRTUAL ENVIRONMENT
# ============================================
log "🐍 Setting up Python virtual environment..."

if [[ -d ".venv" ]]; then
    warn "Virtual environment already exists. Recreating..."
    rm -rf .venv
fi

log "Creating .venv with Python 3.11..."
python3.11 -m venv .venv
log "✅ Virtual environment created"

# Activate venv
source .venv/bin/activate

# Verify Python version in venv
log "Python in venv: $(python --version)"

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
if [[ -f "requirements.txt" ]]; then
    log "Installing Python packages from requirements.txt..."
    pip install -r requirements.txt --quiet
    log "✅ Python dependencies installed"
else
    warn "requirements.txt not found. Installing minimal dependencies..."
    pip install pydantic pytest pytest-cov ruff bandit --quiet
fi

# ============================================
# STEP 6: INSTALL SECURITY TOOLS
# ============================================
log "🔒 Installing security tools..."

# Install Ruff
if ! command -v ruff &> /dev/null; then
    log "Installing Ruff..."
    pip install ruff --quiet
    log "✅ Ruff installed"
else
    log "✅ Ruff already installed: $(ruff --version)"
fi

# Install Bandit
if ! pip show bandit &> /dev/null; then
    log "Installing Bandit..."
    pip install bandit --quiet
    log "✅ Bandit installed"
else
    log "✅ Bandit already installed"
fi

# Frida (Python package)
if ! pip show frida &> /dev/null; then
    log "Installing Frida..."
    pip install frida frida-tools --quiet
    log "✅ Frida installed"
else
    log "✅ Frida already installed"
fi

# Trivy (optional - skip if fails)
if [[ "$OS_TYPE" == "Linux" ]] && ! command -v trivy &> /dev/null; then
    log "Installing Trivy..."
    (
        wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
        echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
        sudo apt-get update -qq && sudo apt-get install -y trivy
    ) 2>&1 | tee -a "$LOG_FILE" || warn "Trivy installation failed (non-critical)"
    
    if command -v trivy &> /dev/null; then
        log "✅ Trivy installed"
    fi
fi

# Syft (optional - skip if fails)
if ! command -v syft &> /dev/null; then
    log "Installing Syft..."
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b ~/.local/bin 2>&1 | tee -a "$LOG_FILE" || warn "Syft installation failed (non-critical)"
    
    if command -v syft &> /dev/null; then
        log "✅ Syft installed"
    fi
fi

# ============================================
# STEP 7: INSTALL OLLAMA + MODELS
# ============================================
log "🤖 Installing Ollama..."

if ! command -v ollama &> /dev/null; then
    log "Downloading Ollama installer..."
    curl -fsSL https://ollama.com/install.sh | sh
    log "✅ Ollama installed"
else
    log "✅ Ollama already installed: $(ollama --version)"
fi

# Start Ollama service (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    log "Starting Ollama service..."
    nohup ollama serve > logs/ollama.log 2>&1 &
    sleep 5
fi

# Pull model based on available RAM
log "📥 Pulling Ollama model (this may take a few minutes)..."

if [[ $RAM_GB -ge 12 ]]; then
    MODEL="llama3.2:3b"
    log "RAM ≥12GB detected. Pulling $MODEL..."
elif [[ $RAM_GB -ge 6 ]]; then
    MODEL="llama3.2:1b"
    log "RAM 6-12GB detected. Pulling smaller model: $MODEL..."
else
    warn "⚠️ RAM <6GB detected. Using tinyllama (560MB model)..."
    MODEL="tinyllama"
fi

ollama pull $MODEL 2>&1 | tee -a "$LOG_FILE"
log "✅ Model $MODEL pulled successfully"

# ============================================
# STEP 8: VERIFY INSTALLATION
# ============================================
log "✅ Verifying installation..."

VERIFICATION_REPORT="logs/installation_verification.txt"
{
    echo "DAQIQ Environment Verification Report"
    echo "======================================"
    echo "Date: $(date)"
    echo ""
    echo "System Information:"
    echo "  OS: $OS_TYPE"
    echo "  Arch: $ARCH"
    echo "  RAM: ${RAM_GB}GB"
    echo ""
    echo "Python:"
    python --version
    pip --version
    echo ""
    echo "Installed Tools:"
    echo "  Ruff: $(ruff --version 2>/dev/null || echo 'Not found')"
    echo "  Bandit: $(bandit --version 2>/dev/null || echo 'Not found')"
    echo "  Trivy: $(trivy --version 2>/dev/null || echo 'Not found')"
    echo "  Syft: $(syft --version 2>/dev/null || echo 'Not found')"
    echo "  Nmap: $(nmap --version 2>/dev/null | head -1 || echo 'Not found')"
    echo "  Frida: $(frida --version 2>/dev/null || echo 'Not found')"
    echo "  Ollama: $(ollama --version 2>/dev/null || echo 'Not found')"
    echo ""
    echo "Ollama Models:"
    ollama list 2>/dev/null || echo "Could not list models"
    echo ""
    echo "Python Packages:"
    pip list | grep -E "pydantic|pytest|ruff|bandit|frida"
} > "$VERIFICATION_REPORT"

cat "$VERIFICATION_REPORT" | tee -a "$LOG_FILE"

# ============================================
# STEP 9: INCREASE WSL2 MEMORY (if needed)
# ============================================
if [[ $RAM_GB -lt 8 ]] && [[ -f /proc/version ]] && grep -qi microsoft /proc/version; then
    warn ""
    warn "⚠️ WSL2 DETECTED WITH LOW RAM (${RAM_GB}GB)"
    warn "   To improve performance, increase WSL2 memory allocation:"
    warn ""
    warn "   1. Exit WSL2 completely (close all WSL terminals)"
    warn "   2. In Windows PowerShell (as Admin), run:"
    warn "      wsl --shutdown"
    warn "   3. Create/edit C:\\Users\\YourUsername\\.wslconfig:"
    warn ""
    warn "      [wsl2]"
    warn "      memory=12GB"
    warn "      processors=6"
    warn ""
    warn "   4. Restart WSL2"
    warn ""
fi

# ============================================
# STEP 10: SUMMARY
# ============================================
echo ""
echo "═══════════════════════════════════════════════════════"
log "✅ DAQIQ ENVIRONMENT SETUP COMPLETE!"
echo "═══════════════════════════════════════════════════════"
echo ""
log "📊 Summary:"
log "  Platform: $OS_TYPE ($ARCH)"
log "  RAM: ${RAM_GB}GB"
log "  Python: $(python --version)"
log "  Ollama Model: $MODEL"
echo ""
log "📝 Logs saved to:"
log "  - Setup log: $LOG_FILE"
log "  - Verification report: $VERIFICATION_REPORT"
echo ""
log "🚀 Next steps:"
log "  1. Virtual environment is ACTIVE (.venv)"
log "  2. Run tests: pytest --cov=daqiq"
log "  3. Start Issue #17 (Benchmarking)"
echo ""
log "📚 Documentation: docs/roadmap/DAQIQ_NEXUS_v4.md"
echo "═══════════════════════════════════════════════════════"
