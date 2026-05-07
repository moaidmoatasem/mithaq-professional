"""Example: Threat modeling with ArchitectAgent."""

from mithaq.agents.architect_agent import ArchitectAgent


def main():
    """Demonstrate threat modeling for a mobile banking app."""
    print("🔒 mithaq Security Framework - Threat Modeling Example\n")

    architect = ArchitectAgent()

    print("📋 Agent Capabilities:")
    caps = architect.get_capabilities()
    print(f"  Role: {caps['role']}")
    print(f"  Goal: {caps['goal']}")
    print(f"  Model: {caps['llm_model']}\n")


if __name__ == "__main__":
    main()

