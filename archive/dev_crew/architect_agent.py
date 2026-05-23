# packages/cherenkov/dev_crew/architect_agent.py
import json

import httpx
from cherenkov.dev_crew.session_manager import get_ssot_context

OLLAMA_URL = "http://localhost:11434/api/generate"
ARCHITECT_MODEL = "llama3.2:3b" # Good for reasoning and PMO tasks

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
        2. Keep it scoped so a local 7B coder model can execute it.
        3. Do NOT write the code yourself. Write the specification.
        """

    async def get_next_directive(self, current_focus: str) -> dict:
        """Asks the local Ollama PMO for the next engineering task."""
        prompt = f"Based on our SSOT, what is the exact specification to build: {current_focus}?"

        payload = {
            "model": ARCHITECT_MODEL,
            "system": self.system_prompt,
            "prompt": prompt,
            "format": "json", # Force JSON output for pipeline automation
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()["response"]
            return json.loads(result)

# Example Usage:
# import asyncio
# architect = LocalArchitect()
# task = asyncio.run(architect.get_next_directive("The SQLite WAL initialization module"))
# print(task)
