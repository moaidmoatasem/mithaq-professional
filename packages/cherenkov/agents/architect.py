"""Security Architect agent using Foundation-Sec-8B via LiteLLM.

Routes through the LiteLLM proxy (http://localhost:4000) per AGENTS.md §9.
Input is sanitized through ABLATION before reaching the model.
"""

import logging
from typing import Any

import litellm

from cherenkov.core.ablation import Sanitizer
from cherenkov.core.config.llm_config import LITELLM_PROXY_URL

logger = logging.getLogger(__name__)

FOUNDATION_SEC_MODEL = "architect"

SYSTEM_PROMPT = (
    "You are a Security Architect AI. Your role is to:\n"
    "1. Analyze security requirements and design secure architectures\n"
    "2. Perform threat modeling using STRIDE methodology\n"
    "3. Identify potential vulnerabilities and recommend mitigations\n"
    "4. Validate CVE relevance to specific systems\n"
    "5. Generate comprehensive security plans\n\n"
    "Provide structured, actionable recommendations."
)


class SecurityArchitect:
    """Security Architect agent powered by Foundation-Sec-8B via LiteLLM proxy."""

    def __init__(
        self,
        model: str = FOUNDATION_SEC_MODEL,
        proxy_url: str | None = None,
    ):
        self.model = model
        self.proxy_url = proxy_url or LITELLM_PROXY_URL
        self.ablation = Sanitizer()

    async def generate_plan(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate a security architecture plan.

        All user-supplied input is sanitized through ABLATION before
        reaching the LLM per the Sovereign Security Standard.

        Args:
            context: Dict containing target, requirements, constraints, etc.

        Returns:
            Dict with generated plan or error info.
        """
        sanitized_context = self._sanitize_context(context)
        prompt = self._build_prompt(sanitized_context)

        try:
            response = await litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=4096,
                api_base=self.proxy_url,
            )

            content = response.choices[0].message.content

            return {
                "status": "success",
                "plan": content,
                "model": self.model,
            }
        except Exception as exc:
            logger.error("SecurityArchitect.generate_plan failed: %s", exc)
            return {
                "status": "error",
                "error": str(exc),
                "model": self.model,
            }

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Sanitize user-supplied context through ABLATION.

        Redacts PII, credentials, internal paths, and other sensitive data
        before constructing the LLM prompt.
        """
        sanitized = dict(context)

        text_fields = ["target", "threat_context"]
        for field in text_fields:
            raw = sanitized.get(field, "")
            if isinstance(raw, str) and raw.strip():
                result = self.ablation.sanitize(raw)
                sanitized[field] = result.sanitized_text

        list_fields = ["requirements", "constraints"]
        for field in list_fields:
            items = sanitized.get(field, [])
            if isinstance(items, list):
                sanitized[field] = [
                    self.ablation.sanitize(item).sanitized_text if isinstance(item, str) else item
                    for item in items
                ]

        return sanitized

    def _build_prompt(self, context: dict[str, Any]) -> str:
        """Build structured prompt from request context."""
        sections = []

        target = context.get("target", "Unknown")
        sections.append(f"## Target System\n{target}")

        requirements = context.get("requirements", [])
        if requirements:
            sections.append(
                "## Security Requirements\n" + "\n".join(f"- {r}" for r in requirements)
            )

        constraints = context.get("constraints", [])
        if constraints:
            sections.append("## Constraints\n" + "\n".join(f"- {c}" for c in constraints))

        threat_context = context.get("threat_context", "")
        if threat_context:
            sections.append(f"## Threat Context\n{threat_context}")

        sections.append(
            "\nPlease generate a comprehensive security architecture plan including:\n"
            "- Threat model (STRIDE per component)\n"
            "- Architecture recommendations\n"
            "- Security controls and mitigations\n"
            "- Implementation priorities\n"
            "- CVE considerations if applicable"
        )

        return "\n\n".join(sections)
