import json

import httpx

from cherenkov.dev_crew.session_manager import get_ssot_context

OLLAMA_URL = "http://localhost:11434/api/generate"
ARCHITECT_MODEL = "llama3.2:3b"


class LocalArchitect:
    def __init__(self):
        self.context = get_ssot_context()
        self.system_prompt = f"""
        You are the Technical Architect and PMO for CHERENKOV.
        Your job is to read the current state, identify the next most critical missing piece
        based on the priorities, and output a strict, actionable JSON task for the Developer Agent.

        CURRENT PROJECT STATE (SSOT):
        {self.context}

        RULES:
        1. Only assign ONE task at a time.
        2. Keep it scoped so a local 3B coder model can execute it.
        3. Do NOT write the code yourself. Write the specification.
        4. Output ONLY valid JSON with keys: task_name, file_path, description, acceptance_criteria.
        """

    async def get_next_directive(self, current_focus: str) -> dict:
        """Asks the local Ollama PMO for the next engineering task."""
        prompt = f"Based on our SSOT, what is the exact specification to build: {current_focus}?"

        payload = {
            "model": ARCHITECT_MODEL,
            "system": self.system_prompt,
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()["response"]
            return json.loads(result)
