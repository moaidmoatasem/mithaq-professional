from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class DFDItemType(str, Enum):
    ACTOR = "actor"
    PROCESS = "process"
    DATA_STORE = "data_store"
    DATA_FLOW = "data_flow"
    TRUST_BOUNDARY = "trust_boundary"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ThreatStatus(str, Enum):
    OPEN = "Open"
    MITIGATED = "Mitigated"
    NOT_APPLICABLE = "NA"


class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class ControlStatus(str, Enum):
    ASSUMED = "assumed"
    ACTIVE = "active"
    SUGGESTED = "suggested"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    RETIRED = "retired"
    WONT_DO = "wont_do"


@dataclass
class DFDItem:
    id: str
    name: str
    type: DFDItemType
    description: str = ""
    source: Optional[str] = None
    destination: Optional[str] = None
    protocol: str = "HTTP"
    encrypted: bool = False
    is_trust_boundary: bool = False
    trust_zone: str = "default"
    privilege_level: str = ""
    stores_credentials: bool = False


@dataclass
class Threat:
    id: str
    title: str
    description: str
    severity: Severity
    status: ThreatStatus = ThreatStatus.OPEN
    model_type: str = "STRIDE"
    type: str = ""
    mitigation: str = ""
    score: str = ""
    cwe: str = ""
    affected_components: List[str] = field(default_factory=list)


@dataclass
class Control:
    id: str
    title: str
    description: str
    status: ControlStatus = ControlStatus.SUGGESTED
    priority: str = "medium"
    threat_ids: List[str] = field(default_factory=list)


@dataclass
class Risk:
    id: str
    title: str
    description: str
    likelihood: str = "possible"
    impact: str = "moderate"
    score: int = 0
    level: RiskLevel = RiskLevel.MEDIUM
    threat_ids: List[str] = field(default_factory=list)
    impact_description: str = ""


@dataclass
class Diagram:
    title: str
    diagram_type: str = "STRIDE"
    description: str = ""
    version: str = "2.0.0"
    items: List[DFDItem] = field(default_factory=list)
    threats: List[Threat] = field(default_factory=list)


@dataclass
class ThreatModel:
    title: str
    owner: str = ""
    description: str = ""
    version: str = "1.0.0"
    diagrams: List[Diagram] = field(default_factory=list)
    contributors: List[str] = field(default_factory=list)
    reviewer: str = ""
    controls: List[Control] = field(default_factory=list)
    risks: List[Risk] = field(default_factory=list)
