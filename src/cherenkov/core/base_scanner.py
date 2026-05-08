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
    title: str
    severity: Severity
    description: str
    cwe: str
    remediation: str


class ScanResult(BaseModel):
    target: str
    scanner_name: str
    findings: List[Finding] = []
    duration_ms: float = 0.0
    status: str = "completed"


class BaseScanner(ABC):
    """Abstract base class for all scanners"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.version = "1.0.0"

    @abstractmethod
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        """Execute the scan - MUST be implemented"""
        pass

    async def _http_request(self, url: str, timeout: float) -> httpx.Response:
        """Standard HTTP client with timeout"""
        async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
            return await client.get(url, follow_redirects=True)
