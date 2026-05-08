# 💻 cherenkov Code Standards

## Python Style Guide

### 1. PEP 8 Compliance
```python
# ✅ GOOD
def calculate_risk_score(vulnerabilities: List[Vulnerability]) -> float:
    """Calculate overall risk score from vulnerabilities.
    
    Args:
        vulnerabilities: List of detected vulnerabilities
        
    Returns:
        Risk score between 0.0 and 10.0
    """
    if not vulnerabilities:
        return 0.0
    
    total_score = sum(v.severity_score for v in vulnerabilities)
    return min(total_score / len(vulnerabilities), 10.0)

# ❌ BAD
def calcRiskScore(vulns):  # Wrong naming, no types, no docstring
    if not vulns: return 0
    return sum([v.severity_score for v in vulns])/len(vulns)
```

### 2. Type Hints (Mandatory)
```python
from typing import List, Dict, Optional, Union
from datetime import datetime

# ✅ GOOD - All parameters and returns typed
def scan_target(
    url: str,
    scanners: List[BaseScanner],
    timeout: Optional[int] = 30,
    headers: Optional[Dict[str, str]] = None
) -> ScanResult:
    pass

# ❌ BAD - No type hints
def scan_target(url, scanners, timeout=30, headers=None):
    pass
```

### 3. Docstrings (Google Style)
```python
def execute_parallel_scan(
    targets: List[str],
    batch_size: int = 5
) -> List[ScanResult]:
    """Execute security scans in parallel batches.
    
    Scans multiple targets simultaneously using memory-efficient
    batching to prevent resource exhaustion.
    
    Args:
        targets: List of URLs to scan
        batch_size: Number of concurrent scans (default: 5)
        
    Returns:
        List of scan results, one per target
        
    Raises:
        ValueError: If batch_size < 1 or targets is empty
        TimeoutError: If any scan exceeds timeout
        
    Example:
        >>> targets = ["https://example.com", "https://test.com"]
        >>> results = execute_parallel_scan(targets, batch_size=2)
        >>> print(f"Found {len(results)} results")
    """
    pass
```

### 4. Naming Conventions
```python
# Classes: PascalCase
class VulnerabilityScanner:
    pass

# Functions/Methods: snake_case
def scan_for_xss(target: str) -> ScanResult:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private: _leading_underscore
def _internal_helper():
    pass

class MyClass:
    def __init__(self):
        self._private_attribute = None
```

### 5. Error Handling
```python
# ✅ GOOD - Specific exceptions, proper logging
import logging

logger = logging.getLogger(__name__)

def safe_scan(target: str) -> Optional[ScanResult]:
    try:
        result = perform_scan(target)
        return result
    except ConnectionError as e:
        logger.error(f"Connection failed for {target}: {e}")
        return None
    except TimeoutError as e:
        logger.warning(f"Scan timeout for {target}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error scanning {target}")
        raise

# ❌ BAD - Bare except, no logging
def safe_scan(target):
    try:
        return perform_scan(target)
    except:
        return None
```

### 6. Code Organization

---

## Testing Standards

### 1. Test Coverage (Minimum 80%)
```python
import pytest
from unittest.mock import Mock, patch

def test_xss_scanner_detects_vulnerability():
    """Test XSS scanner identifies reflected XSS."""
    scanner = XSSScanner()
    target = "https://example.com?q=<script>alert(1)</script>"
    
    result = scanner.scan(target)
    
    assert result.has_vulnerabilities
    assert len(result.vulnerabilities) == 1
    assert result.vulnerabilities.type == "XSS"
    assert result.vulnerabilities.severity == "HIGH"

@patch('requests.get')
def test_scanner_handles_network_error(mock_get):
    """Test scanner gracefully handles network failures."""
    mock_get.side_effect = ConnectionError("Network down")
    scanner = XSSScanner()
    
    result = scanner.scan("https://example.com")
    
    assert result.error is not None
    assert "network" in result.error.lower()
```

### 2. Test Organization

---

## Git Commit Standards

### Conventional Commits
```bash
# Format: <type>(<scope>): <subject>

feat(scanner): Add API security scanner
fix(auth): Resolve token expiration bug
docs(readme): Update installation instructions
test(xss): Add tests for reflected XSS detection
refactor(core): Simplify orchestrator logic
perf(parallel): Optimize batch processing
chore(deps): Update crewai to v0.71.0
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `chore`: Maintenance


