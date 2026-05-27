"""
CICDIntegrationScanner — detects exposed CI/CD configurations, Git repositories, and pipeline engines.

Probes target servers for common exposed configuration files, build files, and APIs
associated with DevOps/CI-CD pipelines (such as GitHub Actions, GitLab CI, Jenkins, and Git directories).

CWE-538: Insertion of Sensitive Information into Externally-Accessible File or Directory
CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
"""

from __future__ import annotations

import logging
import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.cicd_integration")

# Configuration probe paths, their expected signatures, and finding templates.
_PROBE_CONFIGS = [
    {
        "path": "/.git/config",
        "signatures": ["[core]", "repositoryformatversion"],
        "title": "Exposed Git Configuration Directory",
        "severity": Severity.HIGH,
        "cwe": "CWE-538",
        "description": (
            "The Git configuration file '.git/config' is publicly accessible. "
            "Exposing the Git directory allows unauthorized users to clone the entire repository "
            "and potentially access sensitive credentials, source code, or internal tokens."
        ),
        "remediation": (
            "Restrict access to the '.git' directory on the web server (e.g., using "
            "'.htaccess' in Apache, 'location ~ /\\.git' in Nginx, or placing the directory "
            "outside the web server document root)."
        ),
    },
    {
        "path": "/.git/HEAD",
        "signatures": ["ref: refs/heads/"],
        "title": "Exposed Git HEAD Reference",
        "severity": Severity.HIGH,
        "cwe": "CWE-538",
        "description": (
            "The Git HEAD file '.git/HEAD' is publicly accessible, indicating the "
            "entire Git metadata folder is exposed. This can leak git branches, commit logs, "
            "and revision history."
        ),
        "remediation": "Configure the web server to deny access to all hidden files and folders starting with a dot.",
    },
    {
        "path": "/.github/workflows/ci.yml",
        "signatures": ["name:", "jobs:"],
        "title": "Exposed GitHub Actions Workflow Configuration",
        "severity": Severity.MEDIUM,
        "cwe": "CWE-538",
        "description": (
            "A GitHub Actions workflow file '.github/workflows/ci.yml' is publicly accessible. "
            "Exposing these configuration files reveals details about internal CI/CD steps, "
            "dependencies, deployment strategies, and environment variable names."
        ),
        "remediation": (
            "Ensure that deployment workflows are not served as static resources. "
            "Configure the web server to block access to the '.github' folder."
        ),
    },
    {
        "path": "/.gitlab-ci.yml",
        "signatures": ["stages:", "image:", "before_script:"],
        "title": "Exposed GitLab CI Configuration",
        "severity": Severity.MEDIUM,
        "cwe": "CWE-538",
        "description": (
            "The GitLab CI configuration file '.gitlab-ci.yml' is publicly accessible. "
            "This exposes build stages, runner tags, script commands, and internal infrastructure information."
        ),
        "remediation": "Block external web access to the '.gitlab-ci.yml' file via web server configuration rules.",
    },
    {
        "path": "/Jenkinsfile",
        "signatures": ["pipeline {", "node {", "agent "],
        "title": "Exposed Jenkins Pipeline Configuration",
        "severity": Severity.MEDIUM,
        "cwe": "CWE-538",
        "description": (
            "A Jenkins pipeline configuration file 'Jenkinsfile' is publicly accessible. "
            "This leaks build steps, credentials IDs, and deployment instructions."
        ),
        "remediation": "Remove the 'Jenkinsfile' from the web-accessible directory or restrict access to it.",
    },
    {
        "path": "/api/json",
        "signatures": ["jenkins.model", "primaryView", '"jobs"'],
        "title": "Exposed Jenkins Build Engine API",
        "severity": Severity.HIGH,
        "cwe": "CWE-200",
        "description": (
            "The Jenkins build engine API is publicly exposed without authentication. "
            "An unauthorized attacker can read server configuration details, build statuses, "
            "and active jobs."
        ),
        "remediation": "Enable global security on Jenkins and enforce authentication for all API endpoints.",
    },
]


class CICDIntegrationScanner(BaseScanner):
    """
    Scanner to detect exposed CI/CD and DevOps files or endpoints by probing
    the target for configuration files, git directories, and control engines.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "cicd_integration_scanner",
            description
            or "Detects exposed CI/CD configurations, Git repositories, and pipeline engines",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - probing target paths for CI/CD exposure."""
        start = time.monotonic()
        findings: List[Finding] = []

        # Canonicalize target URL format
        if not target.startswith(("http://", "https://")):
            base_url = f"http://{target}"
        else:
            base_url = target

        base_url = base_url.rstrip("/")

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                for probe in _PROBE_CONFIGS:
                    url = f"{base_url}{probe['path']}"
                    try:
                        response = await client.get(url, follow_redirects=True)
                    except (httpx.RequestError, httpx.TimeoutException):
                        continue

                    if response.status_code == 200:
                        body = response.text
                        # Check if any of the signatures appear in the response body
                        matched_sig = next(
                            (sig for sig in probe["signatures"] if sig in body), None
                        )

                        if matched_sig:
                            findings.append(
                                Finding(
                                    title=probe["title"],
                                    severity=probe["severity"],
                                    description=probe["description"],
                                    cwe=probe["cwe"],
                                    remediation=probe["remediation"],
                                )
                            )

        except Exception as exc:
            logger.debug("CI/CD scan network/parse error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
