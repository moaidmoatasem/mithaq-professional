import json
import re
from dataclasses import dataclass

from cherenkov.ai.lattice_bridge import query_similar_targets
from cherenkov.core.ai.model_router import ModelRouter


@dataclass
class EngagementPlan:
    target: str
    threat_surface: list[str]  # attack vectors identified
    red_team_tasks: list[dict]  # for offensive agent
    secops_tasks: list[dict]  # for compliance agent
    compliance_framework: str  # EGY-FIN CSF, SAMA CSF, etc.
    risk_score: int  # 0-100
    reasoning_trace: str  # LLM reasoning chain


class SecurityArchitect:
    def __init__(self):
        self.router = ModelRouter()

    async def plan_engagement(self, target: str, framework: str = "egyfincsf") -> EngagementPlan:
        # Query historical context from LATTICE
        history = await query_similar_targets(target, limit=5)

        # Build reasoning prompt
        prompt = f"""
You are a senior security architect planning a penetration test.

Target: {target}
Compliance framework: {framework}
Historical findings on similar targets: {history}

Produce a structured engagement plan with:
1. threat_surface (list of string attack vectors)
2. red_team_tasks (list of dicts representing offensive testing priorities)
3. secops_tasks (list of dicts representing compliance and hardening checks)
4. risk_score (integer 0-100)
5. reasoning_trace (string, reasoning for decisions)

Respond in JSON only. Do not include markdown formatting or extra text.
The JSON should have keys: "target", "threat_surface", "red_team_tasks", "secops_tasks", "compliance_framework", "risk_score", "reasoning_trace".
"""
        # Route to deepseek-r1 for reasoning (local)
        response_text = await self.router.complete(prompt)

        # Clean up possible markdown backticks
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
        else:
            json_str = response_text.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback if the LLM didn't return valid JSON
            data = {
                "target": target,
                "threat_surface": [],
                "red_team_tasks": [],
                "secops_tasks": [],
                "compliance_framework": framework,
                "risk_score": 0,
                "reasoning_trace": response_text,
            }

        # Ensure target and framework are in the data to match EngagementPlan
        if "target" not in data:
            data["target"] = target
        if "compliance_framework" not in data:
            data["compliance_framework"] = framework

        return EngagementPlan(**data)
