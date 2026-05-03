# Hardware Requirements

## Minimum Requirements (Tested - May 2026)

### For Local Executor (tinyllama)
- **RAM**: 2GB minimum, 8GB recommended
- **CPU**: 4 cores
- **Disk**: 10GB (models + workspace)
- **OS**: Linux x86_64 (WSL2, Ubuntu, etc.)

### Tested Configurations

#### Configuration 1: Budget (7.5GB RAM)
- **Model**: tinyllama (637MB)
- **Performance**: 8.47s per inference
- **Throughput**: ~100 scans/hour
- **Status**: ✅ Optimal

## Benchmark Results (May 3, 2026)

Tested on WSL2 (7.5GB RAM, 6 cores):

| Model | Size | Inference Time | Result |
|-------|------|----------------|--------|
| tinyllama | 637MB | 8.47s | ✅ OPTIMAL |
| qwen2.5-coder:3b | 1.9GB | 97.98s | ⚠️ Too slow |
| qwen2.5-coder:7b | 4.7GB | >120s | ❌ Timeout |
| deepseek-coder-v2:16b | 8.9GB | >120s | ❌ Timeout |

**Conclusion**: For systems with <8GB RAM, use `tinyllama`.

## Cloud Architect (Groq/Gemini)
- No local hardware requirements
- Requires API keys
- Internet connection required
