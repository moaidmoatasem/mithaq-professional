#!/usr/bin/env python3
"""Generate analytics report from workflow results"""

import sys

sys.path.insert(0, "src")

from mithaq.analytics import generate_analytics_report

if __name__ == "__main__":
    report = generate_analytics_report("analytics_report.md")
    print(report)

