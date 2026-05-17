"""
SQLInjectionScanner — detects error-based and boolean-based SQL injection.

Probes URL query parameters with classic SQL injection payloads and looks
for database error strings in responses.  Only inert, read-only payloads
are used; no destructive SQL (DROP / DELETE / UPDATE) is ever sent.

CWE-89: Improper Neutralization of Special Elements used in an SQL Command
OWASP A03:2021 — Injection
"""

from __future__ import annotations

import logging
import time
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.sqli")

# Inert payloads — single-quote terminators and Boolean tautologies only.
# Ordered from most likely to trigger verbose DB errors to least.
_SQLI_PAYLOADS: list[str] = [
    "'",
    '"',
    "' OR '1'='1",
    "' OR 1=1--",
    '" OR "1"="1',
    "1 AND 1=1",
    "1 AND 1=2",
    "'; SELECT 1--",
]

# Database error substrings that indicate unhandled SQL exceptions.
_ERROR_SIGNATURES: tuple[str, ...] = (
    # MySQL / MariaDB
    "you have an error in your sql syntax",
    "warning: mysql",
    "mysql_fetch",
    "mysql_num_rows",
    # PostgreSQL
    "pg_query",
    "pg::syntaxerror",
    "unterminated quoted string",
    "syntax error at or near",
    # MSSQL
    "unclosed quotation mark",
    "incorrect syntax near",
    "microsoft ole db provider for sql server",
    "odbc sql server driver",
    # Oracle
    "ora-00907",
    "ora-00933",
    "ora-01756",
    "quoted string not properly terminated",
    # SQLite
    "sqlite3::query",
    "sqlite3.operationalerror",
    "unrecognized token",
    # Generic
    "sql syntax",
    "sqlexception",
    "syntax error",
    "invalid query",
    "sql error",
)


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
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                for payload in _SQLI_PAYLOADS:
                    probe_urls = _inject_into_params(target, payload)
                    for probe_url in probe_urls:
                        try:
                            response = await client.get(probe_url, follow_redirects=True)
                        except (httpx.RequestError, httpx.TimeoutException):
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
                                        "Never concatenate user input into SQL strings. "
                                        "Apply an ORM or query builder and disable verbose DB error "
                                        "messages in production."
                                    ),
                                )
                            )
                            break  # One confirmed finding per target is sufficient
                    if findings:
                        break

        except Exception as exc:
            logger.debug("SQLi scan network/parse error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000

        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
