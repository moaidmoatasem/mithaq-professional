"""Static XXE Scanner — analyzes response bodies for XXE artifact patterns"""

from __future__ import annotations

import logging
import re
import time
from typing import List

import httpx

from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity

logger = logging.getLogger("cherenkov.scanners.static_xxe")

_XXE_ENTITY_PATTERN = re.compile(
    r"<!ENTITY\s+\w+\s+(SYSTEM|PUBLIC)\s+[\"']",
    re.IGNORECASE,
)

_XML_BOMB_PATTERN = re.compile(
    r"<!ENTITY\s+\w+\s+\"[^\"']{100,}\"",
    re.IGNORECASE,
)

_DTD_EXTERNAL_PATTERN = re.compile(
    r"<!DOCTYPE\s+\w+\s+(SYSTEM|PUBLIC)\s+[\"']",
    re.IGNORECASE,
)

_PARAM_ENTITY_PATTERN = re.compile(
    r"<!ENTITY\s+%\s+\w+\s+(SYSTEM|PUBLIC)\s+[\"']",
    re.IGNORECASE,
)


class StaticXXEScanner(BaseScanner):
    """Detects XXE patterns by analyzing XML responses and document structures."""

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(
            name or "static_xxe_scanner",
            description
            or "Static analysis scanner for XML External Entity (XXE) patterns (CWE-611)",
        )

    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        start = time.monotonic()
        findings: List[Finding] = []

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
                try:
                    response = await client.get(target, follow_redirects=True)
                except (httpx.RequestError, httpx.TimeoutException):
                    duration_ms = (time.monotonic() - start) * 1000
                    return ScanResult(
                        target=target,
                        scanner_name=self.name,
                        findings=[],
                        duration_ms=duration_ms,
                        status="completed",
                    )

                content_type = response.headers.get("content-type", "")
                body = response.text

                is_xml = "xml" in content_type.lower() or body.strip().startswith("<?xml")

                if not is_xml:
                    duration_ms = (time.monotonic() - start) * 1000
                    return ScanResult(
                        target=target,
                        scanner_name=self.name,
                        findings=[],
                        duration_ms=duration_ms,
                        status="completed",
                    )

                if _XXE_ENTITY_PATTERN.search(body):
                    findings.append(
                        Finding(
                            title="XML External Entity (XXE) Reference Detected",
                            severity=Severity.HIGH,
                            description=(
                                "The response contains XML with inline DOCTYPE declarations "
                                "that reference external entities. This pattern may indicate "
                                "that the server processes XML entities unsafely."
                            ),
                            cwe="CWE-611",
                            remediation=(
                                "Disable DTD processing and external entity resolution "
                                "in the XML parser. Use a secure parser configuration that "
                                "rejects external entities by default."
                            ),
                        )
                    )

                if _DTD_EXTERNAL_PATTERN.search(body):
                    findings.append(
                        Finding(
                            title="External DTD Declaration in XML",
                            severity=Severity.MEDIUM,
                            description=(
                                "The XML response contains an external DTD declaration. "
                                "External DTDs can be used for XXE injection if the parser "
                                "resolves them."
                            ),
                            cwe="CWE-611",
                            remediation=(
                                "Disable DTD processing in the XML parser. If DTDs are "
                                "required, use an allowlist of trusted DTD sources."
                            ),
                        )
                    )

                if _PARAM_ENTITY_PATTERN.search(body):
                    findings.append(
                        Finding(
                            title="Parameter Entity with External Reference",
                            severity=Severity.HIGH,
                            description=(
                                "Parameter entities with SYSTEM or PUBLIC references "
                                "are detected in the XML. These can be used for blind "
                                "XXE exfiltration."
                            ),
                            cwe="CWE-611",
                            remediation=(
                                "Disable parameter entity resolution. If entities are "
                                "required, ensure they reference only internal, trusted content."
                            ),
                        )
                    )

                if _XML_BOMB_PATTERN.search(body):
                    findings.append(
                        Finding(
                            title="XML Entity Expansion (Billion Laughs) Pattern",
                            severity=Severity.MEDIUM,
                            description=(
                                "The XML contains deeply nested or large entity definitions "
                                "characteristic of entity expansion attacks (XML bomb)."
                            ),
                            cwe="CWE-776",
                            remediation=(
                                "Limit entity expansion depth and total entity count in "
                                "the XML parser.禁用DTD processing if not required."
                            ),
                        )
                    )

        except Exception as exc:
            logger.debug("StaticXXEScanner error for %s: %s", target, exc)

        duration_ms = (time.monotonic() - start) * 1000
        return ScanResult(
            target=target,
            scanner_name=self.name,
            findings=findings,
            duration_ms=duration_ms,
            status="completed",
        )
