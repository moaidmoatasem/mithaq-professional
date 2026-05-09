"""
XSS Scanner - Refined Version
Detects Cross-Site Scripting vulnerabilities
"""

import re
from typing import Dict, List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests


class XSSScanner:
    """Production XSS vulnerability scanner"""

    # Common XSS payloads for testing
    XSS_PAYLOADS = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        '"><script>alert(String.fromCharCode(88,83,83))</script>',
        '<svg/onload=alert("XSS")>',
        'javascript:alert("XSS")',
        "<iframe src=\"javascript:alert('XSS')\">",
    ]

    def __init__(self, target_url: str):
        self.target = target_url
        self.vulnerabilities = []

    def scan_reflected_xss(self) -> List[Dict]:
        """Test for reflected XSS in URL parameters"""
        print(f"[*] Scanning for reflected XSS: {self.target}")

        try:
            parsed = urlparse(self.target)
            params = parse_qs(parsed.query)

            if not params:
                print("  [!] No parameters found to test")
                return []

            # Test each parameter with XSS payloads
            for param_name in params.keys():
                for payload in self.XSS_PAYLOADS:
                    test_url = self._inject_payload(self.target, param_name, payload)

                    try:
                        response = requests.get(test_url, timeout=10)

                        # Check if payload is reflected in response
                        if payload in response.text:
                            vuln = {
                                "type": "Reflected XSS",
                                "severity": "High",
                                "parameter": param_name,
                                "payload": payload,
                                "url": test_url,
                                "description": f"XSS payload reflected in parameter: {param_name}",
                            }
                            self.vulnerabilities.append(vuln)
                            print(f"  [!] FOUND XSS in parameter: {param_name}")
                            break  # One payload is enough per parameter

                    except requests.RequestException as e:
                        print(f"  [!] Request failed: {e}")
                        continue

        except Exception as e:
            print(f"  [!] Error: {e}")

        return self.vulnerabilities

    def _inject_payload(self, url: str, param: str, payload: str) -> str:
        """Inject XSS payload into URL parameter"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params[param] = [payload]

        new_query = urlencode(params, doseq=True)
        new_parsed = parsed._replace(query=new_query)

        return urlunparse(new_parsed)

    def scan_dom_xss(self) -> List[Dict]:
        """Check for DOM-based XSS indicators"""
        print("[*] Checking for DOM XSS indicators")

        try:
            response = requests.get(self.target, timeout=10)
            content = response.text

            # Look for dangerous JavaScript patterns
            dangerous_patterns = [
                r"document\.write\(",
                r"innerHTML\s*=",
                r"eval\(",
                r"\.location\s*=",
            ]

            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vuln = {
                        "type": "Potential DOM XSS",
                        "severity": "Medium",
                        "pattern": pattern,
                        "description": f"Dangerous JavaScript pattern found: {pattern}",
                    }
                    self.vulnerabilities.append(vuln)
                    print(f"  [!] Found dangerous pattern: {pattern}")

        except Exception as e:
            print(f"  [!] Error: {e}")

        return self.vulnerabilities

    def run(self) -> Dict:
        """Run all XSS scans"""
        print("\n" + "=" * 70)
        print("🔍 XSS VULNERABILITY SCANNER")
        print("=" * 70)

        self.scan_reflected_xss()
        self.scan_dom_xss()

        return {
            "target": self.target,
            "vulnerabilities": self.vulnerabilities,
            "count": len(self.vulnerabilities),
        }


def scan_xss(url: str) -> Dict:
    """Quick scan function"""
    scanner = XSSScanner(url)
    return scanner.run()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = scan_xss(sys.argv[1])
        print(f"\n✅ Scan complete. Found {result['count']} potential XSS vulnerabilities")
