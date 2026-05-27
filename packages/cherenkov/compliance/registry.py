"""Compliance registry for auto-discovering and managing compliance framework plugins."""

from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path

from .base import ComplianceFramework

logger = logging.getLogger(__name__)


class ComplianceRegistry:
    """Auto-discovers all ComplianceFramework subclasses.

    To add a new framework, drop a new .py file in compliance/ and inherit
    from ComplianceFramework.
    """

    _registry: dict[str, ComplianceFramework] = {}

    @classmethod
    def _discover(cls):
        """Discovers compliance frameworks under packages/cherenkov/compliance."""
        if cls._registry:
            return
        pkg_dir = Path(__file__).parent
        for _, module_name, _ in pkgutil.iter_modules([str(pkg_dir)]):
            if module_name in ("base", "registry", "__init__"):
                continue
            try:
                mod = importlib.import_module(f"cherenkov.compliance.{module_name}")
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, ComplianceFramework)
                        and attr is not ComplianceFramework
                    ):
                        instance = attr()
                        cls._registry[instance.framework_id] = instance
            except Exception as e:
                logger.warning("Could not load compliance module %s: %s", module_name, e)

    @classmethod
    def get(cls, framework_id: str) -> ComplianceFramework | None:
        """Retrieves a compliance framework by ID."""
        cls._discover()
        return cls._registry.get(framework_id)

    @classmethod
    def list_frameworks(cls) -> list[dict]:
        """Lists metadata of all registered compliance frameworks."""
        cls._discover()
        return [
            {
                "id": fw.framework_id,
                "name": fw.framework_name,
                "version": fw.framework_version,
                "regulator": fw.regulator,
                "controls": len(fw.controls),
            }
            for fw in cls._registry.values()
        ]

    @classmethod
    def list_framework_ids(cls) -> list[str]:
        """Lists IDs of all registered compliance frameworks."""
        cls._discover()
        return list(cls._registry.keys())

    @classmethod
    def get_cwe_mappings(cls, cwe: str) -> dict[str, list[str]]:
        """Provides a unified mapping of a given CWE to control IDs across all frameworks.

        Returns:
            A dictionary mapping framework IDs to lists of mapped control IDs.
        """
        cls._discover()
        mappings = {}
        for fw_id, fw in cls._registry.items():
            control_ids = fw.cwe_map.get(cwe)
            if control_ids:
                mappings[fw_id] = control_ids
        return mappings

    @classmethod
    def generate_report(cls, framework_id: str, findings: list[dict], scan_id: str):
        """Generates a compliance report for a specific framework.

        Args:
            framework_id: Framework unique ID.
            findings: List of security findings.
            scan_id: Scan ID trace.

        Raises:
            ValueError: If the framework is unknown.
        """
        fw = cls.get(framework_id)
        if not fw:
            available = list(cls._registry.keys())
            raise ValueError(f"Unknown framework: {framework_id}. Available: {available}")
        return fw.generate_report(findings, scan_id)
