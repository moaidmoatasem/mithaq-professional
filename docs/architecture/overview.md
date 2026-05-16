# CHERENKOV Architecture

This document describes the architectural principles and design patterns of the CHERENKOV project.

## 1. The Trident of Truth
CHERENKOV operates on the "Trident of Truth" framework:
- **MEISSNER:** Network enforcement and proxy layer. Controls external access.
- **ABLATION:** Data redaction and anonymization. Protects sensitive information.
- **TOKAMAK:** Sandboxed validation. Ensures untrusted code and scanners are executed safely.

## 2. Clean Architecture
The project strictly enforces a Clean Architecture pattern, isolating concerns across layers:
- **Persistence Layer (`ResultStore`):** Manages all state and data storage. Must not be accessed directly by CLI or external scripts.
- **API Layer (`orchestration_api.py`):** The single entry point for routing, business logic, and orchestration. All external clients (CLI, Web Dashboards) MUST use this layer.
- **CLI/Client Layer:** Thin wrappers that interact only with the API layer.

## 3. Agent Governor and Cognitive Routing
CHERENKOV leverages an **Agent Governor** pattern to route tasks among various internal AI agents dynamically. Agents are assigned specific **roles** and **rules**, and their outputs are moderated by the governor to ensure safety, alignment, and execution of the given flow.

## 4. Scanners Plugin Architecture
Scanners must inherit from the `BaseScanner` class (`src/cherenkov/core/base_scanner.py`).
This guarantees:
- Auto-discovery via the `ScannerRegistry`.
- Standardized execution through the `scan()` interface.
- Consistent output formatting (`ScanResult`).
