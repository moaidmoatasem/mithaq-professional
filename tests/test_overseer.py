import pytest
from cherenkov.core.hybrid_orchestrator import HybridOrchestrator, ExecutionMode, CognitiveLoopException

def test_overseer_loop_detection():
    orchestrator = HybridOrchestrator()
    context = {"test_file": "sensitive_content"}
    scope = ["static_analysis"]
    
    # Attempt 1
    orchestrator.execute_security_audit("web", context, scope, mode=ExecutionMode.LOCAL_ONLY)
    
    # Attempt 2
    orchestrator.execute_security_audit("web", context, scope, mode=ExecutionMode.LOCAL_ONLY)
    
    # Attempt 3 - Should raise CognitiveLoopException
    with pytest.raises(CognitiveLoopException):
        orchestrator.execute_security_audit("web", context, scope, mode=ExecutionMode.LOCAL_ONLY)

def test_overseer_aimd_decrease():
    orchestrator = HybridOrchestrator()
    initial_limit = orchestrator.concurrency_limit
    
    # Simulate a failure
    orchestrator.handle_inference_result(success=False)
    
    assert orchestrator.concurrency_limit == initial_limit // 2
    assert orchestrator.consecutive_successes == 0

def test_overseer_aimd_increase():
    orchestrator = HybridOrchestrator()
    orchestrator.concurrency_limit = 2
    
    # Simulate 5 consecutive successes
    for _ in range(5):
        orchestrator.handle_inference_result(success=True)
        
    assert orchestrator.concurrency_limit == 3
    assert orchestrator.consecutive_successes == 0
