# DESIGN.md | CHERENKOV Sovereign Security Design System

> **Source of Truth for Google Stitch & AI Agents**
> Identity: Sovereign, Precise, Air-Gapped, Forensic.
> Palette: Obsidian, Bismuth Purple, Cobalt Steel.

---

## 1. MISSION & VIBE
CHERENKOV is a "Fail-Closed" security intelligence platform. The design must reflect **uncompromising authority** and **forensic clarity**. It is not a "friendly" SaaS; it is a tactical command interface for national-scale security infrastructure.

**Vibe Keywords**: Tactical, Precise, Obsidian, High-Contrast, Glitch-Resistant, Mathematical.

---

## 2. DESIGN TOKENS (System Design Oriented)

### 🎨 Color Palette (The Sovereign Spectrum)
- **Primary (Bismuth Purple)**: `#8E44AD` | Use for AI-driven insights, active agent status, and primary calls to action.
- **Secondary (Cobalt Steel)**: `#4682B4` | Use for HUD elements, borders, brackets, and tactical data streams.
- **Background (Obsidian)**: `#0A0A0A` | The deep-canvas base. Use for all main surfaces.
- **Surface (Elevated)**: `#1A1D26` | Use for panels and cards.
- **Critical (Alert)**: `#FF4444` | Use only for verified vulnerabilities and fail-closed events.
- **Safe (Verity)**: `#00FF88` | Use for verified cryptographic proofs and "Tokamak" signatures.

### 🔡 Typography (The IBM/JetBrains Stack)
- **Headings**: `IBM Plex Sans` | Bold, tracking -0.01em.
- **Body**: `IBM Plex Sans Arabic` | Medium weight, optimized for RTL/LTR bilingual legibility.
- **Mono**: `JetBrains Mono` | Used for all technical traces, logs, and SHA-256 signatures.

### 📐 Spacing & Grid
- **Base Unit**: 4px grid.
- **Atomic Spacing**: 4px (xs), 8px (sm), 12px (md), 16px (lg), 24px (xl).
- **Layout**: 12-column tactical grid with 24px gutters.

---

## 3. ATOMIC COMPONENTS

### ⚛️ Atoms
- **CyberButton**: Chamfered corners (clip-path), gradient background (Bismuth to Deep Violet), 1px Cobalt border.
- **CyberBadge**: Monospaced text, background tint of severity color, high-contrast text.
- **PulseDot**: 8px circular indicator with CSS glow (box-shadow) for "Live" status.

### 🧬 Molecules
- **StatCard**: Large display value in Bismuth Purple, small label in Cobalt Steel, HUD-bracket corners.
- **VulnCard**: Severity-coded left border, expandable detail section, "View Proof" action button.

### 🦠 Organisms
- **TacticalPanel**: Elevated surface with `fx-grid` background, chamfered header, and integrated log stream.
- **ForensicHeader**: Global navigation with Brand Mark, Ablation Sync status, and active mission timer.

---

## 4. DESIGN PATTERNS (Stitch Specific)

### 🌊 Motion & FX
- **Scanlines**: Subtle vertical repeating linear gradient for CRT-effect.
- **Glitch**: Use `fx-glitch` on critical alerts to denote system stress.
- **Type-On**: All log entries must use a 1.2s typing animation to reflect real-time intelligence.

### 🛡️ System Design Constraints
- **Fail-Closed States**: If a data stream is interrupted, the component must turn "Obsidian-Grey" with a red pulse, denoting a broken perimeter.
- **Forensic Trace**: Every result must display its SHA-256 hash in `JetBrains Mono` at the bottom right.

---

## 5. GOOGLE STITCH COMMANDS (Prompts)

### COMMAND 01: The Core Dashboard
> "Stitch a high-fidelity 'Tactical Operations' dashboard for CHERENKOV. Use the DESIGN.md rules. Background must be Obsidian (#0A0A0A). Feature a 3:1 grid. Left: A large 'Operation Stream' panel with JetBrains Mono logs. Right: A 'Threat Intelligence' sidebar with severity-coded cards. Include a header with a Bismuth Purple logo and a 'ABLATION SAFE' pulse badge."

### COMMAND 02: The Forensic Proof View
> "Stitch a detail view for a specific vulnerability finding. Follow CHERENKOV Atomic patterns. Show a 'Proof of Concept' execution window with a command-line interface. Include a 'CHERENKOV Trace' section showing a cryptographic SHA-256 signature and a 'Redacted by ABLATION' label for all credential fields."

### COMMAND 03: The Network Shield (MEISSNER)
> "Stitch a network visualization component. Show a local subnet vs. the global internet. The boundary must be labeled '[MEISSNER]'. Use Cobalt Steel for authorized nodes and Bismuth Purple for the CHERENKOV monitoring agent. Visualize egress-control as a glowing barrier."
