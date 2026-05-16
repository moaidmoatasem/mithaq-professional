from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from cherenkov.threat_modeling.schemas import (
    Control,
    DFDItem,
    DFDItemType,
    Diagram,
    Risk,
    Threat,
    ThreatModel,
    RiskLevel,
)

TM_BOM_SCHEMA = (
    "https://github.com/OWASP/www-project-threat-model-library/blob/"
    "v1.0.2/threat-model.schema.json"
)


class TMBOMExporter:
    """Exports ThreatModel to OWASP TM-BOM (Threat Model Bill of Materials) format.

    TM-BOM is the emerging ECMA-424 standard format for threat models,
    supported by OWASP Threat Dragon v2.5+ (import) and the OWASP
    Threat Model Library. This export follows the v1.0.2 schema.
    """

    def __init__(self, model: ThreatModel):
        self.model = model

    def export(self) -> Dict:
        """Build the TM-BOM JSON structure per v1.0.2 schema."""
        diagram = self.model.diagrams[0] if self.model.diagrams else None
        trust_zones = self._extract_trust_zones(diagram)
        actors = self._extract_actors(diagram)
        components = self._extract_components(diagram)
        data_stores = self._extract_data_stores(diagram)
        data_flows = self._extract_data_flows(diagram)
        threats = self._extract_threats(diagram)

        return {
            "$schema": TM_BOM_SCHEMA,
            "version": self.model.version,
            "scope": {
                "title": self.model.title,
                "description": self.model.description,
                "business_criticality": "high",
                "data_sensitivity": ["pii", "cred"],
                "exposure": "external",
                "tier": "business_critical",
            },
            "description": self._build_description(),
            "trust_zones": trust_zones,
            "trust_boundaries": self._extract_trust_boundaries(trust_zones),
            "actors": actors,
            "components": components,
            "data_stores": data_stores,
            "data_sets": self._extract_data_sets(data_stores),
            "data_flows": data_flows,
            "threat_personas": [
                {
                    "symbolic_name": "external-attacker",
                    "title": "External Attacker",
                    "description": "Remote unauthenticated attacker with malicious intent",
                    "is_person": True,
                    "skill_level": "engineer",
                    "access_level": "anonymous",
                    "malicious_intent": True,
                    "applicability_to_org": "high",
                },
                {
                    "symbolic_name": "malicious-insider",
                    "title": "Malicious Insider",
                    "description": "Authenticated user with privileged access",
                    "is_person": True,
                    "skill_level": "expert_engineer",
                    "access_level": "admin",
                    "malicious_intent": True,
                    "applicability_to_org": "moderate",
                },
            ],
            "threats": threats,
            "controls": self._extract_controls(),
            "risks": self._extract_risks(),
            "assumptions": [
                {
                    "description": "Network perimeter is protected by a firewall and IDS/IPS",
                    "topics": ["network-security"],
                    "validity": "unconfirmed",
                },
                {
                    "description": "All external connections use TLS 1.3",
                    "topics": ["crypto"],
                    "validity": "unconfirmed",
                },
            ],
        }

    def _build_description(self) -> str:
        desc = f"# {self.model.title}\n\n{self.model.description}\n\n"
        if self.model.diagrams:
            diagram = self.model.diagrams[0]
            desc += (
                f"## Architecture\n\n"
                f"This threat model covers {len(diagram.items)} DFD elements "
                f"with {len(diagram.threats)} identified threats "
                f"using {diagram.diagram_type} methodology.\n\n"
            )
            actors = sum(1 for i in diagram.items if i.type == DFDItemType.ACTOR)
            procs = sum(1 for i in diagram.items if i.type == DFDItemType.PROCESS)
            stores = sum(1 for i in diagram.items if i.type == DFDItemType.DATA_STORE)
            flows = sum(1 for i in diagram.items if i.type == DFDItemType.DATA_FLOW)
            desc += (
                f"- **Actors**: {actors}\n"
                f"- **Processes**: {procs}\n"
                f"- **Data Stores**: {stores}\n"
                f"- **Data Flows**: {flows}\n"
            )
        desc += "\n## Controls\n\n"
        for c in self.model.controls:
            desc += f"- **{c.title}** ({c.status.value}): {c.description}\n"
        return desc

    def _extract_trust_zones(self, diagram: Optional[Diagram]) -> List[Dict]:
        zones = {}
        if diagram:
            for item in diagram.items:
                zone = item.trust_zone
                if zone not in zones:
                    zones[zone] = {
                        "symbolic_name": zone.replace(" ", "-").lower(),
                        "title": zone.replace("_", " ").title(),
                        "description": f"Trust zone: {zone}",
                    }
        if not zones:
            zones["default"] = {
                "symbolic_name": "default",
                "title": "Default Trust Zone",
                "description": "Default trust zone boundary",
            }
        return list(zones.values())

    def _extract_trust_boundaries(self, zones: List[Dict]) -> List[Dict]:
        if len(zones) < 2:
            return [
                {
                    "trust_zone_a": zones[0]["symbolic_name"],
                    "trust_zone_b": zones[0]["symbolic_name"],
                    "authentication_methods": ["password", "token"],
                    "access_control_methods": ["rbac"],
                    "access_token_expires": True,
                    "access_token_ttl": 3600,
                    "has_refresh_token": True,
                    "refresh_token_expires": True,
                    "refresh_token_ttl": 604800,
                    "can_user_logout": True,
                    "can_system_logout": True,
                }
            ]
        return [
            {
                "trust_zone_a": "untrusted",
                "trust_zone_b": "dmz" if any(z["symbolic_name"] == "dmz" for z in zones) else zones[1]["symbolic_name"],
                "authentication_methods": ["password", "token", "biometrics"],
                "access_control_methods": ["rbac"],
                "access_token_expires": True,
                "access_token_ttl": 3600,
                "has_refresh_token": True,
                "refresh_token_expires": True,
                "refresh_token_ttl": 604800,
                "can_user_logout": True,
                "can_system_logout": True,
            }
        ]

    def _extract_actors(self, diagram: Optional[Diagram]) -> List[Dict]:
        actors = []
        if diagram:
            for item in diagram.items:
                if item.type == DFDItemType.ACTOR:
                    actors.append(
                        {
                            "symbolic_name": self._sn(item.name),
                            "title": item.name,
                            "description": item.description,
                            "type": "user" if "user" in item.name.lower() else "third_party",
                            "permissions": item.privilege_level or "user",
                            "trust_zone": self._sn(item.trust_zone),
                        }
                    )
        return actors

    def _extract_components(self, diagram: Optional[Diagram]) -> List[Dict]:
        components = []
        if diagram:
            for item in diagram.items:
                if item.type == DFDItemType.PROCESS:
                    components.append(
                        {
                            "symbolic_name": self._sn(item.name),
                            "title": item.name,
                            "description": item.description,
                            "trust_zone": self._sn(item.trust_zone),
                        }
                    )
        return components

    def _extract_data_stores(self, diagram: Optional[Diagram]) -> List[Dict]:
        stores = []
        if diagram:
            for item in diagram.items:
                if item.type == DFDItemType.DATA_STORE:
                    stores.append(
                        {
                            "symbolic_name": self._sn(item.name),
                            "title": item.name,
                            "description": item.description,
                            "type": "sql",
                            "trust_zone": self._sn(item.trust_zone),
                        }
                    )
        return stores

    def _extract_data_sets(self, stores: List[Dict]) -> List[Dict]:
        return [
            {
                "symbolic_name": f"{s['symbolic_name']}-data",
                "title": f"{s['title']} Data",
                "description": f"Sensitive data residing in {s['title']}",
                "placements": [{"data_store": s["symbolic_name"], "encrypted": True}],
                "data_sensitivity": ["pii", "cred"],
                "record_count": 100000,
            }
            for s in stores
        ]

    def _extract_data_flows(self, diagram: Optional[Diagram]) -> List[Dict]:
        flows = []
        if diagram:
            for item in diagram.items:
                if item.type == DFDItemType.DATA_FLOW:
                    flows.append(
                        {
                            "symbolic_name": self._sn(item.name),
                            "title": item.name,
                            "description": item.description,
                            "source": {
                                "type": "Actor" if self._is_actor(diagram, item.source or "") else "Component",
                                "object": self._sn(item.source or ""),
                            },
                            "destination": {
                                "type": "DataStore" if self._is_data_store(diagram, item.destination or "") else "Component",
                                "object": self._sn(item.destination or ""),
                            },
                            "has_sensitive_data": True,
                            "encrypted": item.encrypted,
                        }
                    )
        return flows

    def _extract_threats(self, diagram: Optional[Diagram]) -> List[Dict]:
        threats = []
        if diagram:
            for t in diagram.threats:
                threats.append(
                    {
                        "symbolic_name": self._sn(t.title),
                        "title": t.title,
                        "description": t.description,
                        "threat_persona": "external-attacker",
                        "event": f"Attacker exploits {t.type.lower()} vulnerability in {t.title.lower()}",
                        "sources": ["adversary"],
                        "weaknesses": [
                            {"cwe_id": int(t.cwe.replace("CWE-", "")) if t.cwe else 0}
                        ] if t.cwe else [],
                    }
                )
        return threats

    def _extract_controls(self) -> List[Dict]:
        return [
            {
                "symbolic_name": self._sn(c.title),
                "title": c.title,
                "description": c.description,
                "threats": [self._sn(t) for t in c.threat_ids],
                "status": c.status.value,
                "priority": c.priority,
            }
            for c in self.model.controls
        ]

    def _extract_risks(self) -> List[Dict]:
        level_map = {
            RiskLevel.VERY_LOW: ("minimal", 2),
            RiskLevel.LOW: ("minor", 6),
            RiskLevel.MEDIUM: ("moderate", 10),
            RiskLevel.HIGH: ("major", 16),
            RiskLevel.VERY_HIGH: ("severe", 20),
            RiskLevel.CRITICAL: ("severe", 25),
        }
        return [
            {
                "symbolic_name": self._sn(r.title),
                "title": r.title,
                "description": r.description,
                "threats": [self._sn(t) for t in r.threat_ids],
                "likelihood": r.likelihood,
                "impact": level_map.get(r.level, ("moderate", 10))[0],
                "impact_description": r.impact_description or r.description,
                "score": r.score or level_map.get(r.level, ("moderate", 10))[1],
                "level": r.level.value,
            }
            for r in self.model.risks
        ]

    def _is_actor(self, diagram: Diagram, name: str) -> bool:
        return any(i.name == name and i.type == DFDItemType.ACTOR for i in diagram.items)

    def _is_data_store(self, diagram: Diagram, name: str) -> bool:
        return any(i.name == name and i.type == DFDItemType.DATA_STORE for i in diagram.items)

    @staticmethod
    def _sn(text: str) -> str:
        return text.lower().replace(" ", "-").replace("_", "-").replace("/", "-")

    def export_to_file(self, path: str) -> Path:
        """Write the TM-BOM JSON to a file."""
        file_path = Path(path)
        file_path.write_text(json.dumps(self.export(), indent=2))
        return file_path
