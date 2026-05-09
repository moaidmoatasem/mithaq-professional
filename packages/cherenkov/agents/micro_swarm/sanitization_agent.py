from typing import Any, Dict

from cherenkov.core.ablation.sanitizer import Sanitizer


class SanitizationAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sanitizer = Sanitizer()

    def sanitize(self, text: str) -> Dict[str, Any]:
        result = self.sanitizer.sanitize(text)
        return {
            "sanitized_text": result.sanitized_text,
            "secrets_found": result.secrets_found,
            "sanitization_applied": result.sanitization_applied,
        }
