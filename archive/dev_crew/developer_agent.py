# packages/cherenkov/dev_crew/developer_agent.py
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
CODER_MODEL = "qwen2.5-coder:7b" # High performance for Python

class LocalDeveloper:
    def __init__(self):
        self.system_prompt = """
        You are a Senior Python Engineer working on CHERENKOV.
        You receive strict specifications from the Architect.
        You output ONLY complete, working Python code. 
        No markdown, no explanations, no chat. Only code.
        """

    async def write_code(self, architect_task: dict) -> str:
        """Executes the task defined by the Architect."""
        prompt = f"Implement this spec exactly: {architect_task}"

        payload = {
            "model": CODER_MODEL,
            "system": self.system_prompt,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            return response.json()["response"]
