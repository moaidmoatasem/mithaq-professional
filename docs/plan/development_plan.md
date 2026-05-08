# cherenkov — Final Refined Development Plan
> Version: 2.0 | Synthesized from: Deep code review + Gemini + Perplexity
> Date: May 2026 | 26 weeks to v1.0

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Ground Truth: What Exists Today](#2-ground-truth-what-exists-today)
3. [Phase 0 — Emergency Security Fixes](#3-phase-0--emergency-security-fixes)
4. [Phase 1 — Repository & Foundation Cleanup](#4-phase-1--repository--foundation-cleanup)
5. [Phase 2 — Architecture Overhaul](#5-phase-2--architecture-overhaul)
6. [Phase 3 — Real Scanner Library](#6-phase-3--real-scanner-library)
7. [Phase 4 — AI Integration (Real)](#7-phase-4--ai-integration-real)
8. [Phase 5 — Production Hardening & v1.0](#8-phase-5--production-hardening--v10)
9. [Testing Strategy](#9-testing-strategy)
10. [Storage & Persistence Layer](#10-storage--persistence-layer)
11. [Docker & Container Security](#11-docker--container-security)
12. [Documentation Strategy](#12-documentation-strategy)
13. [Community & Open Source Strategy](#13-community--open-source-strategy)
14. [Honest Metrics & Success Criteria](#14-honest-metrics--success-criteria)
15. [What NOT to Do](#15-what-not-to-do)

---

## 1. Executive Summary

cherenkov is a local-first, AI-assisted security testing framework. The vision is
legitimate: deterministic scanners + local LLM triage, zero cloud dependency,
async plugin architecture. The gap between that vision and the current codebase
is large but closeable.

This plan consolidates feedback from three independent deep reviews into one
phase-gated execution path. The 132 generated scanner modules are not thrown
away — they become candidates that earn their place by passing a validation gate.

**The single guiding principle:** prove it first, claim it second.

---

## 2. Ground Truth: What Exists Today

| Item | Current state |
|---|---|
| Working validated scanners | 3 (headers, HTTP methods, HTTPS) |
| Generated unvalidated modules | 132 (in swarm_outputs/, orchestration_iterations/) |
| Test coverage enforced | 25% (fail_under = 25 in pyproject.toml) |
| Web framework | Flask — debug=True, host=0.0.0.0 (CRITICAL vuln) |
| AI integration | Scaffold only — not wired to scanner pipeline |
| Persistence layer | None (in-memory list — lost on restart) |
| CLI | Argparse, 59 lines, 2 commands |
| CHANGELOG.md | Empty (0 bytes) |
| Active critical CVEs | 2: RCE via Flask debug, stored XSS in web UI |
| Repo cleanliness | Poor: 4 source dirs, 20+ root scripts, diary files |

**A note on the 132 modules:** These are AI-generated drafts, not working
scanners. They are raw material. They become official scanners one by one as
they pass the Phase 3 validation gate. Until then they live in candidates/ and
do not appear in any public-facing claims.

---

## 3. Phase 0 — Emergency Security Fixes

**Timeline:** This week. No exceptions.
**Blocker:** Do not publish, announce, or link to this project until this
phase is complete and tagged as v0.1.1-security.

### 3.1 Flask Debug Mode + Host Binding (CRITICAL — CVSS 10.0)

Flask debug=True activates the Werkzeug interactive debugger, which exposes
arbitrary Python code execution via browser. Binding to 0.0.0.0 makes this
reachable by anyone on the same network.

```python
# cherenkov_web.py — replace the __main__ block entirely
if __name__ == '__main__':
    import os
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    host  = os.getenv('FLASK_HOST', '127.0.0.1')   # localhost by default
    port  = int(os.getenv('FLASK_PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
```

Add to .env.example:
```
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### 3.2 Stored XSS in Web UI (CRITICAL — CVSS 9.0)

Two-layer fix required. The root issue is JavaScript-side; server-side
validation is the second layer.

```javascript
// templates/index.html — JavaScript fix
function escapeHtml(str) {
    const map = {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'};
    return String(str).replace(/[&<>"']/g, m => map[m]);
}
// Replace:  html += '<h3>Scan Results for ' + data.target + '</h3>';
// With:
html += '<h3>Scan Results for ' + escapeHtml(data.target) + '</h3>';
```

```python
# cherenkov_web.py — server-side URL validation
from urllib.parse import urlparse

@app.route('/api/scan', methods=['POST'])
def run_scan():
    data = request.json
    target_url = data.get('url', '').strip()

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400
    try:
        parsed = urlparse(target_url)
        if parsed.scheme not in ('http', 'https'):
            return jsonify({'error': 'Only http/https URLs are supported'}), 400
        if not parsed.netloc:
            return jsonify({'error': 'Invalid URL: missing hostname'}), 400
    except Exception:
        return jsonify({'error': 'Invalid URL format'}), 400
    # ... rest of function
```

### 3.3 Bare Exception Handlers (HIGH)

Silent exceptions in a security scanner produce false negatives.

```bash
# Find all instances
grep -rn "except:" . --include="*.py" | grep -v "#"
grep -rn "except Exception: pass" . --include="*.py"
```

```python
# Before
except:
    print(f" [✓] {method} is blocked")

# After
except (requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.SSLError) as e:
    logger.debug("Method %s unreachable: %s", method, e)
    print(f" [✓] {method} is blocked or unreachable")
```

### 3.4 URL Input Validation

```python
from urllib.parse import urlparse

class SimpleScanner:
    def __init__(self, target_url: str):
        parsed = urlparse(target_url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError(f"Unsupported scheme '{parsed.scheme}'.")
        if not parsed.netloc:
            raise ValueError("Invalid URL: missing hostname.")
        self.target = target_url
```

### 3.5 HTTP Methods Consent Warning

The scanner sends PUT/DELETE without warning. This can modify server state.

```python
def scan_http_methods(self):
    print("\n[!] WARNING: This sends PUT/DELETE/TRACE requests to the target.")
    print("    Only run against systems you own or have written authorisation to test.")
    consent = input("    Continue? (yes/no): ").strip().lower()
    if consent != 'yes':
        print("    Skipping HTTP methods scan.")
        return
```

### 3.6 Phase 0 Commit

```bash
git checkout -b fix/phase-0-critical-security
git add -A
git commit -m "fix: resolve critical security vulnerabilities

- Flask debug=False, bind to localhost by default (env-configurable)
- Fix stored XSS via innerHTML in web dashboard
- Add server-side URL validation to /api/scan
- Add URL validation to SimpleScanner.__init__
- Replace bare except handlers with typed exception handling
- Add consent prompt before mutating HTTP method checks

Severity: CRITICAL (CVSS 10.0 RCE, CVSS 9.0 XSS)"

git push origin fix/phase-0-critical-security
# Merge to main immediately
git tag -a v0.1.1-security -m "Security patch: fix RCE and XSS"
git push --tags
```

---

## 4. Phase 1 — Repository & Foundation Cleanup

**Timeline:** Weeks 1–2
**Goal:** A senior security engineer clones this repo and understands what it
does and doesn't do within 5 minutes.

### 4.1 Honest README Rewrite

```markdown
# cherenkov — Local AI Security Testing Framework

> **Status:** Alpha · v0.1.1 · Phase 1 of 5

## What works today
- 3 validated HTTP scanners: security headers, HTTP methods, HTTPS detection
- CLI: `cherenkov scan https://example.com`
- Local web dashboard (localhost only)
- Ollama integration scaffold (not yet wired to scanner pipeline)

## Roadmap
- Phase 2: Plugin architecture + FastAPI migration (Weeks 2–4)
- Phase 3: 50 validated scanners (Weeks 4–10)
- Phase 4: Dual-brain AI triage (Weeks 10–18)
- Phase 5: v1.0 production release (Weeks 18–26)

## Honest metrics
| Metric | Today | v1.0 target |
|--------|-------|-------------|
| Validated scanners | 3 | 50+ |
| Test coverage | ~30% | 80% |
| AI integration | scaffold | end-to-end |
```

### 4.2 Remove All Development Diary Files

```bash
git rm TONIGHT_ACHIEVEMENTS.md SESSION_ACHIEVEMENTS.md AGENT_MEMORY.md
git rm PROJECT_SUMMARY.md README.md.backup README_BADGES.txt
git rm -f cherenkov-nexus-web
```

Move (not delete) the 132 generated candidates:
```bash
mkdir -p candidates/generated_scanners
mv swarm_outputs/* candidates/generated_scanners/
mv orchestration_iterations/* candidates/generated_scanners/
mv autonomous_development/* candidates/generated_scanners/
```

Create candidates/README.md:
```markdown
# Scanner Candidates

AI-generated scanner drafts awaiting validation.
A scanner graduates to src/cherenkov/scanners/ only after:
1. Passing unit tests (positive + negative)
2. Finding a known vulnerability on DVWA/bWAPP
3. NOT firing on OWASP WebGoat safe pages
4. Passing bandit with no new issues
5. Having CWE reference + remediation docs
```

Add to .gitignore:
```
*ACHIEVEMENTS.md
AGENT_MEMORY.md
*.backup
swarm_outputs/
orchestration_iterations/
autonomous_development/
```

### 4.3 Consolidate Dependencies — Single pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "cherenkov"
version = "0.1.1"
description = "Local-first AI security testing framework"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "rich>=13.0.0",
    "typer>=0.12.0",
]

[project.optional-dependencies]
web = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.29.0",
]
ai = [
    "crewai>=0.28.0",
    "langchain-community>=0.0.20",
]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.4.0",
    "bandit>=1.7.8",
    "pre-commit>=3.7.0",
    "hypothesis>=6.0.0",
    "pip-audit>=2.7.0",
]

[project.scripts]
cherenkov = "cherenkov.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.coverage.report]
fail_under = 30
precision = 2
show_missing = true

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "S"]
ignore = ["E501", "S101"]
```

Delete requirements.txt entirely. One source of truth.

### 4.4 Clean Repository Root

```bash
mkdir -p scripts/dev scripts/docker tools

mv launch_*.sh celebration_scan.sh deploy_now.sh scripts/dev/
mv dockerize_everything.sh batch_scan.sh run_all_systems.sh scripts/dev/
mv run_autonomous_agent.sh test_scan.sh scripts/dev/
mv get-docker.sh docker-manage.sh scripts/docker/
mv analyze_generated_scanners.py extract_scanners.py tools/
mv refine_scanners.py auto_improve_scanners.py tools/
mv autonomous_roadmap_executor.py tools/
```

### 4.5 Real CHANGELOG.md and STATUS.md

CHANGELOG.md first real entry:
```markdown
# Changelog

## v0.1.1 — Security Patch (May 2026)
### Fixed
- CRITICAL: Flask debug mode disabled; server binds to localhost by default
- CRITICAL: Stored XSS in web dashboard via unescaped innerHTML
- HIGH: Bare `except:` handlers replaced with typed exception handling
- HIGH: URL validation added to SimpleScanner and /api/scan
- MEDIUM: Consent prompt added before mutating HTTP method checks

## v0.1.0-alpha — Initial Release (May 2026)
- Basic HTTP security header scanner
- HTTP methods scanner
- HTTPS/HTTP detection
- Flask web dashboard
- Basic CLI
```

---

## 5. Phase 2 — Architecture Overhaul

**Timeline:** Weeks 2–4

### 5.1 Drop Flask, Use FastAPI

Flask is replaced by FastAPI for three concrete reasons: async support for
concurrent scanning, native Pydantic integration, auto-generated OpenAPI docs.
The current web app is ~200 lines — migration is small.

### 5.2 BaseScanner Plugin Architecture

```python
# src/cherenkov/core/base_scanner.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"

@dataclass
class Finding:
    scanner:     str
    title:       str
    severity:    Severity
    description: str
    evidence:    str        = ""
    remediation: str        = ""
    cwe_id:      str|None   = None
    cvss_score:  float|None = None

@dataclass
class ScanResult:
    target:       str
    scanner:      str
    findings:     list[Finding] = field(default_factory=list)
    error:        str|None      = None
    scan_time_ms: int           = 0

class BaseScanner(ABC):
    name:        str       = ""
    description: str       = ""
    severity:    Severity  = Severity.INFO
    tags:        list[str] = field(default_factory=list)

    def __init__(self, target: str, timeout: int = 10):
        self.target  = target
        self.timeout = timeout

    @abstractmethod
    async def scan(self) -> ScanResult: ...

    def finding(self, **kwargs) -> Finding:
        return Finding(scanner=self.name, **kwargs)
```

Auto-discovery registry — drop a file in scanners/ and it's registered:
```python
# src/cherenkov/core/registry.py
import importlib, pkgutil
from pathlib import Path
from .base_scanner import BaseScanner

_registry: dict[str, type[BaseScanner]] = {}

def load_all_scanners() -> None:
    path = Path(__file__).parent.parent / "scanners"
    for _, name, _ in pkgutil.iter_modules([str(path)]):
        module = importlib.import_module(f"cherenkov.scanners.{name}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if (isinstance(obj, type) and issubclass(obj, BaseScanner)
                    and obj is not BaseScanner and obj.name):
                _registry[obj.name] = obj
```

### 5.3 Async Scan Engine with Rate Limiting

Rate limiting is not optional. An async engine running 10+ concurrent scanners
can trigger WAF blocks or accidentally overload fragile staging environments.

```python
# src/cherenkov/core/engine.py
import asyncio, time, logging
from .registry import all_scanners, load_all_scanners
from .base_scanner import ScanResult

logger = logging.getLogger(__name__)

class ScanEngine:
    def __init__(self, concurrency: int = 10, requests_per_sec: float = 5.0):
        self.concurrency      = concurrency
        self.requests_per_sec = requests_per_sec
        self._last_req        = 0.0
        load_all_scanners()

    async def _rate_limit(self) -> None:
        if self.requests_per_sec <= 0:
            return
        gap = 1.0 / self.requests_per_sec
        elapsed = time.monotonic() - self._last_req
        if elapsed < gap:
            await asyncio.sleep(gap - elapsed)
        self._last_req = time.monotonic()

    async def run(
        self,
        target:        str,
        scanner_names: list[str] | None = None,
        tags:          list[str] | None = None,
    ) -> list[ScanResult]:
        scanners = all_scanners()
        if scanner_names:
            scanners = {k: v for k, v in scanners.items() if k in scanner_names}
        if tags:
            scanners = {k: v for k, v in scanners.items()
                       if any(t in getattr(v, 'tags', []) for t in tags)}

        sem = asyncio.Semaphore(self.concurrency)

        async def run_one(name, cls):
            async with sem:
                await self._rate_limit()
                t0 = time.monotonic()
                try:
                    result = await cls(target).scan()
                    result.scan_time_ms = int((time.monotonic() - t0) * 1000)
                    return result
                except Exception as e:
                    logger.warning("Scanner %s failed: %s", name, e)
                    return ScanResult(target=target, scanner=name, error=str(e),
                                     scan_time_ms=int((time.monotonic() - t0) * 1000))

        return await asyncio.gather(*[run_one(n, c) for n, c in scanners.items()])
```

### 5.4 SQLite Persistence Layer

The in-memory scan history list is replaced with SQLite. No external services
required. Data persists at ~/.cherenkov/results.db.

```python
# src/cherenkov/storage/database.py
import sqlite3, json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import asdict
from ..core.base_scanner import ScanResult

DB_PATH = Path.home() / ".cherenkov" / "results.db"

def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                target     TEXT NOT NULL,
                started_at TEXT NOT NULL,
                results    TEXT NOT NULL
            )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_target ON scans(target)")

def save_scan(target: str, results: list[ScanResult]) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO scans (target, started_at, results) VALUES (?, ?, ?)",
            (target, datetime.utcnow().isoformat(), json.dumps([asdict(r) for r in results]))
        )
        return cur.lastrowid

def get_scan(scan_id: int) -> list | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT results FROM scans WHERE id=?", (scan_id,)).fetchone()
    return json.loads(row[0]) if row else None

def list_scans(limit: int = 50) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, target, started_at FROM scans ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [{"id": r[0], "target": r[1], "started_at": r[2]} for r in rows]

def prune_old_scans(days: int = 90) -> int:
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("DELETE FROM scans WHERE started_at < ?", (cutoff,)).rowcount
```

### 5.5 Canonical Project Structure

```
cherenkov-professional/
├── src/cherenkov/
│   ├── cli.py
│   ├── core/
│   │   ├── base_scanner.py
│   │   ├── engine.py
│   │   ├── registry.py
│   │   └── report.py
│   ├── scanners/          ← validated only
│   ├── api/
│   │   └── main.py        ← FastAPI
│   ├── storage/
│   │   └── database.py
│   └── ai/
│       ├── triage.py
│       └── orchestrator.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── candidates/
│   ├── README.md
│   └── generated_scanners/
├── docs/
├── scripts/dev/ scripts/docker/
├── tools/
├── .github/workflows/ .github/ISSUE_TEMPLATE/
├── pyproject.toml
├── Dockerfile
├── Dockerfile.minimal   ← two only
├── docker-compose.yml
└── README.md
```

### 5.6 Typer CLI

```python
# src/cherenkov/cli.py
import typer, asyncio
from rich.console import Console
from rich.table import Table
from .core.engine import ScanEngine
from .storage.database import init_db, save_scan

app     = typer.Typer(name="cherenkov")
console = Console()

@app.command()
def scan(
    target:  str       = typer.Argument(...),
    output:  str       = typer.Option("table", "-o"),
    rps:     float     = typer.Option(5.0, "--rps", help="Max requests/sec"),
    timeout: int       = typer.Option(10),
):
    init_db()
    engine  = ScanEngine(requests_per_sec=rps)
    results = asyncio.run(engine.run(target))
    scan_id = save_scan(target, results)
    console.print(f"Scan #{scan_id} complete.")

@app.command("list-scanners")
def list_scanners():
    from .core.registry import load_all_scanners, all_scanners
    load_all_scanners()
    t = Table("Name", "Description", "Tags")
    for name, cls in all_scanners().items():
        t.add_row(name, cls.description, ", ".join(getattr(cls, 'tags', [])))
    console.print(t)

@app.command()
def history(limit: int = typer.Option(20, "-n")):
    from .storage.database import list_scans, init_db
    init_db()
    t = Table("ID", "Target", "Started at")
    for r in list_scans(limit):
        t.add_row(str(r['id']), r['target'], r['started_at'])
    console.print(t)
```

---

## 6. Phase 3 — Real Scanner Library

**Timeline:** Weeks 4–10
**Target:** 50 validated scanners. Not 132. Quality over quantity.
**Rule:** Every scanner passes the validation gate before being counted.

### 6.1 Validation Gate (Required for Every Scanner)

No exceptions. Not for candidates generated by CrewAI, not for hand-written ones.

1. Unit test: positive case (finds the vulnerability with mocked HTTP)
2. Unit test: negative case (no false positive when vulnerability absent)
3. Integration test: fires on DVWA or bWAPP running in Docker
4. False-positive test: does NOT fire on OWASP WebGoat safe pages
5. Bandit: no new security issues
6. Documentation: CWE ID, description, technique, remediation in docstring

### 6.2 Tier 1 — Infrastructure & Configuration (Weeks 4–6)

Deterministic header/config checks. Highest confidence, lowest false-positive rate.

| Scanner | What it checks | CWE |
|---|---|---|
| security_headers | X-Frame-Options, CSP, HSTS, X-Content-Type | CWE-16 |
| tls_configuration | TLS version, cipher suites, cert expiry | CWE-326 |
| cors_policy | Wildcard origins, credentialed requests | CWE-942 |
| cookie_security | HttpOnly, Secure, SameSite | CWE-614 |
| http_methods | TRACE, PUT, DELETE, CONNECT allowed | CWE-749 |
| content_type_sniffing | X-Content-Type-Options missing | CWE-430 |
| clickjacking | Frame-ancestors / X-Frame-Options | CWE-1021 |
| information_disclosure | Server version, stack traces in headers | CWE-200 |
| directory_listing | Open directory indexes | CWE-548 |
| robots_txt_analysis | Sensitive paths in robots.txt | CWE-200 |

### 6.3 Tier 2 — Input Validation (Weeks 6–8)

Active probing. Require explicit user consent before firing.

| Scanner | Technique |
|---|---|
| xss_reflected | Reflected XSS payloads in query params |
| xss_dom | DOM XSS via URL fragments |
| sql_injection | Error-based, boolean-based SQLi (read-only payloads) |
| open_redirect | Redirect parameter manipulation |
| ssrf_basic | SSRF via URL params, internal IP detection |
| path_traversal | ../../etc/passwd patterns |
| command_injection | OS command injection in params |
| xxe_basic | XML External Entity injection |
| file_upload | Dangerous file type acceptance |
| idor_basic | Predictable numeric object references |

### 6.4 Tier 3 — Authentication & Business Logic (Weeks 8–10)

| Scanner | What it checks |
|---|---|
| jwt_validation | None alg, weak secrets, missing expiry |
| auth_bypass | Common bypass patterns |
| rate_limiting | Brute-force protection on login |
| session_management | Session fixation, low-entropy tokens |
| graphql_introspection | Introspection in production |
| swagger_exposure | OpenAPI docs in production |
| default_credentials | admin/admin, admin/password |
| api_versioning | Deprecated API versions still active |
| 2fa_bypass | OTP reuse, missing 2FA on sensitive actions |
| password_policy | Weak password acceptance |

---

## 7. Phase 4 — AI Integration (Real)

**Timeline:** Weeks 10–18

### 7.1 Dual-Brain: The Actual Spec

**Brain 1 — Deterministic:** Scanner engine from Phase 3. Rule-based, fast,
high precision. Always runs. Its output is ground truth.

**Brain 2 — LLM triage:** Local model via Ollama. Receives Brain 1's structured
findings and adds:
- Ranks findings by exploitability and attack chain potential
- Identifies cross-finding risk patterns
- Produces plain-English remediation steps in context

Brain 2 never overrides Brain 1. If Ollama isn't running, full scanner results
are returned without enrichment. The AI layer enriches; it never gates.

### 7.2 LLM with Context Window Management

Findings are chunked before sending. 50 scanners on a large app can easily
exceed a 3B–8B model's context window.

```python
# src/cherenkov/ai/triage.py
import httpx, json, logging
from ..core.base_scanner import ScanResult, Finding

logger = logging.getLogger(__name__)

TRIAGE_PROMPT = """You are a senior security engineer reviewing scan results.

Target: {target}
Findings:
{findings}

Tasks:
1. Rank by actual exploitability in context (consider attack chaining)
2. Identify patterns that increase overall risk
3. Write one specific remediation per finding

Respond in valid JSON only:
{{
  "prioritized_findings": [{{"title":"...","reason":"...","exploitability":"high|medium|low"}}],
  "risk_patterns": ["..."],
  "remediations": {{"finding_title": "remediation text"}}
}}"""

MAX_FINDINGS_PER_CHUNK = 15

class LLMTriage:
    def __init__(self, model="qwen2.5-coder:7b", ollama_url="http://localhost:11434"):
        self.model      = model
        self.ollama_url = ollama_url

    def _chunks(self, findings: list) -> list:
        return [findings[i:i+MAX_FINDINGS_PER_CHUNK]
                for i in range(0, len(findings), MAX_FINDINGS_PER_CHUNK)]

    async def triage(self, results: list[ScanResult]) -> dict:
        findings = [f for r in results for f in r.findings]
        target   = results[0].target if results else "unknown"

        if not findings:
            return {"prioritized_findings": [], "risk_patterns": [], "remediations": {}}

        merged = {"prioritized_findings": [], "risk_patterns": [], "remediations": {}}

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                for chunk in self._chunks(findings):
                    text = "\n".join(
                        f"- [{f.severity.upper()}] {f.title}: {f.description}"
                        for f in chunk
                    )
                    resp = await client.post(
                        f"{self.ollama_url}/api/generate",
                        json={"model": self.model,
                              "prompt": TRIAGE_PROMPT.format(target=target, findings=text),
                              "stream": False}
                    )
                    resp.raise_for_status()
                    r = json.loads(resp.json().get("response", "{}"))
                    merged["prioritized_findings"].extend(r.get("prioritized_findings", []))
                    merged["risk_patterns"].extend(r.get("risk_patterns", []))
                    merged["remediations"].update(r.get("remediations", {}))
            return merged
        except httpx.ConnectError:
            logger.info("Ollama unavailable — returning results without AI triage")
            return {"error": "Ollama not available", "raw_findings": [f.title for f in findings]}
```

### 7.3 Model Recommendations

| Model | RAM | Speed | Security quality | Use |
|---|---|---|---|---|
| tinyllama | 637MB | ~8s | Poor | Last resort (<8GB RAM) |
| qwen2.5-coder:3b | 2.1GB | ~98s | Fair | Low-RAM dev |
| **qwen2.5-coder:7b** | **4.3GB** | **~120s** | **Good** | **Default** |
| deepseek-r1:8b | 5GB | ~140s | Very good | Security focus |

### 7.4 CrewAI: One Specific Job

CrewAI's only role: given a vulnerability class description, generate a Python
scanner that passes the Phase 3 validation gate. It does not run scans. It does
not do triage. Every scanner it generates still must pass every gate step.

---

## 8. Phase 5 — Production Hardening & v1.0

**Timeline:** Weeks 18–26

### 8.1 Output Formats

```bash
cherenkov scan https://example.com --output table   # default
cherenkov scan https://example.com --output json    # machine-readable
cherenkov scan https://example.com --output sarif   # CI/CD (GitHub Code Scanning)
cherenkov scan https://example.com --output html    # standalone report
```

SARIF v2.1 output enables direct GitHub Code Scanning and GitLab SAST
integration without additional tooling. This is the single most important
feature for professional pipeline adoption.

### 8.2 Supply Chain Security

```bash
pip-audit                              # dependency CVE audit
cyclonedx-py requirements > sbom.xml  # generate SBOM
pre-commit run --all-files             # lint + security hooks
```

### 8.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "${{ matrix.python-version }}"}
      - run: pip install -e .[dev]
      - run: ruff check .
      - run: bandit -r src/ -ll
      - run: pip-audit
      - run: pytest --cov=cherenkov --cov-fail-under=80
      - uses: codecov/codecov-action@v4
```

### 8.4 v1.0 Definition of Done

All boxes must be checked. No exceptions.

- [ ] 50+ validated scanners (each with unit tests + DVWA proof)
- [ ] 80% test coverage enforced in CI across Python 3.10/3.11/3.12
- [ ] SARIF v2.1 output tested against GitHub Code Scanning
- [ ] Zero known CVEs in cherenkov itself
- [ ] AI triage end-to-end with qwen2.5-coder:7b, degrades without Ollama
- [ ] SQLite persistence — scan history survives restart
- [ ] Docker runs as non-root user, image <2GB, starts <30s
- [ ] pip install cherenkov works cleanly
- [ ] cherenkov scan, cherenkov history, cherenkov list-scanners all functional
- [ ] CONTRIBUTING.md with scanner development quickstart
- [ ] One external user has successfully run it

---

## 9. Testing Strategy

### 9.1 Infrastructure

```bash
docker run -d -p 8080:80 vulnerables/web-dvwa
docker run -d -p 8081:80 webpwnized/mutillidae

pytest tests/unit/           # fast, no network
pytest tests/integration/ -m requires_dvwa
pytest --cov=cherenkov --cov-report=html
```

### 9.2 Scanner Test Template

```python
# tests/unit/scanners/test_security_headers.py
import pytest
from unittest.mock import AsyncMock, patch
from cherenkov.scanners.security_headers import SecurityHeadersScanner
from cherenkov.core.base_scanner import Severity

@pytest.mark.asyncio
async def test_missing_csp_flagged():
    with patch("httpx.AsyncClient.get") as mock:
        mock.return_value = AsyncMock(headers={}, status_code=200)
        result = await SecurityHeadersScanner("https://example.com").scan()
    finding = next((f for f in result.findings if "Content-Security-Policy" in f.title), None)
    assert finding is not None
    assert finding.severity == Severity.MEDIUM

@pytest.mark.asyncio
async def test_no_false_positive_with_all_headers():
    headers = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": "max-age=31536000",
        "X-Content-Type-Options": "nosniff",
    }
    with patch("httpx.AsyncClient.get") as mock:
        mock.return_value = AsyncMock(headers=headers, status_code=200)
        result = await SecurityHeadersScanner("https://example.com").scan()
    assert result.findings == []

@pytest.mark.asyncio
@pytest.mark.requires_dvwa
async def test_dvwa_integration():
    result = await SecurityHeadersScanner("http://localhost:8080").scan()
    assert len(result.findings) > 0
```

### 9.3 Coverage Targets Per Phase

| Phase | fail_under |
|---|---|
| Phase 0 | 25 |
| Phase 1 | 35 |
| Phase 2 | 50 |
| Phase 3 | 65 |
| Phase 4 | 75 |
| Phase 5 / v1.0 | 80 (enforced in CI) |

---

## 10. Storage & Persistence Layer

- SQLite by default at ~/.cherenkov/results.db — zero external deps
- cherenkov_DB_URL env var accepts PostgreSQL connection string for teams
- 90-day auto-prune policy documented in README
- Alembic for schema migrations — never drop/recreate the database

---

## 11. Docker & Container Security

### 11.1 Non-Root User (Required)

A security tool executing active payloads must never run as root in its container.

```dockerfile
FROM python:3.12-slim AS base
RUN useradd --create-home --shell /bin/bash cherenkov
WORKDIR /app

FROM base AS builder
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

FROM base AS final
COPY --from=builder /install /usr/local
COPY src/ ./src/
USER cherenkov                           # ← non-root
EXPOSE 8000
CMD ["uvicorn", "cherenkov.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Keep Two Dockerfiles Only

- Dockerfile — full build (scanner + web + AI deps)
- Dockerfile.minimal — scanner + CLI only

Delete Dockerfile.agent, Dockerfile.optimized, Dockerfile.simple.

### 11.3 Docker Compose

```yaml
services:
  cherenkov:
    build: .
    ports: ["127.0.0.1:8000:8000"]   # localhost only
    volumes: ["cherenkov-data:/home/cherenkov/.cherenkov"]
    environment: [cherenkov_OLLAMA_URL=http://ollama:11434]
    depends_on: [ollama]
  ollama:
    image: ollama/ollama:latest
    ports: ["127.0.0.1:11434:11434"]
    volumes: ["ollama-data:/root/.ollama"]
volumes:
  cherenkov-data:
  ollama-data:
```

---

## 12. Documentation Strategy

Write docs when the code exists. Never before.

| Document | Write when |
|---|---|
| README | Phase 1 — honest current state |
| CONTRIBUTING.md | Phase 1 — before accepting any PRs |
| Scanner dev guide | Phase 2 — when BaseScanner exists |
| API reference | Phase 2 — auto-generated by FastAPI |
| Installation guide | Phase 3 — when pip-installable |
| Security architecture | Phase 4 — when dual-brain is in code |
| User guide | Phase 5 — when stable |

Record an asciinema demo of cherenkov scanning DVWA before any community promotion.
That single asset does more for adoption than every badge and feature list combined.

---

## 13. Community & Open Source Strategy

### 13.1 Issue Templates

- bug_report.md
- scanner_request.md
- false_positive.md
- scanner_contribution.md

### 13.2 PR Template

```markdown
## What does this PR do?

## Scanner validation (scanner PRs only)
- [ ] Unit test: positive case
- [ ] Unit test: negative case
- [ ] Validated against DVWA or bWAPP
- [ ] Does not fire on WebGoat safe pages
- [ ] CWE ID documented

## General
- [ ] ruff check passes
- [ ] bandit passes with no new issues
- [ ] pytest passes with no coverage regression
```

### 13.3 When to Promote

Do not post to Hacker News, Reddit, or security communities until:
- 20+ validated scanners exist
- The README reflects reality
- The asciinema demo exists
- One external user has confirmed it works

The security engineering community is experienced and skeptical. Post before
these conditions are met and the comments section will be permanent reputational
damage that is very hard to recover from.

---

## 14. Honest Metrics & Success Criteria

| Milestone | Criteria |
|---|---|
| Phase 0 | Zero critical/high CVEs. v0.1.1 tagged. |
| Phase 1 | README matches reality. No diary files. Single pyproject.toml. |
| Phase 2 | BaseScanner, engine, SQLite, FastAPI, Typer CLI. 3 scanners migrated. |
| Phase 3 | 50 validated scanners. Each with tests + DVWA proof + CWE docs. |
| Phase 4 | Dual-brain end-to-end. Triage degrades without Ollama. Chunking in place. |
| v1.0 | All Phase 5 checklist complete. 80% CI coverage. pip-installable. SARIF. |

---

## 15. What NOT to Do

**Do not count AI-generated drafts as working scanners.**
Files in candidates/ are not scanners. They count when they pass the gate.

**Do not update the README before the code.**
Every sentence must be backed by working code today.

**Do not add features while open issues are unresolved.**
Fix the 8 open issues before adding more scanners.

**Do not skip the validation gate. Ever.**
A false negative in a security tool is worse than no tool.

**Do not ship until Phase 0 is complete.**
There are active CVSS 10.0 and CVSS 9.0 vulnerabilities in the current release.

**Do not race toward 132.**
50 validated scanners that reliably work > 132 claimed scanners where 3 are proven.

**Do not measure progress in lines of code.**
A 60-line scanner with DVWA proof > 1,500 lines of generated boilerplate.

---

*This document lives at docs/plan/development_plan.md.
Update the Ground Truth section at the start of every phase.*

