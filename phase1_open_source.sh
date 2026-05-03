#!/bin/bash
# ============================================
# DAQIQ PHASE 1: MIT LICENSE + OPEN SOURCE + CLEANUP
# Hardware-Agnostic | Production-Ready | May 2026
# ============================================

set -e  # Exit on error

echo "🚀 DAQIQ PHASE 1: OPEN SOURCE TRANSFORMATION"
echo "=============================================="
echo ""

cd ~/daqiq-dev-agents

# ============================================
# STEP 1: CLEANUP - REMOVE SCAN REPORTS FROM ROOT
# ============================================
echo "🧹 STEP 1: Cleaning up scan reports from repository root..."

# Create scan_reports directory if it doesn't exist
mkdir -p scan_reports

# Move all scan reports to dedicated directory
if ls scan_report_*.json 1> /dev/null 2>&1; then
    mv scan_report_*.json scan_reports/ 2>/dev/null || true
    echo "  ✅ Moved scan reports to scan_reports/"
fi

if ls unified_scan_*.json 1> /dev/null 2>&1; then
    mv unified_scan_*.json scan_reports/ 2>/dev/null || true
    echo "  ✅ Moved unified scans to scan_reports/"
fi

# Update .gitignore to prevent future commits
cat >> .gitignore << 'GITIGNORE_EOF'

# Scan reports and outputs
scan_report_*.json
unified_scan_*.json
scan_reports/
swarm_outputs/
GITIGNORE_EOF

echo "  ✅ Updated .gitignore to exclude scan reports"

# ============================================
# STEP 2: ADD MIT LICENSE
# ============================================
echo ""
echo "📄 STEP 2: Adding MIT License..."

cat > LICENSE << 'LICENSE_EOF'
MIT License

Copyright (c) 2026 Moaid EL-Moatasem Bellah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
LICENSE_EOF

echo "  ✅ MIT License created"

# ============================================
# STEP 3: CREATE COMPREHENSIVE ROADMAP
# ============================================
echo ""
echo "📋 STEP 3: Creating DAQIQ NEXUS v4 Roadmap..."

mkdir -p docs/roadmap

cat > docs/roadmap/DAQIQ_NEXUS_v4.md << 'ROADMAP_EOF'
# 🚀 DAQIQ NEXUS v4 - MASTER ROADMAP
**Autonomous AI-Driven Security Testing Platform with Dual-Brain Architecture**

*Last Updated: May 3, 2026 | License: MIT | Status: Phase 0 - Foundation*

---

## 📊 EXECUTIVE SUMMARY

DAQIQ is evolving from an autonomous scanner generator (DAQIQ Professional) into a full dual-brain security intelligence platform (DAQIQ NEXUS) with:

- **Cloud Architect Brain**: RAG-powered planning, compliance mapping, CVE intelligence
- **Local Executor Brain**: CPU-optimized LLM + Professional scanners (132+ modules)
- **Zero-Trust Bridge**: Sanitization, Daqiq Trace, Burhan proof-of-concept
- **Agentic Development**: Self-coding agents with approval gates

---

## 🏗️ THREE-LAYER ARCHITECTURE

### Layer 1: Execution (DONE - DAQIQ Professional)
- ✅ 132 autonomous security scanners (87% success rate)
- ✅ Docker production container (daqiq-prod)
- ✅ CI/CD workflows (GitHub Actions)
- ✅ XSS, CSRF, SQLi, path traversal, XXE, file upload, API scanners
- ✅ 28 autonomous agents, 900+ lines generated
- ✅ 100% test coverage on core components

### Layer 2: Intelligence & Orchestration (IN PROGRESS - NEXUS Core)
- 🔄 Dual-brain architecture (Architect + Executor)
- 🔄 Sanitization Bridge (fail-closed, 91.78% coverage)
- 🔄 Daqiq Trace (cognitive forensics)
- 🔄 RAG knowledge base (CVEs, compliance, OWASP)
- 🔄 Burhan proof system

### Layer 3: Experience & Governance (PLANNED - NEXUS Platform)
- 📅 PyQt Desktop forensic UI
- 📅 Policy engine (Pydantic Gates)
- 📅 SBOM + AI-BOM tracking
- 📅 Cairo pilot deployment
- 📅 Open-core commercialization

---

## 💻 HARDWARE REQUIREMENTS (Hardware-Agnostic Design)

### Minimum Recommended Configuration
- **CPU**: Modern multi-core processor (Intel/AMD/ARM)
  - 6+ cores recommended for parallel execution
  - 8+ cores optimal for concurrent MiniGPT swarms
- **RAM**: 12GB+ available for local execution
  - Scales with number of concurrent agents
  - WSL2/Linux: Configure ~12GB for execution layer
- **Storage**: 20GB+ for models and knowledge base
- **OS**: Linux, WSL2, or macOS (Docker-compatible)

### Performance Tuning Guidelines

**Model Quantization**:
- **8-bit quantization**: 99%+ accuracy retention, ~4GB RAM per 3B model
- **4-bit quantization**: 98.9% accuracy retention, ~2.5GB RAM per 3B model
- **Recommendation**: Start with 4-bit (Q4_K_M) for maximum concurrency

**CPU Core Allocation**:
- Single agent: 4-6 cores optimal
- Parallel swarm (3-4 agents): 12+ cores recommended
- Hyperthreading: Enable for I/O-bound tasks

**Memory Strategy**:
\`\`\`yaml
# Example: 16GB total RAM system
System Reserve:     4GB
WSL2/Container:    12GB
  ├─ Ollama (3x3B @ 4-bit): 7.5GB
  ├─ Python runtime:        2GB
  ├─ Tools (Frida/Nmap):    1.5GB
  └─ Buffers:               1GB
\`\`\`

### Supported Platforms
- **x86_64**: Intel/AMD workstations, servers
- **ARM64**: Apple Silicon (M1/M2/M3), ARM servers
- **Cloud**: AWS EC2, GCP Compute, Azure VMs
- **Edge**: High-performance laptops, workstations

**Adaptive Configuration**:
\`\`\`python
# Auto-detect and configure based on available resources
import psutil

def configure_executor():
    cores = psutil.cpu_count(logical=False)
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    if ram_gb >= 16 and cores >= 8:
        return "multi_agent"  # 3-4 concurrent MiniGPTs
    elif ram_gb >= 12 and cores >= 6:
        return "dual_agent"   # 2 concurrent MiniGPTs
    else:
        return "single_agent" # 1 MiniGPT, sequential
\`\`\`

---

## 📅 DETAILED ROADMAP

### NOW (0-3 Months) - Phase 0-1: Foundation

See full roadmap in repository for complete details.

---

## 🚀 IMMEDIATE NEXT STEPS (This Week)

1. ✅ Add MIT License
2. ✅ Create DAQIQ NEXUS v4 roadmap
3. ✅ Clean up scan reports from repository
4. [ ] Create GitHub Project "DAQIQ NEXUS - Phase 0-1"
5. [ ] Create 10 foundational issues
6. [ ] Implement \`setup_daqiq_env.sh\`

---

*Built with ❤️ for secure AI-powered security testing*  
*Hardware: Agnostic (x86_64, ARM64, Cloud)*
ROADMAP_EOF

echo "  ✅ Roadmap created: docs/roadmap/DAQIQ_NEXUS_v4.md"

# ============================================
# STEP 4: CREATE ARCHITECTURE OVERVIEW
# ============================================
echo ""
echo "🏗️ STEP 4: Creating Architecture Overview..."

mkdir -p docs/architecture

cat > docs/architecture/overview.md << 'ARCH_EOF'
# 🏗️ DAQIQ NEXUS - ARCHITECTURE OVERVIEW

## Core Components

### 1. Architect Agent (Cloud Brain)
- High-level planning, compliance mapping
- Technology: Groq/Gemini + RAG

### 2. Sanitization Bridge ✅
- **Current Coverage**: 91.78%
- Fail-closed redaction

### 3. Local Executor (Stateless MiniGPT)
- On-premises tool orchestration
- Hardware-agnostic (x86_64/ARM64/Cloud)

---

*Last Updated: May 3, 2026*
ARCH_EOF

echo "  ✅ Architecture overview created"

# ============================================
# STEP 5: UPDATE README
# ============================================
echo ""
echo "📝 STEP 5: Updating README with roadmap links..."

# Add roadmap section after existing content (append only if not exists)
if ! grep -q "DAQIQ NEXUS v4 Roadmap" README.md; then
cat >> README.md << 'README_APPEND'

---

## 📚 Documentation & Roadmap

- **[DAQIQ NEXUS v4 Roadmap](./docs/roadmap/DAQIQ_NEXUS_v4.md)** - Strategic plan, Phases 0-6
- **[Architecture Overview](./docs/architecture/overview.md)** - Dual-brain system design

---

## 📜 License

**MIT License** - see [LICENSE](./LICENSE) for details.

Copyright (c) 2026 Moaid EL-Moatasem Bellah

---

**Built with ❤️ for secure AI-powered security testing**  
*Hardware-Agnostic | Open Source | Zero-Trust by Design*
README_APPEND
fi

echo "  ✅ README updated"

# ============================================
# STEP 6: CREATE CONTRIBUTING GUIDE
# ============================================
echo ""
echo "🤝 STEP 6: Creating CONTRIBUTING.md..."

cat > CONTRIBUTING.md << 'CONTRIB_EOF'
# Contributing to DAQIQ

Thank you for your interest in contributing to DAQIQ! 🚀

## Development Workflow

### Creating a Feature

\`\`\`bash
git checkout -b feature/your-feature-name
pytest --cov=daqiq
git commit -m "feat: Add your feature"
\`\`\`

## Code Quality Standards

- Maintain ≥80% coverage for new code
- Follow zero-trust principles
- Use Ruff for formatting

Thank you for contributing! 🙏
CONTRIB_EOF

echo "  ✅ CONTRIBUTING.md created"

# ============================================
# STEP 7: GIT COMMIT & PUSH
# ============================================
echo ""
echo "📦 STEP 7: Committing all changes..."

# Stage all changes
git add LICENSE docs/ README.md CONTRIBUTING.md .gitignore 2>/dev/null || true

# Remove scan reports from git tracking
git rm --cached scan_report_*.json 2>/dev/null || true
git rm --cached unified_scan_*.json 2>/dev/null || true

# Commit
git commit -m "feat: Open source with MIT License + DAQIQ NEXUS v4 roadmap

✨ Features:
- MIT License for open source
- Hardware-agnostic roadmap
- Architecture documentation
- Contributing guidelines

🧹 Cleanup:
- Move scan reports to scan_reports/
- Update .gitignore

Status: Phase 0 - Foundation 🚀" || echo "Nothing to commit or commit failed"

# Push
git push origin main || echo "Push failed - check your git configuration"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ PHASE 1 COMPLETE!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "🚀 Reply '1' for 10 GitHub Issues!"
echo ""
