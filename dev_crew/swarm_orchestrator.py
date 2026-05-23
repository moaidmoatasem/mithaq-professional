# packages/cherenkov/dev_crew/swarm_orchestrator.py
import re
from pathlib import Path
from cherenkov.dev_crew.architect_agent import LocalArchitect
from cherenkov.dev_crew.developer_agent import LocalDeveloper
from cherenkov.dev_crew.validation_gate import ValidationGate

MAX_ITERATIONS = 3

class AutonomousSprint:
    def __init__(self, focus_area: str, target_filepath: str):
        self.focus_area = focus_area
        self.target_file = Path(target_filepath)
        self.architect = LocalArchitect()
        self.developer = LocalDeveloper()
        self.validation_gate = ValidationGate(self.target_file)

    def extract_code(self, raw_llm_output: str) -> str:
        """Strips markdown formatting from the Developer's output."""
        match = re.search(r'```python\n(.*?)\n```', raw_llm_output, re.DOTALL)
        return match.group(1) if match else raw_llm_output

    async def execute_sprint(self):
        print(f"🚀 INITIATING SPRINT: {self.focus_area}")

        # Step 1: Architect generates the spec
        print("🧠 Architect is analyzing SSOT and drafting specification...")
        spec = await self.architect.get_next_directive(self.focus_area)
        print(f"📋 Spec Generated: {spec.get('task_name', 'Unnamed Task')}")

        iteration = 0
        current_feedback = ""

        # Step 2: The Code/Validate Loop
        while iteration < MAX_ITERATIONS:
            iteration += 1
            print(f"\n💻 Developer Iteration {iteration}/{MAX_ITERATIONS}...")

            # Inject feedback if this is a retry
            task_prompt = spec
            if current_feedback:
                task_prompt["previous_failure_feedback"] = current_feedback

            raw_code = await self.developer.write_code(task_prompt)
            clean_code = self.extract_code(raw_code)

            # Write code to disk
            self.target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write(clean_code)

            # Step 3: Run Validation Gate
            print("🛡️ Running Validation Gate (Ruff/Pytest)...")
            val_result = self.validation_gate.run_checks()

            if val_result.passed:
                print("✅ SPRINT SUCCESSFUL. Code committed to disk.")
                # Future: Trigger SSOT update here
                return True
            else:
                print(f"❌ VALIDATION FAILED. Feeding errors back to Developer.")
                current_feedback = val_result.feedback

        print("🛑 CIRCUIT BREAKER TRIPPED. Max iterations reached. Human intervention required.")
        return False