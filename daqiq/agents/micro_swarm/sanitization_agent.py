"""
Sanitization Gatekeeper - Ultra-fast PII/secret scrubber
"""
import re
from typing import Dict

def scrub_secrets(text: str) -> Dict[str, str]:
    """
    Fast semantic sanitization
    Removes: API keys, paths, IPs, emails, tokens
    """
    sanitized = text
    redactions = []
    
    # Patterns
    patterns = {
        'api_key': r'[A-Za-z0-9]{32,}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ipv4': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'file_path': r'/[a-zA-Z0-9_\-./]+',
        'jwt': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'
    }
    
    for name, pattern in patterns.items():
        matches = re.findall(pattern, sanitized)
        if matches:
            redactions.extend([(name, m) for m in matches])
            sanitized = re.sub(pattern, f'[REDACTED_{name.upper()}]', sanitized)
    
    return {
        'sanitized_text': sanitized,
        'redactions': redactions,
        'redaction_count': len(redactions)
    }
