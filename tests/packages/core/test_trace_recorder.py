from cherenkov.core.schemas.cherenkov_trace import CherenkovTrace
from cherenkov.core.trace_recorder import TraceRecorder


def test_trace_recorder(tmp_path):
    log_file = tmp_path / "test_traces.jsonl"
    recorder = TraceRecorder(trace_log_path=str(log_file))

    trace = CherenkovTrace(trace_id="test-trace", target="127.0.0.1", mode="local_only")

    recorder.record_trace(trace)

    assert log_file.exists()
    content = log_file.read_text()
    assert "test-trace" in content
    assert "127.0.0.1" in content
    assert "local_only" in content
