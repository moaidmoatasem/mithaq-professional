"""
Open Redirect Scanner - New Implementation
Detects open redirect vulnerabilities
"""

from typing import Dict, List
import logging
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

logger = logging.getLogger(__name__)


class OpenRedirectScanner:
    """Production open redirect vulnerability scanner"""

    # Test redirect targets
    REDIRECT_TARGETS = [
        "http://evil.com",
        "https://attacker.com",
        "//evil.com",
        "javascript:alert(1)",
    ]

    def __init__(self, target_url: str):
        self.target = target_url
        self.vulnerabilities = []

    def scan_redirect_parameters(self) -> List[Dict]:
        """Test URL parameters for open redirects"""
        logger.info("[*] Scanning for open redirect: %s", self.target)

        try:
            parsed = urlparse(self.target)
            params = parse_qs(parsed.query)

            # Common redirect parameter names
            redirect_params = [
                "url",
                "redirect",
                "next",
                "return",
                "returnTo",
                "goto",
                "target",
                "destination",
                "redir",
                "redirect_uri",
            ]

            # Check if any redirect parameters exist
            found_params = [p for p in redirect_params if p in params]

            if not found_params:
                logger.info("  [!] No redirect parameters found")
                return []

            # Test each redirect parameter
            for param in found_params:
                for redirect_target in self.REDIRECT_TARGETS:
                    test_url = self._inject_redirect(self.target, param, redirect_target)

                    try:
                        response = requests.get(test_url, timeout=10, allow_redirects=False)

                        # Check if redirect occurs
                        if response.status_code in [301, 302, 303, 307, 308]:
                            location = response.headers.get("Location", "")

                            if redirect_target in location or "evil.com" in location:
                                vuln = {
                                    "type": "Open Redirect",
                                    "severity": "Medium",
                                    "parameter": param,
                                    "redirect_to": location,
                                    "test_url": test_url,
                                    "description": f"Open redirect in parameter: {param}",
                                }
                                self.vulnerabilities.append(vuln)
                                logger.warning("  [!] FOUND open redirect in: %s", param)
                                break

                    except requests.RequestException as e:
                        logger.error("  [!] Request failed: %s", e)
                        continue

        except Exception as e:
            logger.error("  [!] Error: %s", e)

        return self.vulnerabilities

    def _inject_redirect(self, url: str, param: str, target: str) -> str:
        """Inject redirect target into URL parameter"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params[param] = [target]

        new_query = urlencode(params, doseq=True)
        new_parsed = parsed._replace(query=new_query)

        return urlunparse(new_parsed)

    def run(self) -> Dict:
        """Run open redirect scan"""
        logger.info("\n" + "=" * 70)
        logger.info("🔍 OPEN REDIRECT SCANNER")
        logger.info("=" * 70)

        self.scan_redirect_parameters()

        return {
            "target": self.target,
            "vulnerabilities": self.vulnerabilities,
            "count": len(self.vulnerabilities),
        }


def scan_open_redirect(url: str) -> Dict:
    """Quick scan function"""
    scanner = OpenRedirectScanner(url)
    return scanner.run()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if len(sys.argv) > 1:
        result = scan_open_redirect(sys.argv[1])
        logger.info("\n✅ Scan complete. Found %d open redirect vulnerabilities", result['count'])
