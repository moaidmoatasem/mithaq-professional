"""EGY-FIN CSF Compliance Mapper"""

from __future__ import annotations

EGY_FIN_CSF_MAPPING: dict[str, list[str]] = {
    "CWE-79": ["CBE-2.1.4"],
    "CWE-89": ["CBE-2.1.4"],
    "CWE-22": ["CBE-2.2.1"],
    "CWE-352": ["CBE-2.1.5"],
    "CWE-611": ["CBE-2.3.1"],
    "CWE-287": ["CBE-2.4.1"],
    "CWE-798": ["CBE-2.4.2"],
    "CWE-502": ["CBE-2.5.1"],
    "CWE-200": ["CBE-2.6.1"],
    "CWE-918": ["CBE-2.7.1"],
    "CWE-77": ["CBE-2.1.6"],
    "CWE-78": ["CBE-2.1.6"],
    "CWE-94": ["CBE-2.1.4"],
    "CWE-306": ["CBE-2.2.2"],
    "CWE-312": ["CBE-2.8.1"],
    "CWE-319": ["CBE-2.8.2"],
    "CWE-434": ["CBE-2.2.3"],
    "CWE-601": ["CBE-2.2.4"],
    "CWE-732": ["CBE-2.2.5"],
}


class EgyFinCsfMapper:
    """Mapper for EGY-FIN CSF compliance framework."""

    @staticmethod
    def get_controls(cwe_id: str) -> list[str]:
        """Get EGY-FIN CSF controls for a given CWE ID."""
        return EGY_FIN_CSF_MAPPING.get(cwe_id, [])

    @staticmethod
    def list_all_mappings() -> dict[str, list[str]]:
        """Return the complete CWE to EGY-FIN CSF mapping."""
        return EGY_FIN_CSF_MAPPING.copy()
