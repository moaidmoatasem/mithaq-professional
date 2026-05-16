"""
CSRF Scanner - Refined Version
Detects Cross-Site Request Forgery vulnerabilities
"""

import logging
import re
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class CSRFScanner:
    """Production CSRF vulnerability scanner"""

    def __init__(self, target_url: str):
        self.target = target_url
        self.vulnerabilities = []

    def scan_csrf_tokens(self) -> List[Dict]:
        """Check for CSRF token protection"""
        logger.info("[*] Scanning for CSRF protection: %s", self.target)

        try:
            response = requests.get(self.target, timeout=10)
            content = response.text

            # Look for forms
            forms = re.findall(r"<form[^>]*>", content, re.IGNORECASE)

            if not forms:
                logger.info("  [!] No forms found")
                return []

            logger.info("  [*] Found %d form(s)", len(forms))

            # Check each form for CSRF tokens
            for i, form in enumerate(forms, 1):
                has_csrf = self._check_form_csrf_token(form, content)

                if not has_csrf:
                    vuln = {
                        "type": "Missing CSRF Token",
                        "severity": "High",
                        "form_number": i,
                        "description": f"Form {i} missing CSRF protection token",
                    }
                    self.vulnerabilities.append(vuln)
                    logger.warning("  [!] Form %d has NO CSRF token", i)
                else:
                    logger.info("  [✓] Form %d has CSRF protection", i)

        except Exception as e:
            logger.error("  [!] Error: %s", e)

        return self.vulnerabilities

    def _check_form_csrf_token(self, form: str, content: str) -> bool:
        """Check if form has CSRF token"""
        csrf_patterns = [
            r"csrf[_-]?token",
            r"_token",
            r"authenticity[_-]?token",
            r"__RequestVerificationToken",
        ]

        for pattern in csrf_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def scan_samesite_cookies(self) -> List[Dict]:
        """Check for SameSite cookie attribute"""
        logger.info("[*] Checking SameSite cookie protection")

        try:
            response = requests.get(self.target, timeout=10)

            if "Set-Cookie" in response.headers:
                cookies = response.headers["Set-Cookie"]

                if "SameSite" not in cookies:
                    vuln = {
                        "type": "Missing SameSite Cookie Attribute",
                        "severity": "Medium",
                        "description": "Cookies missing SameSite attribute (CSRF protection)",
                    }
                    self.vulnerabilities.append(vuln)
                    logger.warning("  [!] Cookies missing SameSite attribute")
                else:
                    logger.info("  [✓] SameSite cookie protection enabled")
            else:
                logger.info("  [*] No cookies set")

        except Exception as e:
            logger.error("  [!] Error: %s", e)

        return self.vulnerabilities

    def run(self) -> Dict:
        """Run all CSRF scans"""
        logger.info("\n" + "=" * 70)
        logger.info("🔍 CSRF VULNERABILITY SCANNER")
        logger.info("=" * 70)

        self.scan_csrf_tokens()
        self.scan_samesite_cookies()

        return {
            "target": self.target,
            "vulnerabilities": self.vulnerabilities,
            "count": len(self.vulnerabilities),
        }


def scan_csrf(url: str) -> Dict:
    """Quick scan function"""
    scanner = CSRFScanner(url)
    return scanner.run()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if len(sys.argv) > 1:
        result = scan_csrf(sys.argv[1])
        logger.info("\n✅ Scan complete. Found %d CSRF vulnerabilities", result["count"])
