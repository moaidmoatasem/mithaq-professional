import logging

from .schemas.cherenkov_trace import CherenkovTrace

logger = logging.getLogger(__name__)


class TraceRecorder:
    """Trace Recorder & State Engine for Cherenkov traces."""

    def __init__(self, trace_log_path: str = "cherenkov_traces.jsonl"):
        self.trace_log_path = trace_log_path

    def record_trace(self, trace: CherenkovTrace) -> None:
        try:
            with open(self.trace_log_path, "a") as f:
                # Use model_dump_json for Pydantic v2
                f.write(trace.model_dump_json() + "\n")
            logger.info("Recorded trace: %s", trace.trace_id)
        except Exception as e:
            logger.error("Failed to record trace %s: %s", trace.trace_id, e)
            raise
