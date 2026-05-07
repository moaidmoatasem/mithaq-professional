"""
Integration tests for workflow orchestration
"""
import pytest
from pathlib import Path
from mithaq.workflow_parser import WorkflowParser, load_workflow
from mithaq.orchestration_api import orchestrate_workflow

def test_parse_security_workflow():
    """Test parsing a security scan workflow"""
    workflow_file = "mithaq-professional/examples/workflows/security_scan_workflow.yaml"
    
    if not Path(workflow_file).exists():
        pytest.skip("Example workflow not found")
    
    parser = WorkflowParser(workflow_file)
    config = parser.parse()
    
    assert config['name'] == "Basic Security Scan"
    assert len(config['agents']) == 2
    assert len(config['tasks']) == 2

def test_parse_parallel_workflow():
    """Test parsing a parallel workflow"""
    workflow_file = "mithaq-professional/examples/workflows/parallel_test_workflow.yaml"
    
    if not Path(workflow_file).exists():
        pytest.skip("Example workflow not found")
    
    parser = WorkflowParser(workflow_file)
    config = parser.parse()
    
    assert config['name'] == "Parallel Exploit Testing"
    assert parser.is_parallel() is True

def test_workflow_execution():
    """Test executing a workflow"""
    # Mock workflow config
    workflow = {
        'name': 'Test Workflow',
        'agents': [{'role': 'tester'}],
        'tasks': [{'name': 'test', 'description': 'run test'}]
    }
    
    result = orchestrate_workflow(workflow)
    
    assert result.success is True
    assert result.duration >= 0

