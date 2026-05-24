#!/usr/bin/env python3
"""
CHERENKOV — ABLATION Pre-Inference Redaction Layer
Provides regex-based sanitization and redaction mechanisms to protect sensitive data
(passwords, secrets, emails, and cryptographic keys) before passing source code to LLMs.
"""

import re
import logging
from typing import Set

logger = logging.getLogger("CherenkovAblation")

# ── Redaction Patterns ────────────────────────────────────────────────────────
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

# Detect private key blocks
PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+ PRIVATE KEY-----"
)

# Detect high-entropy credential assignments in source code.
# Examples: PASSWORD = "...", db_pass = '...', api_key = "..."
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pass|pwd|secret|token|auth|credential|api_key|private_key|db_password)\b\s*=\s*(['\"])(.*?)\2"
)

# JWT pattern
JWT_PATTERN = re.compile(
    r"\beyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9\.[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+\b"
)


class AblationSanitizer:
    """Pre-inference sanitization engine enforcing strict data leakage prevention."""

    @staticmethod
    def redact_emails(text: str) -> str:
        """Replace emails with a safe redacted token."""
        return EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)

    @staticmethod
    def redact_private_keys(text: str) -> str:
        """Replace cryptographic private keys with a safe redacted token."""
        return PRIVATE_KEY_PATTERN.sub("[REDACTED_PRIVATE_KEY]", text)

    @staticmethod
    def redact_secret_assignments(text: str) -> str:
        """Replace hardcoded passwords and API keys in variable assignments."""
        def replace_secret(match):
            var_name = match.group(1)
            quote = match.group(2)
            val = match.group(3)
            
            # Skip very short variables or empty assignments to avoid false positives
            if len(val) <= 2:
                return match.group(0)
                
            return f"{var_name} = {quote}[REDACTED_{var_name.upper()}]{quote}"

        return SECRET_ASSIGNMENT_PATTERN.sub(replace_secret, text)

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Performs all configured sanitization steps sequentially."""
        if not text:
            return ""

        original_len = len(text)
        
        # 1. Redact Private Keys
        text = cls.redact_private_keys(text)
        
        # 2. Redact emails
        text = cls.redact_emails(text)
        
        # 3. Redact variable assignments of secrets
        text = cls.redact_secret_assignments(text)
        
        # 4. Redact JWT tokens
        text = JWT_PATTERN.sub("[REDACTED_JWT_TOKEN]", text)

        logger.debug(f"Sanitization completed. Length change: {original_len} -> {len(text)}")
        return text


if __name__ == "__main__":
    # Small self-test
    test_code = """
    import os
    
    DB_PASSWORD = "SovereignSecurityKey2026!#"
    admin_email = "moaid@cherenkov.security"
    jwt_secret = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdWIiOiAiMTIzNDU2Nzg5MCIsICJuYW1lIjogIkpvaG4gRG9lIiwgImFkbWluIjogdHJ1ZX0.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
    
    key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0123...\n-----END RSA PRIVATE KEY-----"
    """
    
    print("--- Original ---")
    print(test_code)
    print("\n--- Sanitized ---")
    print(AblationSanitizer.sanitize(test_code))
