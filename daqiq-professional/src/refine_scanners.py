#!/usr/bin/env python3
"""
Refine and fix AI-generated scanners
Creates production-ready versions
"""

from pathlib import Path

output_dir = Path("daqiq/scanners/refined")
output_dir.mkdir(exist_ok=True)

print("🔧 Refining AI-generated scanners...\n")

# 1. FIXED XSS SCANNER - Add HTTP scanning capability
xss_scanner_fixed = '''"""
XSS Scanner - Refined Version
Detects Cross-Site Scripting vulnerabilities
"""

import requests
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict


class XSSScanner:
    """Production XSS vulnerability scanner"""
    
    # Common XSS payloads for testing
    XSS_PAYLOADS = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        '"><script>alert(String.fromCharCode(88,83,83))</script>',
        '<svg/onload=alert("XSS")>',
        'javascript:alert("XSS")',
        '<iframe src="javascript:alert(\'XSS\')">',
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
                                'type': 'Reflected XSS',
                                'severity': 'High',
                                'parameter': param_name,
                                'payload': payload,
                                'url': test_url,
                                'description': f'XSS payload reflected in parameter: {param_name}'
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
        print(f"[*] Checking for DOM XSS indicators")
        
        try:
            response = requests.get(self.target, timeout=10)
            content = response.text
            
            # Look for dangerous JavaScript patterns
            dangerous_patterns = [
                r'document\.write\(',
                r'innerHTML\s*=',
                r'eval\(',
                r'\.location\s*=',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vuln = {
                        'type': 'Potential DOM XSS',
                        'severity': 'Medium',
                        'pattern': pattern,
                        'description': f'Dangerous JavaScript pattern found: {pattern}'
                    }
                    self.vulnerabilities.append(vuln)
                    print(f"  [!] Found dangerous pattern: {pattern}")
        
        except Exception as e:
            print(f"  [!] Error: {e}")
        
        return self.vulnerabilities
    
    def run(self) -> Dict:
        """Run all XSS scans"""
        print("\\n" + "="*70)
        print("🔍 XSS VULNERABILITY SCANNER")
        print("="*70)
        
        self.scan_reflected_xss()
        self.scan_dom_xss()
        
        return {
            'target': self.target,
            'vulnerabilities': self.vulnerabilities,
            'count': len(self.vulnerabilities)
        }


def scan_xss(url: str) -> Dict:
    """Quick scan function"""
    scanner = XSSScanner(url)
    return scanner.run()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = scan_xss(sys.argv[1])
        print(f"\\n✅ Scan complete. Found {result['count']} potential XSS vulnerabilities")
'''

# 2. FIXED CSRF SCANNER
csrf_scanner_fixed = '''"""
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
            forms = re.findall(r'<form[^>]*>', content, re.IGNORECASE)
            
            if not forms:
                print("  [!] No forms found")
                return []
            
            print(f"  [*] Found {len(forms)} form(s)")
            
            # Check each form for CSRF tokens
            for i, form in enumerate(forms, 1):
                has_csrf = self._check_form_csrf_token(form, content)
                
                if not has_csrf:
                    vuln = {
                        'type': 'Missing CSRF Token',
                        'severity': 'High',
                        'form_number': i,
                        'description': f'Form {i} missing CSRF protection token'
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
            r'csrf[_-]?token',
            r'_token',
            r'authenticity[_-]?token',
            r'__RequestVerificationToken',
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
            
            if 'Set-Cookie' in response.headers:
                cookies = response.headers['Set-Cookie']
                
                if 'SameSite' not in cookies:
                    vuln = {
                        'type': 'Missing SameSite Cookie Attribute',
                        'severity': 'Medium',
                        'description': 'Cookies missing SameSite attribute (CSRF protection)'
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
        print("\\n" + "="*70)
        print("🔍 CSRF VULNERABILITY SCANNER")
        print("="*70)
        
        self.scan_csrf_tokens()
        self.scan_samesite_cookies()
        
        return {
            'target': self.target,
            'vulnerabilities': self.vulnerabilities,
            'count': len(self.vulnerabilities)
        }


def scan_csrf(url: str) -> Dict:
    """Quick scan function"""
    scanner = CSRFScanner(url)
    return scanner.run()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = scan_csrf(sys.argv[1])
        print(f"\\n✅ Scan complete. Found {result['count']} CSRF vulnerabilities")
'''

# 3. NEW OPEN REDIRECT SCANNER (AI got this wrong)
open_redirect_scanner_fixed = '''"""
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
        'http://evil.com',
        'https://attacker.com',
        '//evil.com',
        'javascript:alert(1)',
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
            redirect_params = ['url', 'redirect', 'next', 'return', 'returnTo', 
                             'goto', 'target', 'destination', 'redir', 'redirect_uri']
            
            # Check if any redirect parameters exist
            found_params = [p for p in redirect_params if p in params]
            
            if not found_params:
                print("  [!] No redirect parameters found")
                return []
            
            # Test each redirect parameter
            for param in found_params:
                for redirect_target in self.REDIRECT_TARGETS:
                    test_url = self._inject_redirect(self.target, param, redirect_target)
                    
                    try:
                        response = requests.get(test_url, timeout=10, allow_redirects=False)
                        
                        # Check if redirect occurs
                        if response.status_code in [301, 302, 303, 307, 308]:
                            location = response.headers.get('Location', '')
                            
                            if redirect_target in location or 'evil.com' in location:
                                vuln = {
                                    'type': 'Open Redirect',
                                    'severity': 'Medium',
                                    'parameter': param,
                                    'redirect_to': location,
                                    'test_url': test_url,
                                    'description': f'Open redirect in parameter: {param}'
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
        print("\\n" + "="*70)
        print("🔍 OPEN REDIRECT SCANNER")
        print("="*70)
        
        self.scan_redirect_parameters()
        
        return {
            'target': self.target,
            'vulnerabilities': self.vulnerabilities,
            'count': len(self.vulnerabilities)
        }


def scan_open_redirect(url: str) -> Dict:
    """Quick scan function"""
    scanner = OpenRedirectScanner(url)
    return scanner.run()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = scan_open_redirect(sys.argv[1])
        print(f"\\n✅ Scan complete. Found {result['count']} open redirect vulnerabilities")
'''

# Write refined scanners
scanners = {
    "xss_scanner.py": xss_scanner_fixed,
    "csrf_scanner.py": csrf_scanner_fixed,
    "open_redirect_scanner.py": open_redirect_scanner_fixed,
}

for filename, code in scanners.items():
    filepath = output_dir / filename
    with open(filepath, "w") as f:
        f.write(code)
    print(f"✅ Created: {filepath}")

print("\n" + "=" * 70)
print("✅ Refined scanners created!")
print("=" * 70)
print(f"📁 Location: {output_dir}/")
print("\nTest them:")
for filename in scanners.keys():
    print(f"  python {output_dir}/{filename} https://example.com")
