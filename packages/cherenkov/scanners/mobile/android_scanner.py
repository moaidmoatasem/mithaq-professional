"""Android Scanner"""

import asyncio
import logging
import os
import shutil
import tempfile
from typing import List

import defusedxml.ElementTree as ET  # noqa: N817

from cherenkov.core.base_scanner import Finding, Severity
from cherenkov.core.mobile_scanner import MobileScanner

logger = logging.getLogger(__name__)


class AndroidScanner(MobileScanner):
    """Scanner for Android APK files using static analysis logic with apktool and androguard."""

    def __init__(self, target: str = "", timeout: float = 10.0):
        super().__init__(name="android", description="Android APK static analysis scanner")

    async def scan_file(self, file_path: str) -> List[Finding]:
        """Perform static analysis on an APK file using apktool and androguard."""
        findings = []

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"APK file not found: {file_path}")

<<<<<<< HEAD
        # Mock finding: Debug mode enabled
        findings.append(
            Finding(
                title="Android Debug Mode Enabled",
                severity=Severity.HIGH,
                description="The APK has 'android:debuggable=true' in AndroidManifest.xml.",
                cwe="CWE-489",
                remediation="Set 'android:debuggable=false' in the manifest before production release.",
                scanner="drozer_exploit",
            )
        )
=======
        findings.extend(await self._run_androguard(file_path))
>>>>>>> main

        findings.extend(await self._run_apktool(file_path))

        return findings

    async def _run_androguard(self, file_path: str) -> List[Finding]:
        findings = []
        if not shutil.which("androguard"):
            logger.warning("androguard is not installed, skipping androguard analysis")
            return findings

        try:
            process = await asyncio.create_subprocess_exec(
                "androguard",
                "apkid",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.warning("androguard execution timed out")
                return findings

            output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
            if (
                "obfuscated" in output.lower()
                or "packed" in output.lower()
                or "packer" in output.lower()
            ):
                findings.append(
                    Finding(
                        title="Obfuscation/Packer Detected",
                        severity=Severity.INFO,
                        description="Androguard detected that the APK is packed or obfuscated.",
                        cwe="CWE-693",
                        remediation="Ensure this is intended to protect IP, or investigate if it's hiding malicious behavior.",
                    )
                )
        except Exception as e:
            logger.warning("androguard execution failed: %s", e)

        return findings

    async def _run_apktool(self, file_path: str) -> List[Finding]:
        findings = []
        if not shutil.which("apktool"):
            logger.warning("apktool is not installed, skipping manifest analysis")
            return findings

        temp_dir = tempfile.mkdtemp(prefix="apktool_")

        try:
            process = await asyncio.create_subprocess_exec(
                "apktool",
                "d",
                "-f",
                "-q",
                "-o",
                temp_dir,
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.warning("apktool execution timed out")
                return findings

            if process.returncode != 0:
                logger.warning(
                    "apktool failed to decode APK: %s", stderr.decode() if stderr else ""
                )
                return findings

            manifest_path = os.path.join(temp_dir, "AndroidManifest.xml")
            if os.path.exists(manifest_path):
                findings.extend(self._parse_manifest(manifest_path))

        except Exception as e:
            logger.warning("apktool execution failed: %s", e)
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.debug("Failed to remove temp dir %s: %s", temp_dir, e)

        return findings

    def _parse_manifest(self, manifest_path: str) -> List[Finding]:
        findings = []
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # The Android namespace is usually required to access attributes
            ns = {"android": "http://schemas.android.com/apk/res/android"}

            # Check debuggable
            application = root.find("application")
            if application is not None:
                debuggable = application.attrib.get(f"{{{ns['android']}}}debuggable")
                if debuggable == "true":
                    findings.append(
                        Finding(
                            title="Android Debug Mode Enabled",
                            severity=Severity.HIGH,
                            description="The APK has 'android:debuggable=true' in AndroidManifest.xml.",
                            cwe="CWE-489",
                            remediation="Set 'android:debuggable=false' in the manifest before production release.",
                        )
                    )

            # Check permissions
            for perm in root.findall("uses-permission"):
                name = perm.attrib.get(f"{{{ns['android']}}}name", "")
                if name == "android.permission.READ_EXTERNAL_STORAGE":
                    findings.append(
                        Finding(
                            title="Insecure Permissions: READ_EXTERNAL_STORAGE",
                            severity=Severity.LOW,
                            description="The app requests READ_EXTERNAL_STORAGE, which may expose sensitive user data.",
                            cwe="CWE-276",
                            remediation="Only request necessary permissions and use Scoped Storage where possible.",
                        )
                    )
        except Exception as e:
            logger.warning("Failed to parse AndroidManifest.xml: %s", e)

        return findings
