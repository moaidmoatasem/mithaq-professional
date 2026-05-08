"""
Result Persistence - Save and load workflow execution results
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseStorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def save(self, workflow_name: str, result_with_meta: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def load(self, identifier: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list(self, workflow_name: Optional[str] = None) -> List[str]:
        pass


class FileStorageBackend(BaseStorageBackend):
    """File-based JSON storage implementation"""

    def __init__(self, storage_dir: str = "workflow_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, workflow_name: str, result_with_meta: Dict[str, Any]) -> str:
        timestamp = result_with_meta.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
        filename = f"{workflow_name}_{timestamp}.json"
        filepath = self.storage_dir / filename

        with open(filepath, "w") as f:
            json.dump(result_with_meta, f, indent=2)

        return str(filepath)

    def load(self, identifier: str) -> Optional[Dict[str, Any]]:
        # identifier can be filename or filepath
        filepath = Path(identifier)
        if not filepath.is_absolute():
            filepath = self.storage_dir / filepath

        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            return json.load(f)

    def list(self, workflow_name: Optional[str] = None) -> List[str]:
        pattern = f"{workflow_name}_*.json" if workflow_name else "*.json"
        return [f.name for f in self.storage_dir.glob(pattern)]


class ResultStore:
    """Store and retrieve workflow execution results"""

    def __init__(
        self, storage_dir: str = "workflow_results", backend: Optional[BaseStorageBackend] = None
    ):
        if backend is None:
            self.backend = FileStorageBackend(storage_dir)
        else:
            self.backend = backend

    def save_result(self, workflow_name: str, result: Dict[str, Any]) -> str:
        """
        Save a workflow execution result

        Args:
            workflow_name: Name of the workflow
            result: Execution result dictionary

        Returns:
            Identifier (e.g., path) to saved result
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Add metadata
        result_with_meta = {
            "workflow": workflow_name,
            "timestamp": timestamp,
            "saved_at": str(datetime.now()),
            "result": result,
        }

        return self.backend.save(workflow_name, result_with_meta)

    def load_result(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Load a specific result file"""
        return self.backend.load(identifier)

    def list_results(self, workflow_name: Optional[str] = None) -> list:
        """
        List all saved results

        Args:
            workflow_name: Optional filter by workflow name

        Returns:
            List of result identifiers
        """
        return self.backend.list(workflow_name)

    def get_latest(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent result for a workflow"""
        results = self.list_results(workflow_name)

        if not results:
            return None

        # Sort by timestamp (newest first)
        results.sort(reverse=True)
        return self.load_result(results[0])
