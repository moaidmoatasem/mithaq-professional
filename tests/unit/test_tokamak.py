import asyncio
import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from cherenkov.core.tokamak import Command, ScanTOKAMAK, Tokamak, TOKAMAKProfile, TokamakResult


def test_tokamak_execute_success():
    cmd = Command(payload="echo 'hello'", scanner_name="test_scanner", timeout=5)

    with patch("subprocess.run") as mock_run:
        mock_process = MagicMock()
        mock_process.stdout = "hello\n"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = Tokamak.execute(cmd)

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd_args = args[0]
        assert "docker" in cmd_args
        assert "run" in cmd_args
        # Tokamak.execute() always runs fully air-gapped (no network egress)
        assert "--network" in cmd_args
        assert "none" in cmd_args
        assert "--cap-drop=ALL" in cmd_args
        assert "--read-only" in cmd_args
        assert "-v" in cmd_args
        assert "sh" in cmd_args
        assert "/workspace/payload.sh" in cmd_args

        assert kwargs["timeout"] == 5
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True

        assert isinstance(result, TokamakResult)
        assert result.stdout == "hello\n"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert len(result.trace_hash) == 64
        assert "files_erased" in result.shred_receipt
        assert result.shred_receipt["method"] == "overwrite+truncate"


def test_tokamak_execute_timeout():
    cmd = Command(payload="sleep 10", scanner_name="slow", timeout=1)

    with patch("subprocess.run") as mock_run:
        timeout_error = subprocess.TimeoutExpired(cmd=["docker", "run"], timeout=1)
        timeout_error.stdout = "partial output"
        timeout_error.stderr = ""
        mock_run.side_effect = timeout_error

        result = Tokamak.execute(cmd)

        assert result.exit_code == 124
        assert result.stdout == "partial output"
        assert "TimeoutExpired" in result.stderr
        assert len(result.trace_hash) == 64


def test_tokamak_execute_exception():
    cmd = Command(payload="bad", scanner_name="crash", timeout=5)

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Docker not found")

        result = Tokamak.execute(cmd)

        assert result.exit_code == 1
        assert "Docker not found" in result.stderr
        assert len(result.trace_hash) == 64


def test_tokamak_signing_and_receipt():
    cmd = Command(payload="echo hello", scanner_name="test_scanner")

    with patch("subprocess.run") as mock_run:
        mock_process = MagicMock()
        mock_process.stdout = "hello\n"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = Tokamak().execute(cmd)

        assert isinstance(result, TokamakResult)
        assert len(result.trace_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.trace_hash)

        assert isinstance(result.shred_receipt, dict)
        assert "files_erased" in result.shred_receipt
        assert "timestamp" in result.shred_receipt
        assert "method" in result.shred_receipt
        assert result.shred_receipt["method"] == "overwrite+truncate"
        assert isinstance(result.duration_ms, float)
        assert result.duration_ms >= 0


def test_tokamak_image_env_override():
    """TOKAMAK_IMAGE env var overrides the default kali image."""
    cmd = Command(payload="echo 'test'", scanner_name="test_scanner", timeout=5)

    with (
        patch("subprocess.run") as mock_run,
        patch.dict(os.environ, {"TOKAMAK_IMAGE": "custom-image:latest"}),
    ):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        Tokamak.execute(cmd)

        args = mock_run.call_args[0][0]
        assert "custom-image:latest" in args

    # Default image when env var is unset
    with patch("subprocess.run") as mock_run, patch.dict(os.environ, {}, clear=False):
        os.environ.pop("TOKAMAK_IMAGE", None)
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        Tokamak.execute(cmd)

        args = mock_run.call_args[0][0]
        assert "kalilinux/kali-rolling" in args


def test_tokamak_profile_enum_values():
    """TOKAMAKProfile values map to the correct string identifiers."""
    assert TOKAMAKProfile.STANDARD.value == "standard"
    assert TOKAMAKProfile.MOBILE.value == "mobile"
    assert TOKAMAKProfile.KALI.value == "kali"


# ── ScanTOKAMAK.execute_poc() tests ──────────────────────────────────


class _MockDockerAPIError(Exception):
    """Stand-in for docker.errors.APIError."""


class _MockDockerImageNotFoundError(Exception):
    """Stand-in for docker.errors.ImageNotFound."""


@pytest.mark.asyncio
async def test_execute_poc_success():
    """execute_poc() spawns container, captures logs, signs, and removes."""
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.side_effect = [b"nmap output", b""]

    mock_client = MagicMock()
    mock_client.containers.run.return_value = mock_container

    with (
        patch("cherenkov.core.tokamak.DOCKER_AVAILABLE", True),
        patch("cherenkov.core.tokamak.docker", create=True) as mock_docker,
    ):
        mock_docker.from_env.return_value = mock_client
        mock_docker.errors.APIError = _MockDockerAPIError
        mock_docker.errors.ImageNotFound = _MockDockerImageNotFoundError
        tokamak = ScanTOKAMAK()
        result = await tokamak.execute_poc(exploit_command="nmap -sV target", timeout=10)

    mock_client.containers.run.assert_called_once()
    args, run_kwargs = mock_client.containers.run.call_args
    assert args[0] == "python:3.11-slim"
    assert run_kwargs["command"] == ["sh", "-c", "nmap -sV target"]
    assert run_kwargs["detach"] is True
    assert run_kwargs["labels"]["cherenkov.role"] == "tokamak"

    mock_container.wait.assert_called_once()
    mock_container.remove.assert_called_once_with(force=True)

    assert result.stdout == "nmap output"
    assert result.stderr == ""
    assert result.exit_code == 0
    assert len(result.trace_hash) == 64
    assert result.shred_receipt["method"] == "container_removed"
    assert isinstance(result.duration_ms, float)
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_execute_poc_timeout():
    """execute_poc() kills container and returns exit code 124 on timeout."""
    mock_container = MagicMock()
    mock_container.wait.side_effect = asyncio.TimeoutError()
    mock_container.logs.side_effect = [b"", b""]

    mock_client = MagicMock()
    mock_client.containers.run.return_value = mock_container

    with (
        patch("cherenkov.core.tokamak.DOCKER_AVAILABLE", True),
        patch("cherenkov.core.tokamak.docker", create=True) as mock_docker,
    ):
        mock_docker.from_env.return_value = mock_client
        mock_docker.errors.APIError = _MockDockerAPIError
        mock_docker.errors.ImageNotFound = _MockDockerImageNotFoundError
        tokamak = ScanTOKAMAK()
        result = await tokamak.execute_poc(exploit_command="sleep 30", timeout=1)

    mock_container.kill.assert_called_once()
    mock_container.remove.assert_called_once_with(force=True)
    assert result.exit_code == 124


@pytest.mark.asyncio
async def test_execute_poc_api_error():
    """execute_poc() handles Docker API errors gracefully."""
    mock_client = MagicMock()
    mock_client.containers.run.side_effect = _MockDockerAPIError("connection refused")

    with (
        patch("cherenkov.core.tokamak.DOCKER_AVAILABLE", True),
        patch("cherenkov.core.tokamak.docker", create=True) as mock_docker,
    ):
        mock_docker.from_env.return_value = mock_client
        mock_docker.errors.APIError = _MockDockerAPIError
        mock_docker.errors.ImageNotFound = _MockDockerImageNotFoundError
        tokamak = ScanTOKAMAK()
        result = await tokamak.execute_poc(exploit_command="nmap", timeout=5)

    assert result.exit_code == 1
    assert "Docker API error" in result.stderr
    assert result.trace_hash == ""


@pytest.mark.asyncio
async def test_execute_poc_image_not_found():
    """execute_poc() handles missing Docker images."""
    mock_client = MagicMock()
    mock_client.containers.run.side_effect = _MockDockerImageNotFoundError("python:3.11-slim")

    with (
        patch("cherenkov.core.tokamak.DOCKER_AVAILABLE", True),
        patch("cherenkov.core.tokamak.docker", create=True) as mock_docker,
    ):
        mock_docker.from_env.return_value = mock_client
        mock_docker.errors.APIError = _MockDockerAPIError
        mock_docker.errors.ImageNotFound = _MockDockerImageNotFoundError
        tokamak = ScanTOKAMAK()
        result = await tokamak.execute_poc(exploit_command="echo hi", timeout=5)

    assert result.exit_code == 1
    assert "Docker image not found" in result.stderr
    assert result.trace_hash == ""


@pytest.mark.asyncio
async def test_execute_poc_sha256_signing():
    """execute_poc() SHA-256 signs the trace with stdout+stderr+timestamp."""
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.side_effect = [b"evidence data", b""]

    mock_client = MagicMock()
    mock_client.containers.run.return_value = mock_container

    with (
        patch("cherenkov.core.tokamak.DOCKER_AVAILABLE", True),
        patch("cherenkov.core.tokamak.docker", create=True) as mock_docker,
    ):
        mock_docker.from_env.return_value = mock_client
        mock_docker.errors.APIError = _MockDockerAPIError
        mock_docker.errors.ImageNotFound = _MockDockerImageNotFoundError
        tokamak = ScanTOKAMAK()
        result = await tokamak.execute_poc(exploit_command="echo evidence", timeout=5)

    assert len(result.trace_hash) == 64
    assert all(c in "0123456789abcdef" for c in result.trace_hash)


@pytest.mark.asyncio
async def test_execute_poc_removes_container_on_exception():
    """Container is removed even when docker-py raises before execution."""
    mock_client = MagicMock()
    mock_client.containers.run.side_effect = _MockDockerAPIError("daemon down")

    with (
        patch("cherenkov.core.tokamak.DOCKER_AVAILABLE", True),
        patch("cherenkov.core.tokamak.docker", create=True) as mock_docker,
    ):
        mock_docker.from_env.return_value = mock_client
        mock_docker.errors.APIError = _MockDockerAPIError
        mock_docker.errors.ImageNotFound = _MockDockerImageNotFoundError
        tokamak = ScanTOKAMAK()
        result = await tokamak.execute_poc(exploit_command="echo test", timeout=5)

    assert result.exit_code == 1
    assert "Docker API error" in result.stderr
    assert result.shred_receipt["method"] == "container_removed"
    assert result.shred_receipt["profile"] == "standard"
