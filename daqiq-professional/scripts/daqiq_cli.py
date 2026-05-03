#!/usr/bin/env python3
"""
DAQIQ - AI-Powered Security Testing Framework
Main CLI
"""

import sys
import argparse
from daqiq.scanners.header_scanner import SimpleScanner


def scan_command(args):
    """Run security scan"""
    scanner = SimpleScanner(args.url)
    scanner.run()


def generate_command(args):
    """Generate new security tools using AI"""
    from daqiq.crews.autonomous_dev_team import AutonomousDevTeam

    team = AutonomousDevTeam()
    team.run_project(args.description)


def main():
    parser = argparse.ArgumentParser(
        description="DAQIQ - AI-Powered Security Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  daqiq scan https://example.com
  daqiq generate "XSS vulnerability scanner"
  daqiq scan --help
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run security scan on target")
    scan_parser.add_argument("url", help="Target URL to scan")
    scan_parser.set_defaults(func=scan_command)

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate", help="Generate security tools with AI"
    )
    gen_parser.add_argument("description", help="Description of tool to generate")
    gen_parser.set_defaults(func=generate_command)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
