# CHERENKOV UI/UX Requirements
**Classification: Sovereign Design Specification**
**Version: 1.0 | Status: Phase 2 Active | Source: DESIGN.md + CHERENKOV_SSOT.md**

---

## 1. DESIGN AUTHORITY

This document is the ground truth for all front-end implementation. Any design decision not covered here must reference `DESIGN.md` and `CHERENKOV_SSOT.md` before proceeding. AI coders must adhere to the **Lexicon Replacements** defined in SSOT §5.

---

## 2. DESIGN TOKENS (Canonical Reference)

> Source: `stylesheets/tokens.css` — Do not override; extend only.

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--cherenkov-accent` | `#2b7fff` | Primary brand, CTAs, H1, focus rings |
| `--hud-cyan` | `#00e5ff` | Data streams, telemetry, HUD borders |
| `--hud-amber` | `#ffb020` | Attention, scanning state, target labels |
| `--hud-mint` | `#00ff88` | Verified safe states, TOKAMAK-signed |
| `--bg-canvas` | `#0A0A0A` | Deep Obsidian — all main surfaces |
| `--bg-surface` | `#12141a` | Panels, cards |
| `--bg-elevated` | `#1a1d26` | Inputs, chips, inner cards |
| `--sev-critical` | `#ff4444` | Verified anomalies, CRITICAL/HIGH findings |
| `--sev-medium` | `#ffaa00` | MEDIUM findings |
| `--sev-low` | `#ffff00` | LOW findings |
| `--fg1` | `#ffffff` | Primary text |
| `--fg2` | `#b8b8b8` | Secondary/label text |
| `--fg3` | `#7a7a7a` | Placeholder/tertiary |

### Typography

| Role | Family | Weight | Token |
|---|---|---|---|
| All headings | IBM Plex Sans | Bold | `--font-sans` |
| Body / labels | IBM Plex Sans | 400–600 | `--font-sans` |
| Arabic text | IBM Plex Sans Arabic | 400–600 | `--font-arabic` |
| All mono (logs, hashes, code) | JetBrains Mono | 400–700 | `--font-mono` |

> **Air-Gap Requirement:** Fonts MUST be self-hosted in `web/fonts/`. The current CDN `@import` in `tokens.css` must be replaced before air-gapped deployment.

### Spacing Grid

4px base unit. Use tokens `--sp-xs` (4px) through `--sp-5xl` (64px). Never use arbitrary pixel values.

---

## 3. PAGE STRUCTURE & LAYOUT

### 3.1 Global Layout

```
┌─────────────────────────────────────────────────────────┐
│ [FORENSIC HEADER] │
├──────────────────────────────────┬──────────────────────┤
│ │ │
│ TACTICAL OPERATIONS PANEL │ THREAT INTEL PANEL │
│ (75% — 3fr) │ (25% — 1fr) │
│ │ │
│ - State Machine Visualizer │ - Target HUD │
│ - Operation Stream (Log) │ - VulnCard list │
│ - System Capacity Meter │ - Cherenkov Trace │
│ │ │
└──────────────────────────────────┴──────────────────────┘
```

- Grid: `grid-template-columns: 3fr 1fr`
- Gap: `--sp-xl` (20px)
- Max-width: `--container-max` (1200px), centered
- Background: `cyber-canvas fx-grid` (Obsidian + animated HUD grid)

### 3.2 Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| `> 1024px` | Full 3:1 two-column layout |
| `768px–1024px` | Stack to single column; sidebar moves below |
| `< 768px` | Mobile-optimized single column, collapsible sidebar |

---

## 4. COMPONENT SPECIFICATIONS

### 4.1 ATOM: CyberButton
**File:** `components/atoms/CyberButton.js`

| Prop | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique DOM ID |
| `text` | string | yes | Button label |
| `variant` | `'primary'`/`'ghost'`/`'danger'` | no | Default: `'primary'` |
| `onClick` | function | no | Click handler |
| `disabled` | boolean | no | Default: false |

**Visual:**
- Chamfered top-right corner via `clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, ...)`
- Primary: Mint gradient (`#00ff88 → #00cc66`), dark text `#001b0d`
- Ghost: Transparent + `1px solid rgba(0,255,136,0.5)`, mint text
- Danger: Red gradient (`#ff4444 → #cc2222`), white text
- Hover: `translateY(-1px)` + increased glow
- Disabled: `opacity: 0.6; cursor: wait`

**States:** default → hover → active → disabled → loading (text changes to `"EXECUTING..."`)

---

### 4.2 ATOM: CyberBadge
**File:** `components/atoms/CyberBadge.js`

| Prop | Type | Required | Description |
|---|---|---|---|
| `text` | string | yes | Badge label |
| `type` | `'safe'`/`'critical'`/`'high'`/`'medium'`/`'low'`/`'info'` | no | Default: `'safe'` |

**Visual:** `font-family: --font-mono`, uppercase, letter-spacing 0.04em. Color fills from severity token map.

---

### 4.3 ATOM: PulseDot
**File:** `components/atoms/PulseDot.js`

| Prop | Type | Required | Description |
|---|---|---|---|
| `color` | `'green'`/`'red'`/`'amber'`/`'cyan'` | no | Default: `'green'` |
| `label` | string | no | Accessible aria-label |

**Visual:** 8px circle, animated CSS `pulse` keyframes. 
- Green: ONLINE / ABLATION SAFE
- Red: FAIL-CLOSED / MEISSNER BREACH
- Amber: SCANNING / KINETIC ACTIVE
- Cyan: LATTICE SYNC

---

### 4.4 ATOM: StatCard
**File:** `components/molecules/StatCard.js`

| Prop | Type | Required | Description |
|---|---|---|---|
| `label` | string | yes | Uppercase HUD label |
| `value` | string/number | yes | Large display value |
| `id` | string | yes | DOM ID for dynamic updates |
| `accent` | string | no | Color token for value. Default: `--cherenkov-accent` |

**Visual:** Large mono value in accent color, small label in `--fg2`, `hud-bracket` corners.

---

### 4.5 MOLECULE: VulnCard
**File:** `components/molecules/VulnCard.js`

| Prop | Type | Required | Description |
|---|---|---|---|
| `title` | string | yes | Anomaly name |
| `severity` | `'critical'`/`'high'`/`'medium'`/`'low'`/`'safe'` | yes | Severity level |
| `score` | string | yes | CVSS score or custom score |
| `description` | string | no | Short description |
| `scanner` | string | no | Which scanner isolated it |
| `cve` | string | no | CVE identifier |
| `traceId` | string | no | Cherenkov Trace ID |
| `onViewProof` | function | no | Callback for Forensic Proof view |

**Visual:**
- Chamfered corners via `clip-path`
- Severity-coded `border-left: 3px solid <sev-color>`
- Critical/High: Left-gradient red tint background
- `reveal-up` entrance animation (`.55s`)
- Expandable: Click → reveals description, scanner, CVE, trace ID
- "VIEW PROOF" CyberButton (ghost variant) appears on expand
- Cursor: pointer

**Fail-Closed State:** If `traceId` is null, card shows `[UNVERIFIED]` badge in amber. Cannot be "VIEW PROOF"-able.

---

### 4.6 MOLECULE: StatGrid
**File:** `components/molecules/StatGrid.js` *(new — to be created)*

A responsive 2–4 column grid of `StatCard` atoms.

| Prop | Type | Description |
|---|---|---|
| `stats` | `StatCard[]` | Array of stat configs |

---

### 4.7 ORGANISM: ForensicHeader
**File:** `components/organisms/Header.js`

**Elements (left → right):**
1. **Brand Mark** — `CHERENKOV` in `--font-sans` bold, electric blue, glitch FX (`fx-glitch`, `data-text` attr)
2. **Mission Timer** — `JetBrains Mono`, format `HH:MM:SS`, live-incrementing from audit start
3. **MEISSNER Status** — `PulseDot` + label. States:
 - `MEISSNER: LOCKED` (green) — zero-egress enforced
 - `MEISSNER: PERMEABLE` (amber) — hybrid cloud mode active
 - `MEISSNER: BREACH` (red) — fail-closed triggered
4. **ABLATION Status** — `CyberBadge` type `safe`. States:
 - `ABLATION SYNCED` (safe/green)
 - `ABLATION ACTIVE` (amber, pulsing) — redaction in progress
 - `ABLATION FAILED` (critical) — triggers fail-closed

**Layout:** `display: flex; justify-content: space-between; align-items: center`
**Border:** `border-bottom: 1px solid --border-hud`

---

### 4.8 ORGANISM: TacticalOperationsPanel
**File:** `components/organisms/OperationsControl.js`

**Sub-sections (top → bottom):**
1. **Panel Header:** `h2` "Tactical Operations" + `▶ INITIATE SEQUENCE` CyberButton (primary)
2. **StatGrid:** `NODES MAPPED`, `PAYLOADS DELIVERED`, `ANOMALIES ISOLATED`, `TRACES SIGNED`
3. **Execution State Machine Visualizer** *(new):*
 ```
 [MONITORING] → [MEISSNER LOCKDOWN] → [ABLATION SWEEP] → [KINETIC ENGAGEMENT] → [TOKAMAK CONTAINMENT] → [TRACE SIGNED]
 ```
 - Connected by animated dashed lines (`fx-march`)
 - Active step: Bismuth purple glow + `fx-sweep` animation
 - Completed step: Mint green check + dim
 - Failed step: Critical red + glitch FX
4. **Operation Stream:** `JetBrains Mono` log container. Rules:
 - Each line appended with 1.2s type-on animation
 - Prefix: `[+]` for info, `[!]` for alerts (red), `[✓]` for verified (mint)
 - Auto-scroll to bottom
 - Max 500 lines, then oldest purged
 - Scrollable, height: fixed `320px`
5. **System Capacity Meter:** AIMD-driven `cyber-meter` bar
 - Label: `SWARM CAPACITY`
 - Color transitions: <30% = red, 30–70% = amber, >70% = mint

---

### 4.9 ORGANISM: ThreatIntelPanel *(new — missing)*
**File:** `components/organisms/ThreatIntelPanel.js`

**Sub-sections (top → bottom):**
1. **Target HUD Block:**
 - Label: `TARGET` in amber
 - Value: Target IP/hostname in `JetBrains Mono`
 - `hud-bracket` corners
2. **Vulnerability List:**
 - Label: `ANOMALIES ISOLATED`
 - Empty state: `No threats detected.` in `--fg3`, italic
 - Populated: Stack of `VulnCard` components, newest on top
 - Max visible: 6 (scroll after)
3. **Cherenkov Trace Block** (appears after audit):
 - Label: `CHERENKOV TRACE`
 - SHA-256 hash in `JetBrains Mono`, `--fs-micro`, truncated to 20 chars + `...`
 - Click to copy full hash
 - `Cryptographic Shred Receipt` link (opens Forensic Proof View)

---

### 4.10 TEMPLATE: MainLayout
**File:** `components/templates/MainLayout.js` *(exists as import, file missing)*

Accepts `{ header, content, sidebar }` and assembles the full page DOM structure:
- `<header>` at top
- `<main class="dashboard-grid">` with `content` (3fr) and `sidebar` (1fr)
- All wrapped in `<div class="cyber-canvas fx-grid">`

---

### 4.11 VIEW: Forensic Proof Detail
**Trigger:** "VIEW PROOF" button on an expanded VulnCard

**Implementation:** Full-screen modal overlay

**Elements:**
1. **Modal Header:** `CHERENKOV FORENSIC PROOF` title + `[ESC] CLOSE` ghost button
2. **Anomaly Summary:** Title, severity badge, scanner name, CVE
3. **PoC Execution Window:**
 - Dark terminal-style box (`bg-elevated`, `border: 1px solid --border-hud`)
 - Label: `TOKAMAK EXECUTION LOG`
 - `JetBrains Mono` content, line-by-line with type-on animation
4. **Redaction Block:**
 - Any credential fields shown as: `API_KEY: [REDACTED BY ABLATION ██████]`
 - Amber badge: `ABLATION PROTECTED`
5. **Evidence Section:**
 - `CHERENKOV TRACE ID:` full SHA-256 in mono
 - `TIMESTAMP:` ISO 8601
 - `SCANNER:` which module
 - `EXECUTION MODE:` LOCAL-ONLY / HYBRID
6. **Action Footer:**
 - `EXPORT TRACE` (downloads JSON)
 - `INITIATE CRYPTOGRAPHIC SHRED` (danger button, requires confirm)

---

## 5. USER SCENARIOS

### Scenario 1: First Contact — Initiating a Sovereign Audit
**Actor:** Security Analyst
**Entry State:** Dashboard loaded, no active audit. All stats at 0. Log shows `AWAITING COMMAND...`

**Flow:**
1. Analyst enters target IP/hostname in the target input field in `ThreatIntelPanel`.
2. Analyst clicks `▶ INITIATE SEQUENCE`.
3. **UI Response:**
 - Button disables, text changes to `EXECUTING...`
 - MEISSNER status transitions to `MEISSNER: LOCKED` (green → confirmed)
 - State Machine step 1 (`MONITORING`) activates with purple glow
 - Operation Stream logs: `[+] Initializing CHERENKOV Operation...`
 - State Machine advances: step 2 `MEISSNER LOCKDOWN` activates
 - Log: `[+] MEISSNER perimeter sealed. Zero-egress enforced.`
4. If cloud (TENSOR) is needed:
 - MEISSNER status transitions to `MEISSNER: PERMEABLE` (amber)
 - ABLATION badge becomes `ABLATION ACTIVE` (pulsing amber)
 - Log: `[+] ABLATION sweep in progress. Sanitizing breadcrumbs for TENSOR.`
 - State Machine: step 3 `ABLATION SWEEP` activates
5. KINETIC engagement:
 - State Machine: step 4 `KINETIC ENGAGEMENT` activates
 - `NODES MAPPED` counter increments with each discovered node
 - Log: `[!] Anomaly detected: SQL Injection on endpoint /api/auth` (red)
6. TOKAMAK validation:
 - State Machine: step 5 `TOKAMAK CONTAINMENT` activates
 - `ANOMALIES ISOLATED` counter increments
 - VulnCard appears in ThreatIntelPanel with `reveal-up` animation
7. Completion:
 - State Machine: step 6 `TRACE SIGNED` activates (mint green, fully lit)
 - `TRACES SIGNED` counter increments
 - Cherenkov Trace block appears with SHA-256
 - Button re-enables: `RE-ENGAGE`
 - MEISSNER status returns to `MEISSNER: LOCKED`

**Success Criteria:** All 6 state machine steps complete. At least 1 VulnCard visible. Trace ID populated.

---

### Scenario 2: Fail-Closed Event
**Actor:** System (triggered by ABLATION failure or network drop)
**Trigger:** WebSocket disconnects OR ABLATION returns unsafe

**Flow:**
1. Mid-audit, connection drops.
2. **UI Response (within 2 seconds):**
 - All `PulseDot` indicators flip to red, pulsing rapidly
 - `TacticalOperationsPanel` entire border flashes `sev-critical` (red glow)
 - Log: `[!] FAIL-CLOSED EVENT: Perimeter breach detected. Operation suspended.` (red, pulsing)
 - MEISSNER badge: `MEISSNER: BREACH` in critical red
 - State Machine current step turns red with glitch FX
 - Background tint shifts to subtle red overlay
 - `INITIATE SEQUENCE` button becomes `FAIL-CLOSED` (disabled, danger variant)
3. Recovery: Reconnect button appears: `↺ RESTORE PERIMETER`
4. On reconnect: all indicators restore, log shows `[✓] MEISSNER perimeter restored.`

**Success Criteria:** Fail-closed transition visible within 2s. No partial data displayed. Recovery path clear.

---

### Scenario 3: Viewing Forensic Proof
**Actor:** Security Analyst reviewing a critical finding
**Entry State:** VulnCard for "Unauthenticated RCE" visible in ThreatIntelPanel

**Flow:**
1. Analyst clicks VulnCard.
2. Card expands: description, scanner name (`kinetic-scanner-v1`), CVE ID, trace ID.
3. `VIEW PROOF` ghost button appears.
4. Analyst clicks `VIEW PROOF`.
5. **UI Response:**
 - Full-screen modal overlays dashboard with dark background
 - Header: `CHERENKOV FORENSIC PROOF — CT-2026-001`
 - TOKAMAK log animates line by line (type-on)
 - Credential fields show `[REDACTED BY ABLATION]` with amber badge
 - Full SHA-256 trace visible, click-to-copy
6. Analyst clicks `EXPORT TRACE` → downloads `cherenkov-trace-CT-2026-001.json`
7. Analyst closes modal with `[ESC] CLOSE` or Escape key.

**Success Criteria:** Modal is accessible. Export works. ABLATION redaction clearly communicated.

---

### Scenario 4: Multi-Anomaly Triage
**Actor:** Security Analyst with 5+ findings
**Entry State:** Audit complete, 5 VulnCards in ThreatIntelPanel

**Flow:**
1. Analyst sees severity-ordered VulnCard list (critical first).
2. Scrolls through list (ThreatIntelPanel is scrollable, max 6 visible).
3. Filters by severity (filter chips: ALL | CRITICAL | HIGH | MEDIUM | LOW).
4. Clicks each card to expand and review.
5. Uses `VIEW PROOF` on CRITICAL findings.

**Success Criteria:** Cards are sorted by severity. Filter chips work. Scroll is smooth. Modal loads correctly for any card.

---

### Scenario 5: AEGIS Cognitive Loop Intercept
**Trigger:** KINETIC attempts same exploit 3 times (AEGIS 3-strike rule)
**Entry State:** Audit in `KINETIC ENGAGEMENT` state

**Flow:**
1. Loop detected on backend.
2. **UI Response:**
 - Log: `[!] [AEGIS] Cognitive loop detected on target: 192.168.1.104 — Terminating thread.` (red)
 - State Machine `KINETIC ENGAGEMENT` step pulses amber (warning, not fail)
 - New log: `[+] [AEGIS] Forcing new attack strategy via TENSOR.`
 - State Machine reverts to step 3 `ABLATION SWEEP` to re-plan

**Success Criteria:** Loop is surfaced to user clearly. Audit does not halt; it re-plans.

---

## 6. VISUAL FX RULES

| Effect | CSS Class | When to Use |
|---|---|---|
| Animated HUD grid | `.fx-grid` | Canvas background only |
| CRT scanlines | `.fx-scanlines` | Overlay on log/terminal containers |
| Sweep scan line | `.fx-sweep` | Active panels during scanning state |
| Glitch | `.fx-glitch` | Brand mark only; critical alerts |
| Card entrance | `.reveal-up` | All VulnCards, modals |
| Slide-in | `.fx-enter` | Modal/overlay entrance |
| Marching dashes | `.fx-march` | State machine connectors |
| Blinking caret | `.fx-caret` | End of active log stream |
| Pulse dot | `.fx-pulse` | All status indicators |
| Data stream | `.fx-stream` | Background of log container |
| Type-on | `.type-on` | Headings only (short strings) |
| Neon text | `.neon` / `.neon-soft` | Active state labels, SAFE status |
| Neon red | `.neon-red` | CRITICAL/BREACH alerts |

**Restraint Rules:**
- Max 3 animated FX visible simultaneously in any viewport region
- Never apply `.fx-glitch` to body content — brand mark and critical alerts only
- `.neon` is reserved for confirmed-safe states. Use `.neon-soft` for ambient aesthetics
- All motion must respect `prefers-reduced-motion` media query

---

## 7. STATE MAP — UI SYSTEM STATES

| State | MEISSNER Badge | ABLATION Badge | Pulse Color | Log Prefix | Panel Border |
|---|---|---|---|---|---|
| IDLE | `LOCKED` (green) | `SYNCED` (green) | Green | `AWAITING COMMAND...` | Default HUD |
| SCANNING | `LOCKED` (green) | `SYNCED` (green) | Amber | `[+]` | Sweep FX active |
| CLOUD QUERY | `PERMEABLE` (amber) | `ACTIVE` (amber, pulsing) | Amber | `[+] ABLATION sweep...` | Amber HUD |
| KINETIC ACTIVE | `LOCKED` (green) | `SYNCED` (green) | Amber | `[!]` alerts possible | Sweep FX active |
| TOKAMAK PROVING | `LOCKED` (green) | `SYNCED` (green) | Cyan | `[+] Executing kinetic proof...` | Cyan sweep |
| COMPLETE | `LOCKED` (green) | `SYNCED` (green) | Green | `[✓] Cherenkov Trace Signed.` | Mint glow |
| FAIL-CLOSED | `BREACH` (red) | `FAILED` (red) | Red | `[!] FAIL-CLOSED EVENT` | Red glow + glitch |
| LOOP DETECTED | `LOCKED` (green) | `SYNCED` (green) | Amber | `[!] [AEGIS] Loop intercepted` | Amber warning |

---

## 8. ACCESSIBILITY REQUIREMENTS

- All interactive elements must have `aria-label` or visible text label
- Focus ring: `--ring-focus` on all buttons and interactive elements
- Color is never the sole differentiator — severity uses icon + text + color
- Escape key closes all modals
- Log container is `aria-live="polite"` (non-critical) / `aria-live="assertive"` for FAIL-CLOSED events
- `prefers-reduced-motion`: All CSS animations must have `@media (prefers-reduced-motion: reduce)` override

---

## 9. OPEN IMPLEMENTATION GAPS (Action Required)

| Item | Status | Priority |
|---|---|---|
| `MainLayout.js` template file missing | ❌ Not created | P0 |
| `ThreatIntelPanel.js` organism missing | ❌ Not created | P0 |
| `StatGrid.js` molecule missing | ❌ Not created | P1 |
| State Machine Visualizer component | ❌ Not created | P1 |
| Forensic Proof Modal component | ❌ Not created | P1 |
| Target input field in ThreatIntelPanel | ❌ Not created | P1 |
| Severity filter chips | ❌ Not created | P2 |
| Mission Timer in Header | ❌ Not created | P2 |
| Click-to-copy SHA-256 | ❌ Not created | P2 |
| Fail-Closed UI state wiring | ❌ Not implemented | P0 |
| Self-hosted fonts (air-gap) | ❌ CDN import active | P1 |
| `prefers-reduced-motion` overrides | ❌ Not implemented | P2 |
| Export Trace (JSON download) | ❌ Not implemented | P2 |

---

*CHERENKOV: Accuracy is the root of sovereignty.*
