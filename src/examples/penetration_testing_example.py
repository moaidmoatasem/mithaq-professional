"""Example: Penetration testing with TesterAgent."""

from cherenkov.agents.tester_agent import TesterAgent


def main():
    """Demonstrate vulnerability validation."""
    print("🎯 cherenkov Security Framework - Penetration Testing Example\n")

    tester = TesterAgent()

    print("📋 Agent Capabilities:")
    caps = tester.get_capabilities()
    print(f"  Role: {caps['role']}")
    print(f"  Goal: {caps['goal']}\n")

    print("🔍 Validating SQL Injection Vulnerability...")
    print("=" * 60)

    # Correct signature: vuln_id, target, proof_of_concept
    validation = tester.validate_vulnerability(
        vuln_id="CVE-2024-SQLI-001",
        target="E-commerce checkout page",
        proof_of_concept="' OR '1'='1' -- injection in payment_id parameter",
    )

    print(f"Task ID: {validation.task_id}")
    print(f"Action: {validation.action}")
    print(f"Target: {validation.target}")
    print(f"Confidence: {validation.confidence:.2f}")
    print(f"Reasoning: {validation.reasoning}")
    print("=" * 60)


if __name__ == "__main__":
    main()
