"""
Open Redirect Scanner - New Implementation
Detects open redirect vulnerabilities
"""

import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Dict, List


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
        print(f"[*] Scanning for open redirect: {self.target}")

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
                print("  [!] No redirect parameters found")
                return []

            # Test each redirect parameter
            for param in found_params:
                for redirect_target in self.REDIRECT_TARGETS:
                    test_url = self._inject_redirect(
                        self.target, param, redirect_target
                    )

                    try:
                        response = requests.get(
                            test_url, timeout=10, allow_redirects=False
                        )

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
                                print(f"  [!] FOUND open redirect in: {param}")
                                break

                    except requests.RequestException as e:
                        print(f"  [!] Request failed: {e}")
                        continue

        except Exception as e:
            print(f"  [!] Error: {e}")

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
        print("\n" + "=" * 70)
        print("🔍 OPEN REDIRECT SCANNER")
        print("=" * 70)

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

    if len(sys.argv) > 1:
        result = scan_open_redirect(sys.argv[1])
        print(
            f"\n✅ Scan complete. Found {result['count']} open redirect vulnerabilities"
        )
