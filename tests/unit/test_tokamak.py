import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from cherenkov.core.tokamak import Command, Tokamak, TOKAMAKProfile, TokamakResult

pytestmark_profile = pytest.mark.ai_generated


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
        assert "--network" in cmd_args
        assert "none" in cmd_args
        assert "-v" in cmd_args
        assert "cherenkov-tokamak" in cmd_args
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


@pytest.mark.ai_generated
def test_tokamak_profile_selection():
    # Test mobile profile
    cmd = Command(payload="echo 'frida'", profile=TOKAMAKProfile.MOBILE)

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        Tokamak.execute(cmd)

        args = mock_run.call_args[0][0]
        assert "cherenkov-mobile-net" in args
        assert "python:3.11-slim" in args

    # Test kali profile
    cmd = Command(payload="nmap ...", profile=TOKAMAKProfile.KALI)

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        Tokamak.execute(cmd)

        args = mock_run.call_args[0][0]
        assert "none" in args
        assert "kalilinux/kali-rolling" in args
