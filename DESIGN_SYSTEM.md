# CHERENKOV Design System

> **Brand Identity & Visual Language**  
> _Version 1.0 — The Forensic Reveal_

---

## 1. Brand Core

| Element | Value |
|---------|-------|
| **Name** | CHERENKOV |
| **Tagline** | The Forensic Reveal |
| **Voice** | Precise, sovereign, disciplined, technical |
| **Promise** | Find vulnerabilities, prove them, sign the evidence — all on your hardware |

---

## 2. Color System

### Primary Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--cyan-core` | `#00E0FF` | Primary accent, links, active states, cone reveal |
| `--violet-core` | `#9D00FF` | Secondary accent, validation tags, depth |
| `--dark-bg` | `#0A0E1A` | Background base (deep space) |
| `--dark-bg-alt` | `#02040A` | Background deeper (absolute black) |
| `--text-primary` | `#F0F1F5` | Primary text, headings |
| `--text-secondary` | `#B0B8C8` | Body text, descriptions |
| `--text-muted` | `#5A6A8A` | Metadata, captions, subdued elements |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--critical` | `#FF3355` | HIGH/CRITICAL findings |
| `--medium` | `#FFAA00` | MEDIUM findings |
| `--pass` | `#00E676` | Passing scans, validations |
| `--info` | `#00E0FF` | Informational |

---

## 3. Typography

| Context | Font | Weight | Size |
|---------|------|--------|------|
| **Wordmark / Logo** | `Inter` | 800 (ExtraBold) | 38px |
| **Heading 1** | `Inter` | 800 | 2.5rem |
| **Heading 2** | `Inter` | 700 | 1.75rem |
| **Heading 3** | `Inter` | 600 | 1.25rem |
| **Body** | `Inter` | 400 | 1rem |
| **Code/Mono** | `IBM Plex Mono` / `Consolas` | 400 | 0.875rem |
| **Tagline** | `Inter` | 500, uppercase, `0.35em` spacing | 0.85rem |

---

## 4. Logo System

### Primary Logo (SVG)
- **File:** `assets/cherenkov-logo.svg`
- **Symbol:** Hexagonal shield with conical reveal wavefront
- **Animation:** Shield pulse (3s), core glow (2s), data flicker (1.5s)
- **Minimum clear space:** Equal to the shield height on all sides

### Social Preview
- **File:** `assets/social-preview.svg`
- **Dimensions:** 1280×640px
- **Content:** Shield symbol + wordmark + tagline + feature tags + contact

---

## 5. Iconography

### System Icons
- Draw from the hexagonal / shield / wavefront visual language
- Use `--cyan-core` (#00E0FF) for active states, `--violet-core` (#9D00FF) for secondary
- Stroke width: 2px for UI, 6-8px for emphasis

### Validation States
- Passing: `#00E676` (green, checkmark)
- Failing: `#FF3355` (red, X)
- Warning: `#FFAA00` (amber, triangle)
- Running: `#00E0FF` (cyan, spinner)

---

## 6. Components

### Shields / Cards
- Background: `--dark-bg` with `--cyan-core` at 3-5% opacity
- Border: `--cyan-core` at 10-20% opacity, 1px
- Corner radius: 8px
- Padding: 24px

### Tags / Badges
- Background: token color at 10% opacity
- Border: token color at 30% opacity, 1px
- Text: token color
- Font: `IBM Plex Mono`, 12px
- Border radius: 4px
- Padding: 6px 12px

### Buttons
- **Primary:** Solid `--cyan-core` → `--violet-core` gradient
- **Secondary:** Border `--cyan-core` at 30%, transparent bg
- **Danger:** Solid `--critical`
- Border radius: 6px
- Font: `Inter` 600, 14px

---

## 7. Animation

| Element | Duration | Easing | Description |
|---------|----------|--------|-------------|
| Shield pulse | 3s | ease-in-out | Stroke opacity 0.6→1, width 6→8 |
| Core glow | 2s | ease-in-out | Drop-shadow 4px→12px, opacity 0.8→1 |
| Data flicker | 1.5s | step-end | Random opacity 0.4→1 |
| Loading spinner | 1s | linear | Rotating hexagon |

---

## 8. Tone of Voice

- **Discipline over hype** — "Built with discipline. Released with purpose."
- **Precision over breadth** — Focus on what CHERENKOV does, not what it could do
- **Sovereignty as default** — Zero-egress, air-gapped, your hardware
- **Technical honesty** — No overpromising; cite specific architectures (MEISSNER, ABLATION, TOKAMAK)

---

## 9. File Organization

```
assets/
├── cherenkov-logo.svg       # Primary animated logo
└── social-preview.svg       # Social sharing card (1280×640)

.github/
├── profile/
│   └── README.md            # Organization profile
├── FUNDING.yml              # Funding configuration
├── ISSUE_TEMPLATE/          # Issue templates
├── PULL_REQUEST_TEMPLATE/   # PR templates
└── workflows/               # CI/CD workflows

DESIGN_SYSTEM.md             # This file
README.md                    # Repository root README
```

---

<p align="center">
  <a href="https://cherenkov-security.com">cherenkov-security.com</a> ·
  <a href="mailto:support@cherenkov-security.com">support@cherenkov-security.com</a>
</p>
