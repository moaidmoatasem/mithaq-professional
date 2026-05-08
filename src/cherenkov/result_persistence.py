"""
Result Persistence - Save and load workflow execution results
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ResultStore:
    """Store and retrieve workflow execution results"""

    def __init__(self, storage_dir: str = "workflow_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_result(self, workflow_name: str, result: Dict[str, Any]) -> str:
        """
        Save a workflow execution result

        Args:
            workflow_name: Name of the workflow
            result: Execution result dictionary

        Returns:
            Path to saved result file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{workflow_name}_{timestamp}.json"
        filepath = self.storage_dir / filename

        # Add metadata
        result_with_meta = {
            "workflow": workflow_name,
            "timestamp": timestamp,
            "saved_at": str(datetime.now()),
            "result": result,
        }

        with open(filepath, "w") as f:
            json.dump(result_with_meta, f, indent=2)

        return str(filepath)

    def load_result(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a specific result file"""
        filepath = self.storage_dir / filename

        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            return json.load(f)

    def list_results(self, workflow_name: Optional[str] = None) -> list:
        """
        List all saved results

        Args:
            workflow_name: Optional filter by workflow name

        Returns:
            List of result filenames
        """
        pattern = f"{workflow_name}_*.json" if workflow_name else "*.json"
        return [f.name for f in self.storage_dir.glob(pattern)]

    def get_latest(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent result for a workflow"""
        results = self.list_results(workflow_name)

        if not results:
            return None

        # Sort by timestamp (newest first)
        results.sort(reverse=True)
        return self.load_result(results[0])
