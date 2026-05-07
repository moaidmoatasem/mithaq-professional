# mithaq Security Framework - Examples

This directory contains practical examples demonstrating the mithaq multi-agent security framework.

## Examples

### 1. Threat Modeling (`threat_modeling_example.py`)
Demonstrates how to use **ArchitectAgent** for:
- STRIDE-based threat analysis
- Security architecture review
- Attack surface mapping

```bash
python examples/threat_modeling_example.py
```

### 2. Exploit Development (`exploit_development_example.py`)
Shows **DeveloperAgent** capabilities:
- Exploit code generation
- Payload crafting
- Vulnerability analysis

```bash
python examples/exploit_development_example.py
```

### 3. Penetration Testing (`penetration_testing_example.py`)
Demonstrates **TesterAgent** functionality:
- Vulnerability validation
- API fuzzing
- Security testing workflows

```bash
python examples/penetration_testing_example.py
```

### 4. Full Security Audit (`full_security_audit.py`)
Complete workflow using **SecurityCrew**:
- Multi-agent coordination
- End-to-end security audit
- Mobile app analysis

```bash
python examples/full_security_audit.py
```

## Requirements

- Python 3.12+
- mithaq framework installed
- LLM model running (Ollama with deepseek-r1:14b)

## Notes

⚠️ **Important**: These examples require an LLM to be running. Make sure you have:
```bash
ollama run deepseek-r1:14b
```

The examples will demonstrate agent capabilities in mock/test mode without actual LLM calls during testing.

