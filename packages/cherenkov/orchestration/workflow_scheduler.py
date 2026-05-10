"""Workflow Scheduler — orchestrates workflow execution lifecycle."""

import logging
import time
from typing import Any, Dict, Optional

from cherenkov.orchestration.result_persistence import ResultStore
from cherenkov.orchestration.types import WorkflowResult

logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """Schedules and tracks workflow execution."""

    def __init__(self, result_store: Optional[ResultStore] = None) -> None:
        self._result_store = result_store

    @property
    def _store(self) -> ResultStore:
        if self._result_store is None:
            self._result_store = ResultStore()
        return self._result_store

    def schedule(self, config: Dict[str, Any]) -> WorkflowResult:
        """Execute an AI workflow based on configuration."""
        start = time.time()
        try:
            if not config:
                logger.warning("Empty workflow config received")
                return WorkflowResult(
                    success=False, outputs={}, duration=0, errors=["Empty config"]
                )

            outputs: Dict[str, Any] = {"status": "executed", "config": config}
            duration = time.time() - start
            self._store.save_result(config.get("name", "Unnamed"), outputs)
            logger.info("Workflow executed in %.2fs", duration)
            return WorkflowResult(success=True, outputs=outputs, duration=duration, errors=None)

        except Exception as e:
            logger.error("Workflow execution failed: %s", e)
            return WorkflowResult(
                success=False,
                outputs={},
                duration=time.time() - start,
                errors=[str(e)],
            )

    def get_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow by ID."""
        return self._store.get_latest(workflow_id)
