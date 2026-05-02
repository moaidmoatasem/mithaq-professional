# 🚀 DAQIQ Autonomous Agents - Usage Guide

## For First-Time Users

### 1. Run the Demo

```bash
cd ~/daqiq-dev-agents
python daqiq-professional/scripts/demo_workflow_execution.py
```

Expected output:

### 2. Try a Different Workflow

```bash
python daqiq-professional/scripts/daqiq_cli_orchestrate.py orchestrate \
  --config examples/workflows/quick_scan_workflow.yaml
```

### 3. Create Your Own Workflow

```yaml
# my_workflow.yaml
name: "My Custom Workflow"
agents:
  - role: "vulnerability_scanner"
    tools: [sql_injection_scanner]
tasks:
  - name: "scan"
    description: "Run my scan"
```

Then run:
```bash
python daqiq-professional/scripts/daqiq_cli_orchestrate.py orchestrate \
  --config my_workflow.yaml
```

## For Developers

### Run Autonomous Iteration

Let agents decide what to build next:

```bash
cd ~/daqiq-dev-agents
PYTHONPATH=. python daqiq-professional/scripts/swarm_iteration_9_auto.py
```

### Create Specific Feature

```python
# swarm_iteration_9_myfeature.py
from daqiq.agents.micro_swarm.micro_agent import MicroAgent, MicroAgentConfig
from daqiq.agents.micro_swarm.swarm_orchestrator import MicroSwarm

def build_my_feature(context: str):
    # Implement your feature
    return {'status': 'done'}

agent = MicroAgent(MicroAgentConfig(
    role="FeatureBuilder",
    tool_function=build_my_feature
))

swarm = MicroSwarm(max_parallel=1)
results = swarm.deploy([agent], ["Build feature"])
```

### Run Tests

```bash
PYTHONPATH=src:. pytest tests/ -v
```

## Using Docker

### Build Image

```bash
cd daqiq-professional
docker build -t daqiq-autonomous .
```

### Run Demo

```bash
docker run --rm daqiq-autonomous
```

### Run Custom Workflow

```bash
docker run --rm -v $(pwd)/my_workflow.yaml:/app/workflow.yaml \
  daqiq-autonomous python scripts/daqiq_cli_orchestrate.py \
  orchestrate --config /app/workflow.yaml
```

## Advanced Usage

### Result Persistence

```python
from daqiq.result_persistence import ResultStore

store = ResultStore()

# Save result
path = store.save_result("my_workflow", {"status": "success"})

# Load latest
result = store.get_latest("my_workflow")

# List all
results = store.list_results("my_workflow")
```

### Agent Factory

```python
from daqiq.agent_factory import AgentFactory

# Create agent from config
agent = AgentFactory.create_agent('payload_tester', {
    'endpoint': '/api/test'
})

# Create from workflow
agents = AgentFactory.create_agents_from_workflow(workflow_config)
```

## Troubleshooting

### Import Error
```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=daqiq-professional/src:.
```

### Module Not Found
```bash
# Install dependencies
pip install -r requirements.txt
```

### Workflow Not Executing
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('workflow.yaml'))"
```

## Getting Help

- Check logs in `workflow_results/`
- Review test suite: `pytest tests/ -v`
- See iteration history: `git log --oneline`

---

Built by autonomous agents 🤖
