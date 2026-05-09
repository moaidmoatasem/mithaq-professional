from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class MicroAgentConfig:
    role: str
    purpose: str
    tool_function: Callable[[str], Dict[str, Any]] = field(default=lambda ctx: {"status": "noop"})


class MicroAgent:
    def __init__(self, config: MicroAgentConfig):
        self.config = config

    def execute(self, context: str = "") -> Dict[str, Any]:
        return self.config.tool_function(context)
