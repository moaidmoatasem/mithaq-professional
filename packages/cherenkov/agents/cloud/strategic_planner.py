"""
Cloud Strategic Planner Agent
Uses Groq Llama 3.1 70B for high-level threat modeling and task decomposition.
Never receives raw sensitive data - only abstract breadcrumbs.
"""

import os
from typing import Any, Dict, List, Optional

from groq import Groq
from pydantic import BaseModel, Field


class ThreatAnalysisTask(BaseModel):
    """Schema for threat analysis tasks sent to cloud"""

    target_type: str = Field(..., description="Type: web, mobile, infra")
    abstract_context: Dict = Field(..., description="Redacted metadata only")
    analysis_scope: List[str] = Field(..., description="Requested analysis types")


class StrategicPlanner:
    """
    Cloud-based strategic planner using Groq LLM.
    Handles high-level reasoning without accessing sensitive data.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        reasoning_store: Optional[Any] = None,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.session_id = session_id
        self.reasoning_store = reasoning_store
        self.use_local = False

        # Fallback for testing environments to allow offline tests to pass without GROQ_API_KEY
        if not self.api_key and "PYTEST_CURRENT_TEST" in os.environ:
            self.api_key = "mock_key"

        if not self.api_key:
            # Transition to offline/local-first mode using Ollama
            self.use_local = True
            from cherenkov.agents.local.ollama_client import OllamaClient, OllamaConfig
            from cherenkov.core.config.llm_config import DEFAULT_LLM_MODEL, OLLAMA_BASE_URL

            # Extract model name (e.g. "ollama/qwen2.5:3b" -> "qwen2.5:3b")
            model_name = (
                DEFAULT_LLM_MODEL.split("/")[-1] if "/" in DEFAULT_LLM_MODEL else DEFAULT_LLM_MODEL
            )
            config = OllamaConfig(base_url=OLLAMA_BASE_URL, model=model_name)
            self.local_client = OllamaClient(config=config)
            self.model = DEFAULT_LLM_MODEL
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
            self.model = "llama-3.3-70b-versatile"

    def plan_security_audit(self, task: ThreatAnalysisTask) -> Dict:
        """
        Generate high-level security audit plan.

        Args:
            task: Redacted task information

        Returns:
            Strategic audit plan with recommended steps
        """

        system_prompt = """You are a security architect planning audits.
You receive ONLY abstract, redacted information about targets.
Generate strategic reconnaissance plans without needing sensitive details.
Focus on methodology, not specific values."""

        user_prompt = f"""
Target Type: {task.target_type}
Context: {task.abstract_context}
Scope: {", ".join(task.analysis_scope)}

Create a strategic security audit plan with:
1. Threat modeling approach
2. Recommended analysis techniques
3. Priority vulnerability categories
4. Validation methods

Do NOT request raw data. Work with abstract patterns only.
"""

        if self.use_local:
            response = self.local_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )
            return {
                "plan": response.response,
                "model": self.model,
                "tokens_used": response.eval_count or 0,
            }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        return {
            "plan": response.choices[0].message.content,
            "model": self.model,
            "tokens_used": response.usage.total_tokens,
        }

    def decompose_task(self, high_level_goal: str, constraints: Dict) -> Dict:
        """
        Decompose high-level security goal into subtasks.

        Args:
            high_level_goal: Strategic objective
            constraints: Abstract constraints (no sensitive data)

        Returns:
            Subtasks for local execution
        """

        prompt = f"""
Security Goal: {high_level_goal}
Constraints: {constraints}

Break this into 3-5 specific subtasks that can be executed locally.
Each subtask should be:
- Self-contained
- Measurable
- Security-focused

Provide actionable steps without requiring sensitive data.
"""

        if self.use_local:
            response = self.local_client.generate(
                prompt=prompt,
                temperature=0.2,
            )
            return {"subtasks": response.response, "model": self.model}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024,
        )

        return {"subtasks": response.choices[0].message.content, "model": self.model}
