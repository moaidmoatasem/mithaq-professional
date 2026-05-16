from datetime import datetime

from cherenkov.core.schemas.cherenkov_trace import CherenkovTrace


def test_cherenkov_trace_creation():
    trace = CherenkovTrace(trace_id="trace-123", target="target.com", mode="hybrid")
    assert trace.trace_id == "trace-123"
    assert trace.target == "target.com"
    assert trace.mode == "hybrid"
    assert isinstance(trace.timestamp, datetime)
