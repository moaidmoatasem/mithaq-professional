# CHERENKOV Code of Conduct | Sovereign Security Integrity

## 1. Our Pledge
In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to making participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## 2. Sovereign Standards
As a security project focused on **Sovereignty (Ablation)**, we adhere to a higher standard of technical integrity:

- **Local-First**: We prioritize local computation over cloud-dependent services.
- **Fail-Closed**: Security features must fail-closed. A system that cannot guarantee safety must halt.
- **Forensic Truth**: Findings must be backed by evidence (Tokamak). We do not report "guesses"; we report "proofs."
- **Privacy by Design**: We never transmit PII, credentials, or proprietary source code to external entities without explicit, redacted (Ablation) consent.

## 3. Our Responsibilities
Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

Maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct, or to ban temporarily or permanently any contributor for other behaviors that they deem inappropriate, threatening, offensive, or harmful.

## 4. Scope
This Code of Conduct applies both within project spaces and in public spaces when an individual is representing the project or its community. Examples of representing a project or community include using an official project e-mail address, posting via an official social media account, or acting as an appointed representative at an online or offline event. Representation of a project may be further defined and clarified by project maintainers.

## 5. Agent and Human Interactions
CHERENKOV relies heavily on AI agents. The following rules govern interactions:
- **Agent Autonomy:** Agents are permitted to operate autonomously within predefined bounds (e.g., executing established scanners, writing standard code).
- **Human-in-the-Loop (HITL):** Critical security changes (e.g., modifications to TOKAMAK, ABLATION, TOKAMAK, or core orchestration) **REQUIRE** explicit human review and cryptographic approval. Agents must halt and wait for this approval.
- **Agent Handoffs:** Agents must communicate clearly defined state and context during handoffs, adhering to the `AgentState` schema to prevent context pollution.

## 6. Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated and will result in a response that is deemed necessary and appropriate to the circumstances. The project team will maintain confidentiality with regard to the reporter of an incident. 

---
*CHERENKOV: Accuracy is the root of sovereignty.*
