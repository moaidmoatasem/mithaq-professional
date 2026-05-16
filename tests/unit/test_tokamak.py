import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from cherenkov.core.tokamak import Tokamak, Command, TokamakResult


def test_tokamak_execute_success():
    cmd = Command(payload="echo 'hello'", scanner_name="test_scanner", timeout=5)

    with (
        patch("subprocess.run") as mock_run,
        patch("tempfile.mkdtemp") as mock_mkdtemp,
    ):
        mock_tmpdir = os.path.join(tempfile.gettempdir(), "tokamak_test")
        mock_mkdtemp.return_value = mock_tmpdir

        mock_process = MagicMock()
        mock_process.stdout = "hello\n"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = Tokamak().execute(cmd)

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "docker" in args[0]
        assert "--network" in args[0]
        assert "none" in args[0]
        assert "payload.sh" in args[0]
        assert kwargs["timeout"] == 5

        assert isinstance(result, TokamakResult)
        assert result.stdout == "hello\n"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert len(result.trace_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.trace_hash)

        assert isinstance(result.shred_receipt, dict)
        assert "files_erased" in result.shred_receipt
        assert "timestamp" in result.shred_receipt
        assert "method" in result.shred_receipt
        assert result.shred_receipt["method"] == "overwrite+truncate"

        assert isinstance(result.duration_ms, float)
        assert result.duration_ms >= 0


def test_tokamak_execute_timeout():
    import subprocess

    cmd = Command(payload="sleep 10", scanner_name="slow", timeout=1)

    with patch("tempfile.mkdtemp") as mock_mkdtemp:
        mock_tmpdir = os.path.join(tempfile.gettempdir(), "tokamak_test")
        mock_mkdtemp.return_value = mock_tmpdir

        with patch("subprocess.run") as mock_run:
            timeout_error = subprocess.TimeoutExpired(
                cmd=["docker", "run"], timeout=1
            )
            timeout_error.stdout = "some output"
            timeout_error.stderr = ""
            mock_run.side_effect = timeout_error

            result = Tokamak.execute(cmd)

            assert result.exit_code == 124
            assert result.stdout == "some output"
            assert "TimeoutExpired" in result.stderr
            assert len(result.trace_hash) == 64
            assert result.duration_ms >= 0


def test_tokamak_execute_exception():
    cmd = Command(payload="bad", scanner_name="crash", timeout=5)

    with patch("tempfile.mkdtemp") as mock_mkdtemp:
        mock_tmpdir = os.path.join(tempfile.gettempdir(), "tokamak_test")
        mock_mkdtemp.return_value = mock_tmpdir

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Docker not found")

            result = Tokamak().execute(cmd)

            assert result.exit_code == 1
            assert "Docker not found" in result.stderr
            assert len(result.trace_hash) == 64
            assert result.duration_ms >= 0


def test_tokamak_execute_signs_output():
    with (
        patch("subprocess.run") as mock_run,
        patch("tempfile.mkdtemp") as mock_mkdtemp,
    ):
        mock_tmpdir = os.path.join(tempfile.gettempdir(), "tokamak_test")
        mock_mkdtemp.return_value = mock_tmpdir
        mock_run.return_value = MagicMock(
            stdout=b"ok", stderr=b"", returncode=0
        )

        result = Tokamak().execute(Command(payload="test", scanner_name="test"))

        assert len(result.trace_hash) == 64
        assert "files_erased" in result.shred_receipt
        assert result.duration_ms >= 0
