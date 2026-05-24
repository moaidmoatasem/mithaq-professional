"""
LATTICE — DEPRECATED: Re-exports from cherenkov.core.lattice_bridge.

This module exists only for import compatibility. All new code should
import directly from cherenkov.core.lattice_bridge.
"""

from cherenkov.core.lattice_bridge import (  # noqa: F401
    embed_and_store,
    label_false_positive,
    query_similar_targets,
    vector_count,
)
from cherenkov.core.base_scanner import ScanResult  # noqa: F401
