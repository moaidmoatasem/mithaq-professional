# packages/cherenkov/core/tokamak.py
"""
Scan tokamak — ephemeral Docker containers per scan.

THREE PROFILES:
  TOKAMAKProfile.STANDARD — web/infra scans (strict, minimal caps, python:3.11-slim)
  TOKAMAKProfile.MOBILE   — APK/Frida scans (controlled exceptions, python:3.11-slim)
  TOKAMAKProfile.KALI     — active/web vuln scanning (air-gapped, kalilinux/kali-rolling)

Every container is destroyed on exit. Malicious payloads cannot persist.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import subprocess  # nosec B404 — subprocess is required to manage ephemeral Docker containers (TOKAMAK core)
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator

from pydantic import BaseModel, ConfigDict, model_validator

logger = logging.getLogger("cherenkov.tokamak")

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class TOKAMAKProfile(str, Enum):
    STANDARD = "standard"  # web, infra — strict
    MOBILE = "mobile"  # APK, Frida — controlled exceptions
    KALI = "kali"  # Kali rolling — active/web vuln scanning


# ──────────────────────────────────────────────
# Profile definitions
# ──────────────────────────────────────────────

_PROFILE_CONFIGS: dict[TOKAMAKProfile, dict] = {
    TOKAMAKProfile.STANDARD: {
        "image": "python:3.11-slim",
        "mem_limit": "512m",
        "cpu_period": 100_000,
        "cpu_quota": 50_000,  # 50% CPU
        "read_only": True,
        "tmpfs": {"/tmp": "size=64m"},  # nosec B108
        "security_opt": [
            "no-new-privileges",
            "seccomp=./seccomp-profile.json",
        ],
        "cap_drop": ["ALL"],
        "cap_add": ["NET_BIND_SERVICE"],
        "network_mode": "cherenkov-internal",
        "audit_note": "Standard web/infra scan — maximal restrictions",
    },
    TOKAMAKProfile.MOBILE: {
        "image": "python:3.11-slim",
        "mem_limit": "2g",  # Frida + Android emulator needs RAM
        "cpu_period": 100_000,
        "cpu_quota": 80_000,  # 80% CPU for decompilation
        "read_only": False,  # Frida writes to /tmp/frida
        "tmpfs": {"/tmp": "size=256m"},  # nosec B108
        "security_opt": [
            "no-new-privileges",
            # NOTE: No seccomp for mobile — ptrace required by Frida
            # AUDIT: This exception is documented and reviewed per-release.
        ],
        "cap_drop": ["ALL"],
        "cap_add": [
            "NET_BIND_SERVICE",
            "SYS_PTRACE",  # Required: Frida dynamic instrumentation
        ],
        "network_mode": "cherenkov-mobile-net",  # Separate from standard net
        "audit_note": (
            "Mobile scan — SYS_PTRACE added for Frida. "
            "Reviewed in security audit v0.X.X. "
            "Justification: Frida requires ptrace for instrumentation. "
            "Mitigation: separate docker network, no egress to prod."
        ),
    },
    TOKAMAKProfile.KALI: {
        "image": "kalilinux/kali-rolling",
        "mem_limit": "1g",
        "cpu_period": 100_000,
        "cpu_quota": 70_000,  # 70% CPU
        "read_only": True,
        "tmpfs": {"/tmp": "size=128m"},  # nosec B108
        "security_opt": [
            "no-new-privileges",
        ],
        "cap_drop": ["ALL"],
        "cap_add": [],
        "network_mode": "none",  # Air-gapped — no egress at all
        "audit_note": (
            "Kali rolling — full tool suite (nmap, nuclei, nikto). "
            "Network mode 'none' ensures no exfiltration. "
            "Ephemeral: container destroyed after PoC execution."
        ),
    },
}


# ──────────────────────────────────────────────
# TOKAMAK Models (Pydantic V2)
# ──────────────────────────────────────────────


class Command(BaseModel):
    payload: str
    scanner_name: str = ""
    timeout: int = 30

    @model_validator(mode="before")
    @classmethod
    def validate_timeout(cls, values: Any) -> Any:
        if isinstance(values, dict):
            timeout = values.get("timeout", 30)
            if timeout is not None:
                if timeout > 120:
                    values["timeout"] = 120
                elif timeout <= 0:
                    raise ValueError("timeout must be positive")
        return values


class TokamakResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stdout: str
    stderr: str
    trace_hash: str
    shred_receipt: dict
    exit_code: int
    duration_ms: float = 0.0


# ──────────────────────────────────────────────
# TOKAMAK Core
# ──────────────────────────────────────────────


class ScanTOKAMAK:
    """
    Ephemeral per-scan container with profile-based security.
    Container is destroyed on exit regardless of outcome.
    """

    POC_TIMEOUT = 30  # seconds — kills stalled PoC (accepted: Arch review)

    def __init__(self) -> None:
        if not DOCKER_AVAILABLE:
            raise RuntimeError("Docker SDK not available. Install: pip install docker")
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error("Failed to initialize Docker client: %s", e)
            self.client = None
        self._active_container = None

    @asynccontextmanager
    async def scan_context(
        self,
        target_url: str,
        profile: TOKAMAKProfile = TOKAMAKProfile.STANDARD,
        timeout: int = 120,
    ) -> AsyncGenerator:
        """
        Context manager: spin up an ephemeral tokamak, yield it, destroy on exit.

        The container is kept alive with `sleep infinity` so callers can inject
        payloads via exec_run() without a race against the default entrypoint.
        """
        if not self.client:
            raise RuntimeError("Docker daemon is unreachable or client failed to initialize.")

        container = None
        cfg = _PROFILE_CONFIGS[profile]

        if profile == TOKAMAKProfile.MOBILE:
            logger.info("MOBILE SANDBOX STARTED — %s. Audit: %s", target_url, cfg["audit_note"])

        try:
            container = await asyncio.to_thread(
                self.client.containers.run,
                image=cfg["image"],
                command=["sh", "-c", "sleep infinity"],  # keepalive — payload injected via exec_run
                detach=True,
                labels={"cherenkov.role": "tokamak", "cherenkov.target": target_url[:128]},
                environment={
                    "cherenkov_TARGET": target_url,
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
                    logger.warning(
                        "Failed to destroy tokamak %s: %s",
                        container.short_id if container else "?",
                        e,
                    )
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
        Execute a PoC payload in an ephemeral tokamak container.

        The payload is injected via exec_run() into a running container kept
        alive by `sleep infinity`.  Output is expected to be JSON with keys:
          - exploitable: bool
          - evidence: str (e.g. HTTP response snippet, error message)

        Returns a dict with 'exploitable' bool and 'evidence' str.
        """
        try:
            async with self.scan_context(
                target, profile=profile, timeout=self.POC_TIMEOUT
            ) as container:
                try:
                    exec_result = await asyncio.wait_for(
                        asyncio.to_thread(
                            container.exec_run,
                            ["sh", "-c", payload],
                            stdout=True,
                            stderr=True,
                            demux=False,
                        ),
                        timeout=self.POC_TIMEOUT,
                    )
                    exit_code = exec_result.exit_code
                    raw_output = exec_result.output or b""
                    output = raw_output.decode("utf-8", errors="replace").strip()

                    try:
                        result = json.loads(output)
                        if "exploitable" not in result:
                            result["exploitable"] = exit_code == 0
                        return result
                    except json.JSONDecodeError:
                        return {
                            "exploitable": exit_code == 0,
                            "evidence": output or f"No output (exit {exit_code})",
                        }

                except asyncio.TimeoutError:
                    logger.warning(
                        "TOKAMAK PoC timed out after %ss — %s", self.POC_TIMEOUT, technique
                    )
                    return {
                        "exploitable": False,
                        "evidence": f"PoC timed out after {self.POC_TIMEOUT}s",
                    }
        except Exception as e:
            logger.error("TOKAMAK fail-closed triggered during PoC execution: %s", e, exc_info=True)
            return {
                "exploitable": False,
                "evidence": f"Docker execution error: {e}",
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
                    "Watchdog killed stalled container: %s", self._active_container.short_id
                )
            except Exception as e:
                logger.error("Watchdog kill failed: %s", e)
            finally:
                self._active_container = None


class Tokamak:
    """
    Sandbox environment for executing untrusted payloads securely via Docker.
    """

    async def execute_poc(self, request: ValidationRequest) -> ValidationResult:
        """
        Execute a PoC payload using docker-py to verify a finding.
        """
        if not DOCKER_AVAILABLE:
            logger.error("Docker SDK not available, cannot execute PoC.")
            return ValidationResult(is_verified=False)

        try:
            client = docker.from_env()
        except Exception as e:
            logger.error("Failed to initialize Docker client for execute_poc: %s", e)
            return ValidationResult(is_verified=False)

        container = None
        try:
            container = await asyncio.to_thread(
                client.containers.run,
                image="alpine:latest",
                command=request.exploit_command,
                detach=True,
                network_mode="none",
                mem_limit="128m",
                cpu_quota=50000,
                remove=False
            )

            result = await asyncio.to_thread(container.wait, timeout=request.timeout_seconds)
            exit_code = result.get("StatusCode", 1)

            if exit_code == 0:
                logs = await asyncio.to_thread(container.logs)
                trace_data = logs.decode("utf-8", errors="replace") + str(datetime.now(timezone.utc).timestamp())
                trace_hash = hashlib.sha256(trace_data.encode()).hexdigest()
                return ValidationResult(is_verified=True, cryptographic_proof=trace_hash)
            else:
                return ValidationResult(is_verified=False)

        except (docker.errors.NotFound, docker.errors.APIError) as e:
            logger.error("Docker API error during execute_poc: %s", e)
            return ValidationResult(is_verified=False)
        except Exception as e:
            logger.error("Unexpected error during execute_poc: %s", e)
            return ValidationResult(is_verified=False)
        finally:
            if container:
                try:
                    await asyncio.to_thread(container.remove, force=True)
                except Exception as e:
                    logger.warning("Failed to force remove container %s: %s", container.short_id, e)
