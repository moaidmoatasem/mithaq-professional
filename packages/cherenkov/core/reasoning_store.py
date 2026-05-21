from typing import List
from cherenkov.core.schemas.reasoning_trace import ReasoningTrace

class ReasoningStore:
    def __init__(self):
        self.traces: List[ReasoningTrace] = []

    def add_trace(self, trace: ReasoningTrace) -> None:
        self.traces.append(trace)

    def get_traces(self) -> List[ReasoningTrace]:
        return self.traces
