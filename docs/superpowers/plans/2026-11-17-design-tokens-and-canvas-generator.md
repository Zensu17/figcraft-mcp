# Design Tokens and Canvas Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide standard design token assets (`tokens.json`), a programmatic API and interactive FigCraft canvas generator (`tokens.py`), and bilingual documentation with zero emojis.

**Architecture:** A centralized design token JSON schema paired with a pure Python helper that queries values and connects to FigCraft (via port 1984 or CLI) to render live swatches, buttons, and badges directly on the desktop canvas.

**Tech Stack:** Python 3.8+ (standard library: `json`, `argparse`, `pathlib`, `socket`, `subprocess`), Markdown.

**Spec:** `docs/superpowers/specs/2026-11-17-design-tokens-and-canvas-generator-design.md`

## Global Constraints

- Absolute prohibition of emojis and emoticon glyphs across all console output, scripts, and documentation.
- Zero third-party Python dependencies (must run on vanilla Python 3.8+).
- Clean fallback: if FigCraft GUI is not running, `tokens.py` provides clear instructions or launches headless CLI.
- No hardcoded personal user paths.

## Review Focus

- Emojis appearing in stdout/stderr during CLI execution.
- Missing color shades in `tokens.json` (50 through 950 must be complete for all 7 palettes).
- Discrepancies between `TOKENS.md` and `TOKENS.id.md`.
- Canvas generator creating overlapping or unparented layers in FigCraft.
- Accurate export of `tailwind.config.js` theme extensions.

---

### Task 1: Create Design Tokens Data File (`tokens.json`)

**Files:**
- Create: `D:\Code\figcraft-mcp\tokens.json`

**Interfaces:**
- Produces: JSON database of colors, spacing, radius, typography.

- [ ] **Step 1: Write `tokens.json`**
  Include:
  - Colors: `slate`, `zinc`, `indigo`, `sky`, `emerald`, `amber`, `rose` (shades 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950).
  - Spacing: scale 0 to 16 (`0`, `4`, `8`, `12`, `16`, `20`, `24`, `32`, `40`, `48`, `64`).
  - Radius: `none` (0), `sm` (2), `default` (4), `md` (6), `lg` (8), `xl` (12), `2xl` (16), `3xl` (24), `full` (9999).
  - Typography: `xs` (12), `sm` (14), `base` (16), `lg` (18), `xl` (20), `2xl` (24), `3xl` (30), `4xl` (36).
  - Font weights: `normal` (400), `medium` (500), `semibold` (600), `bold` (700), `extrabold` (800).

- [ ] **Step 2: Verify JSON syntax**
  Validate with `python -m json.tool tokens.json > nul`.

- [ ] **Step 3: Commit**
  Run: `git add tokens.json && git commit -m "feat: add standard design tokens dictionary tokens.json"`

---

### Task 2: Implement Token API and Canvas Generator (`tokens.py`)

**Files:**
- Create: `D:\Code\figcraft-mcp\tokens.py`

**Interfaces:**
- Consumes: `tokens.json`.
- Produces: Python token querying functions and interactive CLI for FigCraft canvas generation.

- [ ] **Step 1: Write `tokens.py`**
  Implement:
  - Token lookup API: `get_color(query)`, `get_spacing(key)`, `get_radius(key)`, `get_typography(key)`.
  - Export function: `export_tailwind_theme()`.
  - FigCraft Canvas Controller:
    - Helper to send commands via loopback TCP socket (port 1984) or `figcraft-cli mcp`.
    - `render_palette_swatch(palette_name)`: draws a grid of color swatch cards with hex labels.
    - `render_starter_buttons()`: draws Primary, Secondary, Outline, and Danger buttons with standard padding and radius.
    - `render_starter_badges()`: draws Success, Warning, Danger, and Info status badges.
  - CLI parser: `--palette`, `--starter-buttons`, `--starter-badges`, `--export-tailwind`, `--list`.
  - Zero emojis in all outputs.

- [ ] **Step 2: Test `tokens.py` lookup and commands**
  Run: `python tokens.py --list` and `python tokens.py --export-tailwind`.

- [ ] **Step 3: Commit**
  Run: `git add tokens.py && git commit -m "feat: add tokens helper and canvas generator tokens.py"`

---

### Task 3: Create Bilingual Documentation and Update Skills

**Files:**
- Create: `D:\Code\figcraft-mcp\TOKENS.id.md`
- Create: `D:\Code\figcraft-mcp\TOKENS.md`
- Modify: `D:\Code\figcraft-mcp\skills\figcraft-designer\SKILL.md`
- Modify: `D:\Code\figcraft-mcp\README.md`
- Modify: `D:\Code\figcraft-mcp\README.id.md`

**Interfaces:**
- Produces: Complete reference guides for tokens in English and Indonesian, and informs AI of token standards.

- [ ] **Step 1: Write `TOKENS.id.md` and `TOKENS.md`**
  Document token tables, Python API usage, and CLI generator commands with zero emojis.

- [ ] **Step 2: Update `skills/figcraft-designer/SKILL.md`**
  Add design token standards pointing to `tokens.json` so AI uses these scales.

- [ ] **Step 3: Update README files**
  Add `tokens.py`, `tokens.json`, `TOKENS.md`, and `TOKENS.id.md` to repository structure and feature list.

- [ ] **Step 4: Commit**
  Run: `git add TOKENS.id.md TOKENS.md skills/figcraft-designer/SKILL.md README.md README.id.md && git commit -m "docs: add token documentation and update designer skill"`

---

### Task 4: Automated Verification and Review

**Files:**
- Verification via regex scan and execution test.

- [ ] **Step 1: Run regex emoji scan on all files**
  Confirm 0 emojis across all newly modified and created files.

- [ ] **Step 2: Test canvas generation command**
  Run `python tokens.py --list` to verify exit code 0.
