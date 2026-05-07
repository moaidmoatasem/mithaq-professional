#!/usr/bin/env python3
"""
Enhanced mithaq Scanner with more checks
"""

from .header_scanner import SimpleScanner
import requests
from urllib.parse import urlparse, urljoin
import re


class FullScanner(SimpleScanner):
    """Extended scanner with more vulnerability checks"""

    def scan_cors(self):
        """Check CORS configuration"""
        print(f"\n[*] Checking CORS configuration")

        try:
            headers = {"Origin": "https://evil.com"}
            response = requests.get(self.target, headers=headers, timeout=10)

            if "Access-Control-Allow-Origin" in response.headers:
                origin = response.headers["Access-Control-Allow-Origin"]
                if origin == "*":
                    vuln = {
                        "type": "CORS Misconfiguration",
                        "severity": "High",
                        "description": "Access-Control-Allow-Origin is set to wildcard (*)",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    print(f"  [!] CORS allows ANY origin (*)")
                else:
                    print(f"  [✓] CORS configured: {origin}")
            else:
                print(f"  [✓] CORS not enabled")
        except Exception as e:
            print(f"  [!] Error: {e}")

    def scan_cookies(self):
        """Check cookie security"""
        print(f"\n[*] Checking cookie security")

        try:
            response = requests.get(self.target, timeout=10)

            if "Set-Cookie" in response.headers:
                cookies = response.headers["Set-Cookie"]

                if "Secure" not in cookies:
                    vuln = {
                        "type": "Insecure Cookie",
                        "severity": "Medium",
                        "description": "Cookies missing Secure flag",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    print(f"  [!] Cookies missing Secure flag")

                if "HttpOnly" not in cookies:
                    vuln = {
                        "type": "Insecure Cookie",
                        "severity": "Medium",
                        "description": "Cookies missing HttpOnly flag",
                    }
                    self.results["vulnerabilities"].append(vuln)
                    print(f"  [!] Cookies missing HttpOnly flag")

                if "SameSite" not in cookies:
                    print(f"  [!] Cookies missing SameSite attribute")
            else:
                print(f"  [✓] No cookies set")
        except Exception as e:
            print(f"  [!] Error: {e}")

    def scan_server_info(self):
        """Check for information disclosure"""
        print(f"\n[*] Checking for information disclosure")

        try:
            response = requests.get(self.target, timeout=10)

            if "Server" in response.headers:
                server = response.headers["Server"]
                vuln = {
                    "type": "Information Disclosure",
                    "severity": "Low",
                    "description": f"Server header disclosed: {server}",
                }
                self.results["vulnerabilities"].append(vuln)
                print(f"  [!] Server header exposed: {server}")
            else:
                print(f"  [✓] Server header hidden")

            if "X-Powered-By" in response.headers:
                powered = response.headers["X-Powered-By"]
                vuln = {
                    "type": "Information Disclosure",
                    "severity": "Low",
                    "description": f"X-Powered-By header disclosed: {powered}",
                }
                self.results["vulnerabilities"].append(vuln)
                print(f"  [!] X-Powered-By exposed: {powered}")
            else:
                print(f"  [✓] X-Powered-By header hidden")
        except Exception as e:
            print(f"  [!] Error: {e}")

    def run(self):
        """Run all scans including new ones"""
        print("=" * 70)
        print("🔍 mithaq FULL SECURITY SCANNER")
        print("=" * 70)

        self.scan_security_headers()
        self.scan_http_methods()
        self.scan_ssl_tls()
        self.scan_cors()
        self.scan_cookies()
        self.scan_server_info()
        self.generate_report()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        scanner = FullScanner(sys.argv[1])
        scanner.run()

