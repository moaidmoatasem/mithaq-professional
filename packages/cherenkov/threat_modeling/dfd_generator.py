from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Tuple

from cherenkov.threat_modeling.schemas import (
    DFDItem,
    DFDItemType,
    Diagram,
    Threat,
    ThreatModel,
    Severity,
    ThreatStatus,
)

STRIDE_CATEGORIES: Dict[str, Tuple[str, str]] = {
    "spoofing": ("Spoofing", "Impersonating a user, process, or external system"),
    "tampering": ("Tampering", "Modifying data in transit or at rest"),
    "repudiation": ("Repudiation", "Denying an action occurred without proof"),
    "information_disclosure": (
        "Information Disclosure",
        "Exposing sensitive data to unauthorized parties",
    ),
    "denial_of_service": (
        "Denial of Service",
        "Making a service unavailable to legitimate users",
    ),
    "elevation_of_privilege": (
        "Elevation of Privilege",
        "Gaining unauthorized access to higher privilege levels",
    ),
}


class DFDGenerator:
    """Generates Data Flow Diagrams and threat models from system descriptions.

    Uses pattern-based templates for common architecture patterns and
    integrates with LLM via OllamaClient for complex system descriptions.
    """

    def __init__(self, llm_client=None):
        self._llm = llm_client

    def generate(
        self,
        system_description: str,
        architecture_pattern: str = "web_app",
        owner: str = "Security Team",
        contributors: Optional[List[str]] = None,
    ) -> ThreatModel:
        """Generate a complete threat model from a system description.

        Args:
            system_description: Natural language description of the system.
            architecture_pattern: Known architecture template to apply.
            owner: Threat model owner name.
            contributors: List of contributor names.

        Returns:
            A complete ThreatModel with diagrams, threats, and risks.
        """
        if self._llm:
            return self._generate_with_llm(
                system_description, architecture_pattern, owner, contributors or []
            )
        return self._generate_template(
            system_description, architecture_pattern, owner, contributors or []
        )

    def _generate_with_llm(
        self,
        system_description: str,
        architecture_pattern: str,
        owner: str,
        contributors: List[str],
    ) -> ThreatModel:
        """Use LLM to parse the description and generate a richer threat model."""
        prompt = (
            "Generate a threat model for the following system. "
            "Identify actors, processes, data stores, data flows, and trust boundaries. "
            "Then apply STRIDE to each component to identify threats.\n\n"
            f"System: {system_description}\n"
            f"Architecture pattern: {architecture_pattern}\n"
        )
        llm_result = self._llm.analyze_threat_model({"description": system_description})
        raw_text = llm_result.get("threat_model", "")
        base = self._build_template_model(system_description, owner, contributors)
        self._enrich_from_llm_output(base, raw_text)
        return base

    def _enrich_from_llm_output(self, model: ThreatModel, raw_text: str) -> None:
        """Parse LLM output and merge into the threat model."""
        if not raw_text:
            return
        lines = raw_text.strip().split("\n")
        current_diagram = model.diagrams[0] if model.diagrams else None
        for line in lines:
            line = line.strip()
            lower = line.lower()
            if not current_diagram:
                continue
            if lower.startswith("threat:") or lower.startswith("- threat"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    threat_title = parts[1].strip()
                    tid = str(uuid.uuid4())[:8]
                    t = Threat(
                        id=tid,
                        title=threat_title,
                        description=threat_title,
                        severity=Severity.MEDIUM,
                        type="Information Disclosure",
                    )
                    current_diagram.threats.append(t)

    def _generate_template(
        self,
        system_description: str,
        architecture_pattern: str,
        owner: str,
        contributors: List[str],
    ) -> ThreatModel:
        return self._build_template_model(system_description, owner, contributors)

    def _build_template_model(
        self,
        description: str,
        owner: str,
        contributors: List[str],
    ) -> ThreatModel:
        diagram = self._build_web_app_diagram()
        threats = self._apply_stride_to_diagram(diagram)
        diagram.threats = threats

        model = ThreatModel(
            title=f"Threat Model: {description[:60]}",
            owner=owner,
            description=description,
            contributors=contributors,
            diagrams=[diagram],
            reviewer="",
        )
        self._add_default_controls(model)
        self._add_default_risks(model, threats)
        return model

    def _build_web_app_diagram(self) -> Diagram:
        diagram = Diagram(
            title="Main Request Data Flow",
            diagram_type="STRIDE",
            description="STRIDE data flow diagram for the web application",
        )

        uid = lambda: str(uuid.uuid4())[:8]

        diagram.items.extend(
            [
                DFDItem(
                    id=uid(),
                    name="External User",
                    type=DFDItemType.ACTOR,
                    description="End user accessing the application",
                    trust_zone="untrusted",
                ),
                DFDItem(
                    id=uid(),
                    name="Web Application",
                    type=DFDItemType.PROCESS,
                    description="Primary web application server",
                    trust_zone="internal_network",
                    privilege_level="user",
                ),
                DFDItem(
                    id=uid(),
                    name="API Gateway",
                    type=DFDItemType.PROCESS,
                    description="API gateway and load balancer",
                    trust_zone="dmz",
                    privilege_level="service",
                ),
                DFDItem(
                    id=uid(),
                    name="Application Database",
                    type=DFDItemType.DATA_STORE,
                    description="Primary relational database",
                    trust_zone="secure_network",
                    stores_credentials=True,
                ),
                DFDItem(
                    id=uid(),
                    name="Cache Layer",
                    type=DFDItemType.DATA_STORE,
                    description="In-memory cache (Redis/Memcached)",
                    trust_zone="secure_network",
                ),
                DFDItem(
                    id=uid(),
                    name="User → WebApp",
                    type=DFDItemType.DATA_FLOW,
                    description="HTTPS requests (TLS 1.3)",
                    source="External User",
                    destination="Web Application",
                    protocol="HTTPS",
                    encrypted=True,
                ),
                DFDItem(
                    id=uid(),
                    name="WebApp → API Gateway",
                    type=DFDItemType.DATA_FLOW,
                    description="Internal API calls",
                    source="Web Application",
                    destination="API Gateway",
                    protocol="gRPC",
                    encrypted=True,
                ),
                DFDItem(
                    id=uid(),
                    name="API → Database",
                    type=DFDItemType.DATA_FLOW,
                    description="Database queries with ORM",
                    source="API Gateway",
                    destination="Application Database",
                    protocol="SQL/TLS",
                    encrypted=True,
                ),
                DFDItem(
                    id=uid(),
                    name="Browser Trust Boundary",
                    type=DFDItemType.TRUST_BOUNDARY,
                    description="Boundary between user browser and server",
                    is_trust_boundary=True,
                    trust_zone="untrusted",
                ),
                DFDItem(
                    id=uid(),
                    name="DMZ Trust Boundary",
                    type=DFDItemType.TRUST_BOUNDARY,
                    description="Boundary between DMZ and internal network",
                    is_trust_boundary=True,
                    trust_zone="dmz",
                ),
            ]
        )
        return diagram

    def _apply_stride_to_diagram(self, diagram: Diagram) -> List[Threat]:
        threats: List[Threat] = []
        tid_counter = [0]

        def make_threat(
            title: str,
            description: str,
            severity: Severity,
            stride_type: str,
            mitigation: str,
            cwe: str = "",
        ) -> Threat:
            tid_counter[0] += 1
            return Threat(
                id=f"T-{tid_counter[0]:04d}",
                title=title,
                description=description,
                severity=severity,
                status=ThreatStatus.OPEN,
                model_type="STRIDE",
                type=stride_type,
                mitigation=mitigation,
                cwe=cwe,
            )

        for item in diagram.items:
            if item.type in (DFDItemType.ACTOR, DFDItemType.PROCESS):
                threats.append(
                    make_threat(
                        f"Spoofing of {item.name}",
                        f"An attacker could impersonate '{item.name}' and gain unauthorized access to the system.",
                        Severity.HIGH,
                        "Spoofing",
                        "Implement strong authentication (MFA, certificate-based). "
                        "Use session management with secure cookies.",
                        "CWE-287",
                    )
                )
                threats.append(
                    make_threat(
                        f"Elevation of Privilege via {item.name}",
                        f"An attacker could exploit vulnerabilities in '{item.name}' "
                        f"to escalate privileges beyond {item.privilege_level or 'current'} level.",
                        Severity.CRITICAL,
                        "Elevation of Privilege",
                        "Apply principle of least privilege. Use RBAC with strict permission boundaries. "
                        "Regularly audit privilege assignments.",
                        "CWE-269",
                    )
                )

            if item.type == DFDItemType.DATA_STORE:
                threats.append(
                    make_threat(
                        f"Information Disclosure in {item.name}",
                        f"Sensitive data stored in '{item.name}' could be exposed "
                        f"if proper encryption is not enforced.",
                        Severity.HIGH,
                        "Information Disclosure",
                        "Encrypt data at rest using AES-256. Use column-level encryption for PII. "
                        "Implement access controls and audit logging.",
                        "CWE-200",
                    )
                )
                threats.append(
                    make_threat(
                        f"Tampering with {item.name}",
                        f"An attacker could tamper with data in '{item.name}', "
                        f"compromising data integrity.",
                        Severity.HIGH,
                        "Tampering",
                        "Implement database integrity checks, checksums, and audit trails. "
                        "Use parameterized queries to prevent SQL injection.",
                        "CWE-353",
                    )
                )

            if item.type == DFDItemType.DATA_FLOW:
                threats.append(
                    make_threat(
                        f"Tampering via {item.name}",
                        f"Data flowing through '{item.name}' could be tampered with "
                        f"if {'' if item.encrypted else 'not '}encrypted.",
                        Severity.MEDIUM,
                        "Tampering",
                        "Use TLS 1.3 for all data in transit. Implement message signing "
                        "and integrity checks (HMAC).",
                        "CWE-924",
                    )
                )

        threats.append(
            make_threat(
                "Denial of Service against Web Tier",
                "An attacker could flood the web application with requests, "
                "causing service unavailability.",
                Severity.HIGH,
                "Denial of Service",
                "Implement rate limiting, WAF, CDN-based DDoS protection, "
                "and auto-scaling groups.",
                "CWE-770",
            )
        )
        threats.append(
            make_threat(
                "Repudiation of Critical Actions",
                "Users or internal actors could deny performing critical actions "
                "without sufficient audit evidence.",
                Severity.MEDIUM,
                "Repudiation",
                "Implement immutable audit logging with SHA-256 chaining. "
                "Use digital signatures for critical transactions.",
                "CWE-778",
            )
        )
        return threats

    def _add_default_controls(self, model: ThreatModel) -> None:
        from cherenkov.threat_modeling.schemas import Control, ControlStatus

        model.controls = [
            Control(
                id="C-001",
                title="Authentication & MFA",
                description="Implement multi-factor authentication for all user access",
                status=ControlStatus.ACTIVE,
                priority="critical",
            ),
            Control(
                id="C-002",
                title="Data Encryption at Rest",
                description="Encrypt all sensitive data at rest using AES-256",
                status=ControlStatus.ACTIVE,
                priority="high",
            ),
            Control(
                id="C-003",
                title="TLS for Data in Transit",
                description="Use TLS 1.3 for all network communications",
                status=ControlStatus.ACTIVE,
                priority="high",
            ),
            Control(
                id="C-004",
                title="Input Validation & Sanitization",
                description="Validate and sanitize all user inputs to prevent injection",
                status=ControlStatus.SUGGESTED,
                priority="critical",
            ),
            Control(
                id="C-005",
                title="Rate Limiting & DoS Protection",
                description="Implement rate limiting, WAF, and DDoS mitigation",
                status=ControlStatus.SUGGESTED,
                priority="high",
            ),
            Control(
                id="C-006",
                title="Immutable Audit Logging",
                description="Maintain immutable logs with SHA-256 chaining for forensics",
                status=ControlStatus.ACTIVE,
                priority="high",
            ),
        ]

    def _add_default_risks(self, model: ThreatModel, threats: List[Threat]) -> None:
        from cherenkov.threat_modeling.schemas import Risk, RiskLevel

        critical_count = sum(1 for t in threats if t.severity == Severity.CRITICAL)
        high_count = sum(1 for t in threats if t.severity == Severity.HIGH)
        total = len(threats)

        model.risks = [
            Risk(
                id="R-001",
                title="Unauthorized Access Risk",
                description=f"System has {critical_count} critical threats related to "
                "spoofing and elevation of privilege that could lead to unauthorized access.",
                likelihood="likely",
                impact="major",
                score=16,
                level=RiskLevel.HIGH,
                threat_ids=[t.id for t in threats if t.type in ("Spoofing", "Elevation of Privilege")],
            ),
            Risk(
                id="R-002",
                title="Data Breach Risk",
                description=f"System has {high_count} high-severity threats related to "
                "information disclosure and tampering that could result in data breaches.",
                likelihood="possible",
                impact="severe",
                score=20,
                level=RiskLevel.VERY_HIGH,
                threat_ids=[t.id for t in threats if t.type in ("Information Disclosure", "Tampering")],
            ),
            Risk(
                id="R-003",
                title="Availability Risk",
                description="Denial of service threats could impact system availability "
                "and business continuity.",
                likelihood="possible",
                impact="major",
                score=15,
                level=RiskLevel.HIGH,
                threat_ids=[t.id for t in threats if t.type == "Denial of Service"],
            ),
        ]
