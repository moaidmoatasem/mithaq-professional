import pytest
from unittest.mock import MagicMock, patch
from cherenkov.core.tokamak import Tokamak, Command, TokamakResult
from datetime import datetime, timezone

def test_tokamak_execute_signing_and_receipt():
    command = Command(payload="echo hello", scanner_name="test_scanner")
    
    # Mock subprocess.run to avoid needing Docker during unit tests
    with patch("subprocess.run") as mock_run:
        mock_process = MagicMock()
        mock_process.stdout = "hello"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        result = Tokamak.execute(command)
        
        assert isinstance(result, TokamakResult)
        assert result.stdout == "hello"
        assert result.exit_code == 0
        assert result.trace_hash is not None
        assert len(result.trace_hash) == 64  # SHA-256 hex length
        assert "method" in result.shred_receipt
        assert result.shred_receipt["method"] == "overwrite+truncate"
        assert "timestamp" in result.shred_receipt

def test_tokamak_shred_receipt_format():
    command = Command(payload="exit 0")
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        
        result = Tokamak.execute(command)
        
        receipt = result.shred_receipt
        assert "files_erased" in receipt
        assert isinstance(receipt["files_erased"], list)
        assert len(receipt["files_erased"]) > 0

def test_tokamak_timeout_handling():
    command = Command(payload="sleep 100", timeout=1)
    
    import subprocess
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["docker", "run"], timeout=1, output="partial", stderr="timeout")
        
        result = Tokamak.execute(command)
        
        assert result.exit_code == 124
        assert "TimeoutExpired" in result.stderr
