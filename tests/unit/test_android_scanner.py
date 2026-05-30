import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cherenkov.scanners.mobile.android_scanner import AndroidScanner

pytestmark = pytest.mark.ai_generated


@pytest.fixture
def mock_apktool_installed():
    with patch("shutil.which") as mock_which:

        def which_impl(cmd):
            if cmd in ("apktool", "androguard"):
                return f"/usr/bin/{cmd}"
            return None

        mock_which.side_effect = which_impl
        yield mock_which


@pytest.mark.asyncio
async def test_android_scanner_tools_missing():
    with patch("shutil.which", return_value=None):
        with patch("os.path.exists", return_value=True):
            scanner = AndroidScanner()
            result = await scanner.scan("test.apk")
            assert result.scanner_name == "android"
            assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_android_scanner_findings(mock_apktool_installed):
    scanner = AndroidScanner()

    # Mock asyncio.create_subprocess_exec
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        with patch("os.path.exists", return_value=True):

            async def side_effect(*args, **kwargs):
                cmd = args[0]
                process_mock = MagicMock()

                if cmd == "androguard":

                    async def communicate():
                        return b"This APK is packed with something", b""

                    process_mock.communicate = communicate
                    process_mock.returncode = 0
                    return process_mock

                if cmd == "apktool":
                    # args: "apktool", "d", "-f", "-q", "-o", temp_dir, file_path
                    temp_dir = args[5]
                    manifest_path = os.path.join(temp_dir, "AndroidManifest.xml")
                    os.makedirs(temp_dir, exist_ok=True)
                    with open(manifest_path, "w") as f:
                        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <application android:debuggable="true">
    </application>
</manifest>
""")

                    async def communicate():
                        return b"", b""

                    process_mock.communicate = communicate
                    process_mock.returncode = 0
                    return process_mock

                return process_mock

            mock_exec.side_effect = side_effect

            result = await scanner.scan("test.apk")

            assert result.scanner_name == "android"
            # We expect 3 findings: Obfuscation/Packer, Debuggable, and READ_EXTERNAL_STORAGE
            assert len(result.findings) == 3
            titles = [f.title for f in result.findings]
            assert "Obfuscation/Packer Detected" in titles
            assert "Android Debug Mode Enabled" in titles
            assert "Insecure Permissions: READ_EXTERNAL_STORAGE" in titles


@pytest.mark.asyncio
async def test_android_scanner_no_findings(mock_apktool_installed):
    scanner = AndroidScanner()

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        with patch("os.path.exists", return_value=True):

            async def side_effect(*args, **kwargs):
                cmd = args[0]
                process_mock = MagicMock()

                if cmd == "androguard":

                    async def communicate():
                        return b"Normal APK", b""

                    process_mock.communicate = communicate
                    process_mock.returncode = 0
                    return process_mock

                if cmd == "apktool":
                    # args: "apktool", "d", "-f", "-q", "-o", temp_dir, file_path
                    temp_dir = args[5]
                    manifest_path = os.path.join(temp_dir, "AndroidManifest.xml")
                    os.makedirs(temp_dir, exist_ok=True)
                    with open(manifest_path, "w") as f:
                        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:debuggable="false">
    </application>
</manifest>
""")

                    async def communicate():
                        return b"", b""

                    process_mock.communicate = communicate
                    process_mock.returncode = 0
                    return process_mock

                return process_mock

            mock_exec.side_effect = side_effect

            result = await scanner.scan("test.apk")

            assert result.scanner_name == "android"
            assert len(result.findings) == 0
