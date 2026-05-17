from __future__ import annotations

from typing import Dict, List

from cherenkov.threat_modeling.schemas import (
    DFDItem,
    DFDItemType,
    Diagram,
    ThreatModel,
)


MERMAID_FLOWCHART_TEMPLATE = """graph TB
{styles}
{structure}
"""

MERMAID_C4_TEMPLATE = """C4Context
{system_boundary}
{person}
{boundaries}
{systems}
{relationships}
"""


class MermaidExporter:
    """Exports ThreatModel diagrams to Mermaid.js flowcharts.

    Mermaid.js is widely used in Markdown documentation and provides
    a text-based diagram format that renders in GitHub, GitLab, and
    most documentation tools.
    """

    def __init__(self, model: ThreatModel):
        self.model = model

    def export_flowchart(self, diagram_index: int = 0) -> str:
        """Export a diagram as a Mermaid flowchart."""
        if not self.model.diagrams or diagram_index >= len(self.model.diagrams):
            return "```mermaid\ngraph LR\n  Start[No diagram data]\n```"

        diagram = self.model.diagrams[diagram_index]
        nodes: List[str] = []
        edges: List[str] = []
        styles: List[str] = []
        subgraph_count = 0

        trust_boundary_nodes: Dict[str, List[str]] = {}
        for item in diagram.items:
            zone = item.trust_zone
            if zone not in trust_boundary_nodes:
                trust_boundary_nodes[zone] = []
            trust_boundary_nodes[zone].append(item.name)

        for zone, items in trust_boundary_nodes.items():
            if zone == "default":
                continue
            subgraph_count += 1
            safe_zone = zone.replace(" ", "_").replace("-", "_")
            nodes.append(f"subgraph {safe_zone}[{zone.replace('_', ' ').title()}]")
            for item_name in items:
                safe = self._safe_id(item_name)
                item = self._find_item(diagram, item_name)
                if item:
                    shape, style_class = self._node_style(item)
                    label = f"{'[' if shape == 'rect' else '('}{item_name}{']' if shape == 'rect' else ')'}"
                    nodes.append(f"  {safe}{label}")
                    if style_class:
                        styles.append(f"  class {safe} {style_class};")
            nodes.append("end")

        standalone_items = [
            i
            for i in diagram.items
            if i.type != DFDItemType.DATA_FLOW
            and i.type != DFDItemType.TRUST_BOUNDARY
            and i.trust_zone == "default"
        ]
        for item in standalone_items:
            safe = self._safe_id(item.name)
            shape, style_class = self._node_style(item)
            label = f"{'[' if shape == 'rect' else '('}{item.name}{']' if shape == 'rect' else ')'}"
            nodes.append(f"  {safe}{label}")
            if style_class:
                styles.append(f"  class {safe} {style_class};")

        for item in diagram.items:
            if item.type == DFDItemType.DATA_FLOW and item.source and item.destination:
                src = self._safe_id(item.source)
                dst = self._safe_id(item.destination)
                flow_label = item.name.replace('"', "'")
                arrow = "==>" if item.encrypted else "-->"
                line = f"  {src} {arrow}|{flow_label}| {dst}"
                if not item.encrypted:
                    styles.append(f"  linkStyle {len(edges)} stroke:#e74c3c,stroke-width:2px;")
                edges.append(line)

        styles_block = "\n".join(
            [
                "  classDef actor fill:#4a90d9,stroke:#2c5f8a,color:#fff;",
                "  classDef process fill:#50c878,stroke:#2d8f4e,color:#fff;",
                "  classDef store fill:#e67e22,stroke:#b85e0e,color:#fff;",
            ]
        )
        if styles:
            for s in styles:
                styles_block += f"\n{s}"

        result = "```mermaid\ngraph TB\n"
        result += f"  title{{{diagram.title}}}\n"
        result += styles_block + "\n"
        for n in nodes:
            result += f"  {n}\n"
        for e in edges:
            result += f"  {e}\n"
        result += "```"
        return result

    def export_c4(self, diagram_index: int = 0) -> str:
        """Export as a C4 model diagram (text-based representation)."""
        if not self.model.diagrams or diagram_index >= len(self.model.diagrams):
            return "C4Context\n  System(unknown, \"No diagram data\")\n"

        diagram = self.model.diagrams[diagram_index]
        lines: List[str] = ["C4Context"]
        in_dmz = False
        in_internal = False
        in_secure = False

        for item in diagram.items:
            safe = item.name.replace(" ", "_").replace("-", "_")
            if item.type == DFDItemType.TRUST_BOUNDARY:
                continue
            zone = item.trust_zone

            if zone == "dmz" and not in_dmz:
                lines.append(
                    f'  Boundary(dmz, "DMZ / Perimeter Network", $borderColor="#e67e22") {{'
                )
                in_dmz = True
                in_internal = False
                in_secure = False
            elif zone == "internal_network" and not in_internal:
                if in_dmz:
                    lines.append("  }")
                    in_dmz = False
                lines.append(
                    f'  Boundary(internal, "Internal Network", $borderColor="#2ecc71") {{'
                )
                in_internal = True
                in_secure = False
            elif zone == "secure_network" and not in_secure:
                if in_internal:
                    lines.append("  }")
                    in_internal = False
                lines.append(
                    f'  Boundary(secure, "Secure Network / Trusted Zone", $borderColor="#e74c3c") {{'
                )
                in_secure = True

            if item.type == DFDItemType.ACTOR:
                lines.append(f'  Person({safe}, "{item.name}", "{item.description}")')
            elif item.type == DFDItemType.PROCESS:
                lines.append(
                    f'  System({safe}, "{item.name}", "{item.description}")'
                )
            elif item.type == DFDItemType.DATA_STORE:
                lines.append(
                    f'  System_Ext({safe}_db, "{item.name}", "{item.description}")'
                )

        if in_dmz or in_internal or in_secure:
            lines.append("  }")

        for item in diagram.items:
            if item.type == DFDItemType.DATA_FLOW and item.source and item.destination:
                src = item.source.replace(" ", "_").replace("-", "_")
                dst = item.destination.replace(" ", "_").replace("-", "_")
                label = item.name.replace('"', "'")
                lines.append(f'  Rel({src}, {dst}, "{label}")')

        return "\n".join(lines)

    def _find_item(self, diagram: Diagram, name: str) -> DFDItem | None:
        for item in diagram.items:
            if item.name == name:
                return item
        return None

    def _node_style(self, item: DFDItem):
        type_map = {
            DFDItemType.ACTOR: ("rect", "actor"),
            DFDItemType.PROCESS: ("rect", "process"),
            DFDItemType.DATA_STORE: ("rect", "store"),
        }
        return type_map.get(item.type, ("rect", ""))

    @staticmethod
    def _safe_id(name: str) -> str:
        import re

        safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if safe and safe[0].isdigit():
            safe = "n" + safe
        return safe or "unknown"
