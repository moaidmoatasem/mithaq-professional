import httpx
from cherenkov.core.base_scanner import BaseScanner, Finding, ScanResult, Severity


class GitHubRepoAlignmentScanner(BaseScanner):
    """CWE-231: Improper Implementation - Alignment of GitHub repo description, tags, and homepage to project reality.

    Technique: Manual review of repository metadata. Ensure that the repository description, tags, and homepage accurately reflect the project's purpose and details.

    Remediation: Manually update the repository description, tags, and homepage to align with the project's reality."""

    scanner_tags = ["passive"]

    async def scan(self) -> ScanResult:
        findings = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.target)
                if response.status_code == 200:
                    repo_data = response.json()
                    description_match = (
                        repo_data["description"].lower().find("project reality") != -1
                    )
                    homepage_match = repo_data["homepage"].lower().find("project reality") != -1
                    tags_match = any(tag.lower() == "projectreality" for tag in repo_data["topics"])

                    if not (description_match and homepage_match and tags_match):
                        findings.append(
                            Finding(
                                severity=Severity.HIGH,
                                description="GitHub repo metadata does not align with project reality",
                                recommendation="Manually update repository description, tags, and homepage",
                            )
                        )
                else:
                    findings.append(
                        Finding(
                            severity=Severity.MEDIUM,
                            description=f"Failed to retrieve GitHub repo data. Status code: {response.status_code}",
                            recommendation="Check network connectivity and try again",
                        )
                    )
        except httpx.ConnectError as e:
            findings.append(
                Finding(
                    severity=Severity.HIGH,
                    description=f"Connection error: {e}",
                    recommendation="Check network connectivity and try again",
                )
            )
        except httpx.TimeoutException as e:
            findings.append(
                Finding(
                    severity=Severity.MEDIUM,
                    description=f"Request timed out: {e}",
                    recommendation="Increase timeout or check server performance",
                )
            )

        return ScanResult(failings=findings)
