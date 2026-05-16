from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from cherenkov.threat_modeling.schemas import (
    DFDItem,
    DFDItemType,
    Diagram,
    ThreatModel,
    Severity,
    ThreatStatus,
)

THREAT_DRAGON_VERSION = "2.6.0"
DEFAULT_DIAGRAM_WIDTH = 800
DEFAULT_DIAGRAM_HEIGHT = 600

# Visual cell dimensions by type
_CELL_SIZE: Dict[DFDItemType, Dict[str, int]] = {
    DFDItemType.ACTOR: {"width": 100, "height": 60},
    DFDItemType.PROCESS: {"width": 140, "height": 80},
    DFDItemType.DATA_STORE: {"width": 120, "height": 80},
    DFDItemType.DATA_FLOW: {"width": 0, "height": 0},
    DFDItemType.TRUST_BOUNDARY: {"width": 0, "height": 0},
}

_CELL_TYPE_MAP: Dict[DFDItemType, str] = {
    DFDItemType.ACTOR: "tm.Actor",
    DFDItemType.PROCESS: "tm.Process",
    DFDItemType.DATA_STORE: "tm.Store",
    DFDItemType.DATA_FLOW: "tm.Flow",
    DFDItemType.TRUST_BOUNDARY: "tm.Boundary",
}


class ThreatDragonExporter:
    """Exports ThreatModel to OWASP Threat Dragon v2 JSON format.

    Produces a JSON file that can be imported into Threat Dragon for
    visual editing, STRIDE analysis, and PDF report generation.
    """

    def __init__(self, model: ThreatModel):
        self.model = model

    def export(self) -> Dict:
        """Build the Threat Dragon v2 JSON structure."""
        return {
            "version": THREAT_DRAGON_VERSION,
            "summary": {
                "title": self.model.title,
                "owner": self.model.owner,
                "description": self.model.description,
                "id": 0,
            },
            "detail": {
                "contributors": [{"name": c} for c in self.model.contributors],
                "diagrams": [self._build_diagram(d) for d in self.model.diagrams],
                "diagramTop": len(self.model.diagrams),
                "reviewer": self.model.reviewer or "",
                "threatTop": self._count_all_threats(),
            },
        }

    def _build_diagram(self, diagram: Diagram) -> Dict:
        cells = []
        shape_ids: Dict[str, str] = {}
        x, y = 50, 80
        spacing_y = 120

        for item in diagram.items:
            if item.type == DFDItemType.TRUST_BOUNDARY:
                continue
            if item.type == DFDItemType.DATA_FLOW:
                continue
            cell_id = str(uuid.uuid4())
            shape_ids[item.name] = cell_id
            size = _CELL_SIZE.get(item.type, _CELL_SIZE[DFDItemType.PROCESS])
            stroke_color = self._stroke_color(item.type)

            cell = {
                "id": cell_id,
                "type": "basic.Rect",
                "shape": "basic.Rect",
                "size": {"width": size["width"], "height": size["height"]},
                "position": {"x": x, "y": y},
                "zIndex": 1,
                "visible": True,
                "attrs": {
                    "body": {
                        "stroke": stroke_color,
                        "strokeWidth": 2,
                        "strokeDasharray": None,
                    },
                },
            }

            threat_num = 0
            cell_threats = []
            for t in self.model.diagrams[0].threats if self.model.diagrams else []:
                if item.name.lower() in t.description.lower() or not t.affected_components:
                    threat_num += 1
                    cell_threats.append(
                        {
                            "number": threat_num,
                            "title": t.title,
                            "status": t.status.value,
                            "severity": t.severity.value.capitalize(),
                            "type": t.type,
                            "modelType": t.model_type,
                            "description": t.description,
                            "mitigation": t.mitigation,
                            "threatId": str(uuid.uuid4()),
                            "score": t.score,
                        }
                    )

            cell["threats"] = cell_threats
            cell["hasOpenThreats"] = any(
                th["status"] == "Open" for th in cell_threats
            )
            cell["data"] = self._build_item_data(item)
            cells.append(cell)
            y += spacing_y

        data_flow_id = len(cells) + 1
        for item in diagram.items:
            if item.type != DFDItemType.DATA_FLOW:
                continue
            src_id = shape_ids.get(item.source or "")
            dst_id = shape_ids.get(item.destination or "")
            if not src_id or not dst_id:
                continue
            flow_cell_id = str(uuid.uuid4())
            cells.append(
                {
                    "id": flow_cell_id,
                    "type": "basic.Link",
                    "shape": "basic.Link",
                    "zIndex": 0,
                    "visible": True,
                    "source": {"x": 0, "y": 0, "cell": src_id},
                    "target": {"x": 0, "y": 0, "cell": dst_id},
                    "connector": {"name": "rounded"},
                    "labels": [{"position": 0.5, "text": item.name}],
                    "attrs": {
                        "line": {
                            "stroke": "#5e5e5e",
                            "strokeWidth": 2,
                            "targetMarker": {"name": "classic"},
                            "sourceMarker": {"name": "block"},
                        }
                    },
                    "data": {
                        "name": item.name,
                        "description": item.description,
                        "type": "tm.Flow",
                        "isEncrypted": item.encrypted,
                        "protocol": item.protocol,
                        "hasOpenThreats": False,
                    },
                }
            )

        return {
            "id": 0,
            "title": diagram.title,
            "diagramType": diagram.diagram_type,
            "description": diagram.description,
            "thumbnail": "./public/content/images/thumbnail.stride.jpg",
            "version": diagram.version,
            "cells": cells,
        }

    def _build_item_data(self, item: DFDItem) -> Dict:
        data: Dict = {
            "name": item.name,
            "description": item.description,
            "type": _CELL_TYPE_MAP.get(item.type, "tm.Process"),
            "hasOpenThreats": False,
            "outOfScope": False,
            "privilegeLevel": item.privilege_level,
            "isTrustBoundary": item.is_trust_boundary,
            "isBidirectional": False,
            "isPublicNetwork": item.trust_zone == "untrusted" if item.type == DFDItemType.DATA_FLOW else False,
        }
        if item.type == DFDItemType.DATA_STORE:
            data["storesCredentials"] = item.stores_credentials
            data["isALog"] = False
            data["isEncrypted"] = item.encrypted
            data["isSigned"] = False
        if item.type == DFDItemType.PROCESS:
            data["isWebApplication"] = True
        return data

    def _stroke_color(self, item_type: DFDItemType) -> str:
        palette = {
            DFDItemType.ACTOR: "#4a90d9",
            DFDItemType.PROCESS: "#50c878",
            DFDItemType.DATA_STORE: "#e67e22",
        }
        return palette.get(item_type, "#95a5a6")

    def _count_all_threats(self) -> int:
        count = 0
        for d in self.model.diagrams:
            count += len(d.threats)
        return count

    def export_to_file(self, path: str) -> Path:
        """Write the Threat Dragon JSON to a file."""
        file_path = Path(path)
        file_path.write_text(json.dumps(self.export(), indent=2))
        return file_path
