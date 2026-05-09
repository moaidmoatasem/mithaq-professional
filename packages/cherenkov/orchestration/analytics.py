"""
Analytics & Reporting System
Generate insights from workflow execution history
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class WorkflowAnalytics:
    """Analyze workflow execution patterns and performance"""

    def __init__(self, results_dir: str = "workflow_results"):
        self.results_dir = Path(results_dir)

    def load_all_results(self) -> List[Dict]:
        """Load all workflow results"""
        results = []
        if self.results_dir.exists():
            for file in self.results_dir.glob("*.json"):
                with open(file) as f:
                    results.append(json.load(f))
        return results

    def workflow_statistics(self) -> Dict[str, Any]:
        """Get overall workflow statistics"""
        results = self.load_all_results()

        workflows = defaultdict(list)
        for result in results:
            workflow_name = result.get("workflow", "unknown")
            workflows[workflow_name].append(result)

        stats = {
            "total_executions": len(results),
            "unique_workflows": len(workflows),
            "workflows": {},
        }

        for name, executions in workflows.items():
            stats["workflows"][name] = {
                "executions": len(executions),
                "last_run": executions[-1].get("timestamp", "unknown"),
            }

        return stats

    def performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        results = self.load_all_results()

        if not results:
            return {"message": "No results to analyze"}

        # Extract durations if available
        durations = []
        for result in results:
            if "result" in result and "duration" in result["result"]:
                durations.append(result["result"]["duration"])

        if durations:
            return {
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_runs": len(durations),
            }

        return {"message": "No duration data available"}

    def generate_report(self) -> str:
        """Generate markdown report"""
        stats = self.workflow_statistics()
        perf = self.performance_metrics()

        report = f"""# Workflow Analytics Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

- **Total Executions**: {stats['total_executions']}
- **Unique Workflows**: {stats['unique_workflows']}

## Workflow Breakdown

"""
        for name, data in stats.get("workflows", {}).items():
            report += f"### {name}\n"
            report += f"- Executions: {data['executions']}\n"
            report += f"- Last Run: {data['last_run']}\n"

        report += "## Performance Metrics\n\n"

        if "avg_duration" in perf:
            report += f"- Average Duration: {perf['avg_duration']:.4f}s\n"
            report += f"- Fastest: {perf['min_duration']:.4f}s\n"
            report += f"- Slowest: {perf['max_duration']:.4f}s\n"
        else:
            report += f"- {perf.get('message', 'No data')}\n"

        return report


def generate_analytics_report(output_file: str = "analytics_report.md"):
    """Generate and save analytics report"""
    analytics = WorkflowAnalytics()
    report = analytics.generate_report()

    Path(output_file).write_text(report)
    print(f"📊 Analytics report generated: {output_file}")
    return report
