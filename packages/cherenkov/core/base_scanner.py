"""BaseScanner - Plugin Architecture Foundation"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List

import httpx
from pydantic import BaseModel


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Finding(BaseModel):
    id: str = ""
    title: str
    severity: Severity
    description: str
    cwe: str
    remediation: str
    scanner: str = ""


class ScanResult(BaseModel):
    target: str
    scanner_name: str
    findings: List[Finding] = []
    duration_ms: float = 0.0
    status: str = "completed"


class BaseScanner(ABC):
    """Abstract base class for all scanners"""

    def __init__(self, name: str = "", description: str = ""):
        self.name = name or self.__class__.__name__
        self.description = description or f"{self.__class__.__name__} scanner"
        self.version = "1.0.0"
        self.verify_ssl = True

    @abstractmethod
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - MUST be implemented"""
        pass

    async def _http_request(
        self, url: str, timeout: float, follow_redirects: bool = True
    ) -> httpx.Response:
        """Standard HTTP client with timeout"""
        async with httpx.AsyncClient(timeout=timeout, verify=self.verify_ssl) as client:
            return await client.get(url, follow_redirects=follow_redirects)
