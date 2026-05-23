# CHERENKOV Local Agents Handbook

> **Environment:** WSL2 (Ubuntu 24.04) · Ollama on localhost:11434 · $0 / zero internet

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     3-Layer Agent Stack                     │
├──────────────┬──────────────────────┬───────────────────────┤
│  Layer 1     │  Layer 2             │  Layer 3              │
│  Aider       │  dev_crew CLI        │  SwarmOrchestrator    │
│  (interactive│  (focused sprint)    │  (perpetual build)    │
│   coding)    │                      │                       │
├──────────────┼──────────────────────┼───────────────────────┤
│  You drive   │  You specify focus   │  Fully autonomous     │
│  Model:      │  Architect + Dev     │  Reads cwe_queue.yaml │
│  qwen2.5-    │  + ValidationGate    │  Self-patches 3x      │
│  coder:7b    │  loop (3 retries)    │  before giving up     │
└──────────────┴──────────────────────┴───────────────────────┘
                        │
            ┌───────────┴───────────┐
            │     Ollama Backend    │
            │  llama3.2:3b          │  ← Architect (PMO/spec)
            │  qwen2.5-coder:7b     │  ← Developer + Aider
            │  nomic-embed-text     │  ← Embeddings (Qdrant)
            └───────────────────────┘
```

---

## Prerequisites

### 1. Verify Ollama is running (WSL)

```bash
# From WSL terminal:
curl -s http://localhost:11434/api/tags | python3 -m json.tool | grep name

# Expected output:
# "name": "qwen2.5-coder:7b"
# "name": "llama3.2:3b"
# "name": "nomic-embed-text:latest"
```

If Ollama is not running:
```bash
ollama serve &         # start in background
# or
sudo systemctl start ollama   # if installed as service
```

### 2. Verify project dependencies (WSL)

```bash
cd /home/moaid/cherenkov-professional

# Check dev_crew imports
python3 -c "
import sys; sys.path.insert(0, 'packages')
from cherenkov.dev_crew.swarm_orchestrator import SwarmOrchestrator, AutonomousSprint
from cherenkov.dev_crew.session_manager import get_ssot_context
print('OK')
"

# Check aider
aider --version
```

---

## Layer 1 — Aider (Interactive Coding)

Aider is your pair-programmer. You give it files and a task in natural language; it edits them and optionally commits.

### Start

```bash
cd /home/moaid/cherenkov-professional

# Using the pre-built task runner (recommended):
./scripts/aider-tasks.sh help       # show task menu
./scripts/aider-tasks.sh 2          # run Task 2: real health metrics
./scripts/aider-tasks.sh 3          # run Task 3: graduate scanners
./scripts/aider-tasks.sh 5          # run Task 5: DecisionHub test coverage
./scripts/aider-tasks.sh 6          # run Task 6: frontend HITL polish

# Or drive it directly:
aider packages/cherenkov/api/main.py
aider packages/cherenkov/api/main.py packages/cherenkov/core/circuit_breaker.py
```

### Inside an aider session

```
/help                  show all commands
/add <file>            add another file to the context
/drop <file>           remove a file
/diff                  show staged changes
/undo                  undo last commit
/run pytest tests/     run a command and show output
/clear                 clear conversation history
/exit                  quit
```

### Reconfigure

Config is in `.aider.conf.yml` (gitignored, local only):

```yaml
# .aider.conf.yml
model: ollama_chat/qwen2.5-coder:7b    # change model here
edit-format: diff                       # diff | whole | udiff
auto-commits: true                      # false to review before committing
```

**Swap model without restarting:**
```bash
aider --model ollama_chat/llama3.2:3b packages/cherenkov/api/main.py
```

**Add a new task to `aider-tasks.sh`:**
```bash
# In scripts/aider-tasks.sh, add:
run_task_7() {
  git checkout -b feat/your-branch 2>/dev/null || git checkout feat/your-branch
  aider \
    --message "Your detailed task spec here..." \
    packages/path/to/file.py
  echo "✓ Task 7 complete."
}
# Add to the case dispatcher: 7) run_task_7 ;;
# Add to the help menu
```

---

## Layer 2 — dev_crew CLI (Autonomous Sprint)

The dev_crew CLI runs a focused 3-phase loop: Architect generates a spec → Developer writes code → ValidationGate runs ruff+pytest and feeds errors back, up to 3 times.

Use this when you want to generate or modify a **specific file** autonomously.

### Start

```bash
cd /home/moaid/cherenkov-professional

# Basic usage:
python3 -m cherenkov.dev_crew.cli \
  --focus "add rate limiting to /api/v1/scan endpoint" \
  --file "packages/cherenkov/api/main.py"

# Generate a new scanner:
python3 -m cherenkov.dev_crew.cli \
  --focus "HTTP header injection scanner for CWE-113" \
  --file "packages/cherenkov/scanners/header_injection_scanner.py"

# Add tests:
python3 -m cherenkov.dev_crew.cli \
  --focus "unit tests for DecisionHub approve/reject flows" \
  --file "tests/unit/test_decision_hub.py"
```

**Note:** Run from project root so `PYTHONPATH` resolves correctly:
```bash
PYTHONPATH=packages python3 -m cherenkov.dev_crew.cli --focus "..." --file "..."
# or
cd /home/moaid/cherenkov-professional && python3 -m cherenkov.dev_crew.cli ...
```

### What happens during a sprint

```
1. Architect (llama3.2:3b) reads CLAUDE.md (SSOT) + your --focus
   → outputs a JSON spec: {task_name, file_path, description, acceptance_criteria}

2. Developer (qwen2.5-coder:7b) receives the spec
   → writes Python code, returns it in a ```python``` fence

3. ValidationGate runs:
   a. ruff check  — lint (must pass)
   b. ruff format — auto-format
   c. pytest      — if a test file exists alongside the target

4. If failed: error output is fed back to Developer → retry (max 3x)
5. If passed: file written to disk, SSOT updated with completion log

CIRCUIT BREAKER: if all 3 iterations fail, it stops and reports.
Human fixes and re-runs.
```

### Reconfigure

**Change models** — edit `packages/cherenkov/dev_crew/architect_agent.py`:
```python
ARCHITECT_MODEL = "llama3.2:3b"   # swap to qwen:latest for faster PMO
```

Edit `packages/cherenkov/dev_crew/developer_agent.py`:
```python
CODER_MODEL = "qwen2.5-coder:7b"  # swap to qwen2.5-coder:3b for speed
```

**Change retry limit** — edit `packages/cherenkov/dev_crew/swarm_orchestrator.py`:
```python
MAX_RETRIES = 3   # increase for harder tasks, decrease for speed
```

**Override SSOT context** — the Architect always reads `CLAUDE.md`. Add context there:
```markdown
## Current Sprint Focus
- Priority: fix scan 500 errors
- Blocked: qdrant offline on cold start
```

---

## Layer 3 — SwarmOrchestrator (Perpetual Scanner Builder)

The swarm reads `manifests/cwe_queue.yaml` (gitignored, local) and autonomously generates security scanners for each CWE. Workers self-patch on failures up to 3 times. Passing scanners land in `candidates/generated_scanners/` for your review.

### Start

```bash
cd /home/moaid/cherenkov-professional

# Process one CWE and exit (good for testing):
python3 packages/cherenkov/dev_crew/swarm_orchestrator.py --once

# Run forever (batch of 3 CWEs at a time):
python3 packages/cherenkov/dev_crew/swarm_orchestrator.py

# Run in background (detached):
nohup python3 packages/cherenkov/dev_crew/swarm_orchestrator.py \
  >> logs/swarm.log 2>&1 &
echo "Swarm PID: $!"
```

### Manage the queue

`manifests/cwe_queue.yaml` controls what gets built:

```yaml
queue:
  - cwe_id: CWE-79
    description: "XSS via reflected query params"
    tier: 1
    status: pending      # pending | building | candidate | failed | validated

  - cwe_id: CWE-89
    description: "SQL injection in query params"
    tier: 1
    status: candidate    # done — waiting for your validation gate

  - cwe_id: CWE-611
    description: "XXE via XML file upload"
    tier: 2
    status: failed       # exhausted retries — needs human intervention
```

**Add a new CWE:**
```yaml
  - cwe_id: CWE-611
    description: "XML external entity injection via file upload endpoint"
    tier: 2
    status: pending
```

**Re-run a failed CWE:**
```yaml
    status: pending   # reset from failed → pending
```

**Check swarm progress:**
```bash
cat manifests/cwe_queue.yaml | grep -E "cwe_id|status"
ls -la candidates/generated_scanners/
```

### Review and graduate a candidate

```bash
# 1. Review the generated scanner
cat candidates/generated_scanners/xss_reflected_query.py

# 2. Run the validation gate manually
ruff check candidates/generated_scanners/xss_reflected_query.py
pytest tests/unit/ -k "xss" -v

# 3. If passing, move to packages (graduate)
mv candidates/generated_scanners/xss_reflected_query.py \
   packages/cherenkov/scanners/xss_reflected_query_scanner.py

# 4. Register in the scanner registry
# Edit packages/cherenkov/core/registry.py — add import + register call

# 5. Mark as validated in queue
# Edit manifests/cwe_queue.yaml: status: validated
```

### Reconfigure

**Override the model** (env var, no code change):
```bash
export cherenkov_OLLAMA_MODEL="qwen:latest"   # faster, less capable
python3 packages/cherenkov/dev_crew/swarm_orchestrator.py --once
```

**Change batch size:**
```python
# In swarm_orchestrator.py __main__ block:
await orch.run_forever(batch_size=5)   # default is 3
```

**Point at a different Ollama URL** (e.g. remote node):
```python
OLLAMA_URL = "http://192.168.1.50:11434"   # top of swarm_orchestrator.py
```

---

## Scaling

### Run multiple workers in parallel

The swarm is safe to run in parallel instances as long as they read different CWEs. Use tier partitioning:

```bash
# Worker A: tier 1 (fast, high-value)
cherenkov_OLLAMA_MODEL=qwen2.5-coder:7b \
  python3 packages/cherenkov/dev_crew/swarm_orchestrator.py >> logs/swarm-t1.log 2>&1 &

# Worker B: tier 2 (slower, complex)
cherenkov_OLLAMA_MODEL=qwen:latest \
  python3 packages/cherenkov/dev_crew/swarm_orchestrator.py >> logs/swarm-t2.log 2>&1 &
```

**Note:** Add a `tier` filter to `_load_pending()` if you need strict partitioning — currently all pending CWEs compete.

### Add a second Ollama model for coding

```bash
# Pull a stronger coder for complex CWEs:
ollama pull deepseek-coder-v2:16b

# Use it for tier-3 tasks:
cherenkov_OLLAMA_MODEL=deepseek-coder-v2:16b \
  python3 packages/cherenkov/dev_crew/swarm_orchestrator.py --once
```

### Run Ollama in Docker (isolated, restartable)

```bash
docker compose -f deploy/docker-compose.yml up ollama -d

# Confirm:
curl http://localhost:11434/api/tags

# Pull models into the container:
docker exec cherenkov-ollama ollama pull qwen2.5-coder:7b
docker exec cherenkov-ollama ollama pull llama3.2:3b
```

### Wire agents to the Docker Ollama (not host)

```bash
export OLLAMA_URL="http://localhost:11434"   # same port, Docker exposes it
# No code change needed — default URL already points here
```

---

## Monitoring & Logs

```bash
# Tail swarm logs:
tail -f logs/swarm.log

# Count candidates built so far:
ls candidates/generated_scanners/*.py 2>/dev/null | wc -l

# Check queue status summary:
python3 - << 'EOF'
import yaml
from collections import Counter
data = yaml.safe_load(open('manifests/cwe_queue.yaml'))
counts = Counter(item['status'] for item in data['queue'])
for status, n in sorted(counts.items()):
    print(f"  {status:12s} {n}")
EOF

# Check Ollama memory pressure:
curl -s http://localhost:11434/api/ps | python3 -m json.tool
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `httpx.ReadTimeout` | Model load time > timeout | Already fixed (300s). If still hitting, check Ollama memory |
| `ImportError: AutonomousSprint` | Old swarm_orchestrator without the class | Pull latest from this branch |
| `SSOT file not found` | Running from wrong directory | `cd /home/moaid/cherenkov-professional` first |
| `ruff: command not found` | ruff not on PATH | `pip install ruff` or `uv tool install ruff` |
| Swarm generates empty files | Model returned no code fence | Check `logs/swarm.log` — usually a bad prompt or model OOM |
| Ollama `model not found` | Model name mismatch | `ollama list` to see exact names, update constants |
| `yaml.scanner.ScannerError` | Bad YAML in cwe_queue.yaml | `python3 -c "import yaml; yaml.safe_load(open('manifests/cwe_queue.yaml'))"` |

---

## Quick Reference

```bash
# ── Aider ─────────────────────────────────────────────
./scripts/aider-tasks.sh help          # task menu
./scripts/aider-tasks.sh 2             # run a pre-built task
aider <file1> <file2>                  # interactive session

# ── dev_crew sprint ───────────────────────────────────
PYTHONPATH=packages python3 -m cherenkov.dev_crew.cli \
  --focus "<what to build>" --file "<target path>"

# ── SwarmOrchestrator ─────────────────────────────────
python3 packages/cherenkov/dev_crew/swarm_orchestrator.py --once   # one CWE
python3 packages/cherenkov/dev_crew/swarm_orchestrator.py          # forever
nohup python3 packages/cherenkov/dev_crew/swarm_orchestrator.py >> logs/swarm.log 2>&1 &

# ── Ollama ────────────────────────────────────────────
ollama list                            # installed models
ollama pull qwen2.5-coder:7b           # pull a model
curl http://localhost:11434/api/tags   # API health check
curl http://localhost:11434/api/ps     # currently loaded models
```
