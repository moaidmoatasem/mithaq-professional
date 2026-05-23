"""CI/CD Integration Scanner — detects exposed pipeline configs and build artefacts."""

from __future__ import annotations

import time

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

# Paths that expose CI/CD configuration or build artefacts
_CICD_PATHS: list[tuple[str, str, Severity, str, str]] = [
    (
        "/.github/workflows",
        "GitHub Actions workflow directory accessible",
        Severity.MEDIUM,
        "CWE-538",
        "Restrict web serving to application paths only; CI configs should not be web-accessible.",
    ),
    (
        "/.gitlab-ci.yml",
        "GitLab CI configuration file exposed",
        Severity.HIGH,
        "CWE-538",
        "Ensure .gitlab-ci.yml is not served by your web server.",
    ),
    (
        "/.travis.yml",
        "Travis CI configuration file exposed",
        Severity.MEDIUM,
        "CWE-538",
        "Remove .travis.yml from the web root or block access via server config.",
    ),
    (
        "/Jenkinsfile",
        "Jenkinsfile exposed",
        Severity.MEDIUM,
        "CWE-538",
        "Block access to Jenkinsfile in your web server configuration.",
    ),
    (
        "/Dockerfile",
        "Dockerfile exposed",
        Severity.LOW,
        "CWE-538",
        "Block access to Dockerfile in your web server configuration.",
    ),
    (
        "/docker-compose.yml",
        "docker-compose.yml exposed — may reveal service topology and secrets",
        Severity.HIGH,
        "CWE-538",
        "Remove docker-compose.yml from the web root.",
    ),
    (
        "/.env",
        ".env file accessible — likely contains secrets",
        Severity.CRITICAL,
        "CWE-312",
        "Immediately restrict access to .env. Rotate all exposed credentials.",
    ),
    (
        "/.env.production",
        ".env.production file accessible",
        Severity.CRITICAL,
        "CWE-312",
        "Immediately restrict access to .env.production. Rotate all exposed credentials.",
    ),
    (
        "/build.log",
        "Build log exposed — may reveal internal paths and dependencies",
        Severity.LOW,
        "CWE-538",
        "Remove build logs from the web root.",
    ),
    (
        "/pipeline.yml",
        "pipeline.yml exposed",
        Severity.MEDIUM,
        "CWE-538",
        "Block access to pipeline.yml in your server configuration.",
    ),
    (
        "/bitbucket-pipelines.yml",
        "Bitbucket Pipelines configuration exposed",
        Severity.MEDIUM,
        "CWE-538",
        "Block access to bitbucket-pipelines.yml in your server configuration.",
    ),
    (
        "/circle.yml",
        "CircleCI configuration exposed",
        Severity.MEDIUM,
        "CWE-538",
        "Block access to circle.yml in your server configuration.",
    ),
    (
        "/.circleci/config.yml",
        "CircleCI config directory accessible",
        Severity.MEDIUM,
        "CWE-538",
        "Block access to .circleci/ in your server configuration.",
    ),
]


class CICDIntegrationScanner(BaseScanner):
    """Detects exposed CI/CD configuration files and build artefacts."""

    def __init__(self) -> None:
        super().__init__(
            name="cicd_integration",
            description="Detects exposed CI/CD pipeline configs, Dockerfiles, and build artefacts",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: list[Finding] = []

        from urllib.parse import urlparse

        parsed = urlparse(target)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for path, title, severity, cwe, remediation in _CICD_PATHS:
            url = base.rstrip("/") + path
            try:
                resp = await self._http_request(url, timeout)
                if resp.status_code == 200:
                    findings.append(
                        Finding(
                            title=title,
                            severity=severity,
                            description=(f"The path '{path}' returned HTTP 200. {title}."),
                            cwe=cwe,
                            remediation=remediation,
                        )
                    )
            except Exception:
                pass

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=(time.monotonic() - start) * 1000,
        )
