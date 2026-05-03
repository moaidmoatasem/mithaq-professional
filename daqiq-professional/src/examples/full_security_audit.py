"""Example: Complete security audit with SecurityCrew."""

from daqiq.crews.security_crew import SecurityCrew


def main():
    """Demonstrate end-to-end security audit workflow."""
    print("🔐 DAQIQ Security Framework - Full Security Audit\n")

    # Initialize security crew
    crew = SecurityCrew(verbose=True)

    # Display crew information
    print("📋 Security Crew Configuration:")
    info = crew.get_crew_info()
    print(f"  Agents: {len(info['agents'])}")
    for agent_type, role in info["agents"].items():
        print(f"    - {agent_type}: {role}")
    print(f"  Process: {info['process']}\n")

    # Perform full security audit
    print("🔍 Performing Full Security Audit...")
    print("=" * 60)
    print("Target: E-Commerce Web Application")
    print("Scope: Threat Model + Code Review + Penetration Testing")
    print("=" * 60 + "\n")

    result = crew.perform_security_audit(
        target="E-Commerce Web Application (React + Node.js + MongoDB)",
        scope=["threat_model", "code_review", "pentest"],
    )

    print("\n✅ Audit Results:")
    print(f"  Target: {result['target']}")
    print(f"  Scope: {', '.join(result['scope'])}")
    print(f"  Agents Used: {result['agents_used']}")
    print(f"\n  Findings:\n{result['result']}")
    print("\n" + "=" * 60)

    # Mobile app analysis
    print("\n🔍 Analyzing Mobile Application...")
    print("=" * 60)

    mobile_result = crew.analyze_mobile_app(
        apk_path="/home/user/samples/banking-app.apk"
    )

    print("\n✅ Mobile Analysis Results:")
    print(f"  APK: {mobile_result['apk_path']}")
    print(f"  Analysis Type: {mobile_result['analysis_type']}")
    print(f"  Agents Used: {mobile_result['agents_used']}")
    print(f"\n  Findings:\n{mobile_result['result']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
