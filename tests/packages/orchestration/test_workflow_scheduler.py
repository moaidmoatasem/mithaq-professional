"""Tests for WorkflowScheduler class."""

from unittest.mock import Mock

from cherenkov.orchestration.types import WorkflowResult
from cherenkov.orchestration.workflow_scheduler import WorkflowScheduler


def test_schedule_with_valid_config():
    store = Mock()
    scheduler = WorkflowScheduler(result_store=store)
    config = {"name": "test-workflow", "steps": ["scan", "report"]}

    result = scheduler.schedule(config)

    assert isinstance(result, WorkflowResult)
    assert result.success is True
    assert result.outputs["status"] == "executed"
    assert result.duration >= 0
    store.save_result.assert_called_once_with("test-workflow", result.outputs)


def test_schedule_with_empty_config():
    scheduler = WorkflowScheduler(result_store=Mock())

    result = scheduler.schedule({})

    assert result.success is False
    assert result.errors == ["Empty config"]
    assert result.duration == 0


def test_schedule_handles_store_exception():
    store = Mock()
    store.save_result.side_effect = RuntimeError("DB connection failed")
    scheduler = WorkflowScheduler(result_store=store)

    result = scheduler.schedule({"name": "failing-workflow"})

    assert result.success is False
    assert any("DB connection failed" in e for e in (result.errors or []))


def test_schedule_without_name_defaults_to_unnamed():
    store = Mock()
    scheduler = WorkflowScheduler(result_store=store)
    config = {"key": "value"}

    result = scheduler.schedule(config)

    store.save_result.assert_called_once_with("Unnamed", result.outputs)


def test_get_status_returns_stored_result():
    store = Mock()
    store.get_latest.return_value = {"status": "completed", "result": "ok"}
    scheduler = WorkflowScheduler(result_store=store)

    status = scheduler.get_status("my-workflow")

    assert status == {"status": "completed", "result": "ok"}
    store.get_latest.assert_called_once_with("my-workflow")


def test_get_status_returns_none_for_unknown():
    store = Mock()
    store.get_latest.return_value = None
    scheduler = WorkflowScheduler(result_store=store)

    status = scheduler.get_status("nonexistent")

    assert status is None


def test_schedule_concurrent_calls():
    store = Mock()
    scheduler = WorkflowScheduler(result_store=store)

    r1 = scheduler.schedule({"name": "wf1"})
    r2 = scheduler.schedule({"name": "wf2"})

    assert r1.success is True
    assert r2.success is True
    assert store.save_result.call_count == 2
