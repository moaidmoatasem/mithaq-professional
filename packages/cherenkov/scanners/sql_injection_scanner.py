"""SQL Injection Scanner (CWE-89)"""

import logging
import time
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger(__name__)

# Basic error-based SQLi signatures (MySQL, PostgreSQL, MSSQL, Oracle)
_ERROR_SIGNATURES = [
    "you have an error in your sql syntax",
    "unclosed quotation mark before the character string",
    "postgresql query failed: error:",
    "ora-00933: sql command not properly ended",
    "mysql_fetch_array() expects parameter 1 to be resource",
    "sqlite3.operationalerror:",
    "warning: mysql_connect():",
    "driver][odbc sql server driver",
]

# Simple probes to trigger syntax errors
_PROBES = ["'", "''", "'; --", '") OR 1=1 --', "')) OR 1=1 --"]


def _inject_into_params(url: str, payload: str) -> list[str]:
    """Return a list of URLs, each with one query parameter replaced by *payload*."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    if not params:
        # No query params — inject as a synthetic `id` parameter for probing.
        probe = urlunparse(parsed._replace(query=urlencode({"id": payload})))
        return [probe]

    injected: list[str] = []
    for key in params:
        modified = dict(params)
        modified[key] = [payload]
        new_query = urlencode(modified, doseq=True)
        injected.append(urlunparse(parsed._replace(query=new_query)))
    return injected


class SQLInjectionScanner(BaseScanner):
    """
    Probes query parameters for SQL injection by sending inert payloads and
    checking whether the server leaks database error strings.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "sql_injection_scanner",
            description or "Detects error-based SQL injection (CWE-89)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start_time = time.monotonic()
        findings: list[Finding] = []

        try:
            # Only probe if target looks like a URL
            if not target.startswith(("http://", "https://")):
                return ScanResult(target=target, scanner_name=self.name, status="skipped")

            # For each probe, inject it into each query parameter and check response
            for payload in _PROBES:
                test_urls = _inject_into_params(target, payload)

                for test_url in test_urls:
                    try:
                        async with self._http_request_with_timeout(test_url, timeout) as response:
                            if response is None:
                                continue

                            body_lower = response.text.lower()
                            matched_sig = next(
                                (sig for sig in _ERROR_SIGNATURES if sig in body_lower), None
                            )

                            if response.status_code == 200 and matched_sig:
                                findings.append(
                                    Finding(
                                        title="SQL Injection",
                                        severity=Severity.CRITICAL,
                                        description=(
                                            f"The endpoint returned a database error signature "
                                            f'("{matched_sig}") when the query parameter was set to '
                                            f'"{payload}". This indicates unparameterised SQL and '
                                            f"possible full database compromise."
                                        ),
                                        cwe="CWE-89",
                                        remediation=(
                                            "Use parameterised queries or prepared statements exclusively. "
                                            "Never concatenate user input directly into SQL strings. "
                                            "Apply an ORM or query builder and disable verbose DB error "
                                            "messages in production."
                                        ),
                                        scanner="sql_injection",
                                    )
                                )
                                break  # One confirmed finding per target is sufficient
                    except Exception:
                        continue
                if findings:
                    break

        except Exception as exc:
            logger.debug("SQLi scan network/parse error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start_time) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
        )

    import contextlib

    @contextlib.asynccontextmanager
    async def _http_request_with_timeout(self, url: str, timeout: float):
        """Helper to handle http requests with timeout and return None on error."""
        try:
            resp = await self._http_request(url, timeout)
            yield resp
        except Exception:
            yield None
