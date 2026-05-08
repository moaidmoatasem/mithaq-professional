# src/cherenkov/core/tokamak.py
"""
Scan tokamak — ephemeral Docker containers per scan.

TWO PROFILES (accepted: Copilot — Frida/mobile needs different caps):
  TOKAMAKProfile.STANDARD — web/infra scans (strict, minimal caps)
  TOKAMAKProfile.MOBILE   — APK/Frida scans (controlled exceptions, audited)

Every container is destroyed on exit. Malicious payloads cannot persist.
"""
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncGenerator

logger = logging.getLogger("cherenkov.tokamak")

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class TOKAMAKProfile(str, Enum):
    STANDARD = "standard"   # web, infra — strict
    MOBILE   = "mobile"     # APK, Frida — controlled exceptions


# ──────────────────────────────────────────────
# Profile definitions
# ──────────────────────────────────────────────

_PROFILE_CONFIGS: dict[TOKAMAKProfile, dict] = {

    TOKAMAKProfile.STANDARD: {
        "mem_limit":    "512m",
        "cpu_period":   100_000,
        "cpu_quota":    50_000,           # 50% CPU
        "read_only":    True,
        "tmpfs":        {"/tmp": "size=64m"},
        "security_opt": [
            "no-new-privileges",
            "seccomp=./seccomp-profile.json",
        ],
        "cap_drop":     ["ALL"],
        "cap_add":      ["NET_BIND_SERVICE"],
        "network_mode": "cherenkov-internal",
        "audit_note":   "Standard web/infra scan — maximal restrictions",
    },

    TOKAMAKProfile.MOBILE: {
        "mem_limit":    "2g",             # Frida + Android emulator needs RAM
        "cpu_period":   100_000,
        "cpu_quota":    80_000,           # 80% CPU for decompilation
        "read_only":    False,            # Frida writes to /tmp/frida
        "tmpfs":        {"/tmp": "size=256m"},
        "security_opt": [
            "no-new-privileges",
            # NOTE: No seccomp for mobile — ptrace required by Frida
            # AUDIT: This exception is documented and reviewed per-release.
        ],
        "cap_drop":     ["ALL"],
        "cap_add":      [
            "NET_BIND_SERVICE",
            "SYS_PTRACE",       # Required: Frida dynamic instrumentation
        ],
        "network_mode": "cherenkov-mobile-net",   # Separate from standard net
        "audit_note":   (
            "Mobile scan — SYS_PTRACE added for Frida. "
            "Reviewed in security audit v0.X.X. "
            "Justification: Frida requires ptrace for instrumentation. "
            "Mitigation: separate docker network, no egress to prod."
        ),
    },
}


# ──────────────────────────────────────────────
# TOKAMAK
# ──────────────────────────────────────────────

class ScanTOKAMAK:
    """
    Ephemeral per-scan container with profile-based security.
    Container is destroyed on exit regardless of outcome.
    """

    POC_TIMEOUT = 30      # seconds — kills stalled PoC (accepted: Arch review)

    def __init__(self) -> None:
        if not DOCKER_AVAILABLE:
            raise RuntimeError(
                "Docker SDK not available. Install: pip install docker"
            )
        self.client = docker.from_env()
        self._active_container = None

    @asynccontextmanager
    async def scan_context(
        self,
        target_url: str,
        profile: TOKAMAKProfile = TOKAMAKProfile.STANDARD,
        timeout: int = 120,
    ) -> AsyncGenerator:
        """
        Context manager: create tokamak, yield, destroy on exit.

        Example:
            async with tokamak.scan_context("https://target.com") as container:
                result = await asyncio.wait_for(
                    container.exec_run("cherenkov scan ..."),
                    timeout=timeout
                )
        """
        container = None
        cfg = _PROFILE_CONFIGS[profile]

        if profile == TOKAMAKProfile.MOBILE:
            logger.info(
                "MOBILE SANDBOX STARTED — %s. Audit: %s",
                target_url, cfg["audit_note"]
            )

        try:
            container = await asyncio.to_thread(
                self.client.containers.run,
                image="cherenkov-scanner:latest",
                detach=True,
                environment={
                    "cherenkov_TARGET":  target_url,
                    "cherenkov_TIMEOUT": str(timeout),
                    "cherenkov_ALLOWED_SCHEMES": "http,https",
                },
                **{k: v for k, v in cfg.items() if k != "audit_note"},
            )
            self._active_container = container
            yield container

        finally:
            if container:
                try:
                    await asyncio.to_thread(container.stop, timeout=5)
                    await asyncio.to_thread(container.remove, force=True)
                    logger.debug("TOKAMAK destroyed: %s", container.short_id)
                except Exception as e:
                    logger.warning("Failed to destroy tokamak %s: %s", container.short_id if container else "?", e)
                finally:
                    self._active_container = None

    async def run_poc(
        self,
        target: str,
        technique: str,
        payload: str,
        profile: TOKAMAKProfile = TOKAMAKProfile.STANDARD,
    ) -> dict:
        """
        Execute a PoC in an ephemeral tokamak.
        Returns dict with 'exploitable' bool and 'evidence' str.
        """
        async with self.scan_context(target, profile=profile, timeout=self.POC_TIMEOUT) as container:
            exit_code = await asyncio.wait_for(
                asyncio.to_thread(container.wait, timeout=self.POC_TIMEOUT),
                timeout=self.POC_TIMEOUT + 5,
            )
            logs = await asyncio.to_thread(container.logs)
            output = logs.decode("utf-8", errors="replace")

            try:
                result = json.loads(output)
                return result
            except json.JSONDecodeError:
                return {
                    "exploitable": False,
                    "evidence": f"Non-JSON output (exit {exit_code.get('StatusCode')})",
                }

    async def kill_active(self) -> None:
        """
        Watchdog: kill the active container immediately.
        Called by TokamakAgent when PoC times out.
        (Accepted: Arch review — prevents worker node freeze)
        """
        if self._active_container:
            try:
                await asyncio.to_thread(self._active_container.kill)
                logger.warning(
                    "Watchdog killed stalled container: %s",
                    self._active_container.short_id
                )
            except Exception as e:
                logger.error("Watchdog kill failed: %s", e)
            finally:
                self._active_container = None

