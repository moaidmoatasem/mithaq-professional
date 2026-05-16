"""MobileScanner — Abstract base for mobile (APK/IPA) scanners."""

from __future__ import annotations

import shutil
import tempfile
from abc import abstractmethod
from pathlib import Path
from typing import Optional

import httpx

from cherenkov.core.base_scanner import BaseScanner, ScanResult


class MobileScanner(BaseScanner):
    """Abstract base for mobile application scanners.

    Provides helpers for APK validation, temporary workspace management,
    and running external tools (apktool, androguard) via subprocess.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__(name, description)
        self._workspace: Optional[tempfile.TemporaryDirectory] = None

    @abstractmethod
    async def scan(self, target: str, timeout: float = 10.0) -> ScanResult:
        pass

    async def _download_apk(self, url: str, timeout: float = 30.0) -> bytes:
        async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            return resp.content

    def _validate_apk(self, filepath: str) -> bool:
        path = Path(filepath)
        if not path.is_file():
            return False
        if path.stat().st_size == 0:
            return False
        magic = path.read_bytes()[:4]
        return magic == b"PK\x03\x04"

    def _create_workspace(self) -> Path:
        self._workspace = tempfile.TemporaryDirectory(prefix="cherenkov_mobile_")
        return Path(self._workspace.name)

    def _cleanup_workspace(self) -> None:
        if self._workspace is not None:
            try:
                self._workspace.cleanup()
            except Exception:
                pass
            self._workspace = None

    def _check_tool(self, tool: str) -> bool:
        return shutil.which(tool) is not None
