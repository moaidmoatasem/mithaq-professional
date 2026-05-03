"""
CSRF Scanner - Refined Version
Detects Cross-Site Request Forgery vulnerabilities
"""

import requests
from typing import Dict, List
import re


class CSRFScanner:
    """Production CSRF vulnerability scanner"""

    def __init__(self, target_url: str):
        self.target = target_url
        self.vulnerabilities = []

    def scan_csrf_tokens(self) -> List[Dict]:
        """Check for CSRF token protection"""
        print(f"[*] Scanning for CSRF protection: {self.target}")

        try:
            response = requests.get(self.target, timeout=10)
            content = response.text

            # Look for forms
            forms = re.findall(r"<form[^>]*>", content, re.IGNORECASE)

            if not forms:
                print("  [!] No forms found")
                return []

            print(f"  [*] Found {len(forms)} form(s)")

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
                    print(f"  [!] Form {i} has NO CSRF token")
                else:
                    print(f"  [✓] Form {i} has CSRF protection")

        except Exception as e:
            print(f"  [!] Error: {e}")

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
        print(f"[*] Checking SameSite cookie protection")

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
                    print(f"  [!] Cookies missing SameSite attribute")
                else:
                    print(f"  [✓] SameSite cookie protection enabled")
            else:
                print(f"  [*] No cookies set")

        except Exception as e:
            print(f"  [!] Error: {e}")

        return self.vulnerabilities

    def run(self) -> Dict:
        """Run all CSRF scans"""
        print("\n" + "=" * 70)
        print("🔍 CSRF VULNERABILITY SCANNER")
        print("=" * 70)

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

    if len(sys.argv) > 1:
        result = scan_csrf(sys.argv[1])
        print(f"\n✅ Scan complete. Found {result['count']} CSRF vulnerabilities")
