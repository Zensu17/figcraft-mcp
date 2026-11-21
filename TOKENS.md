# FigCraft Design Tokens, Themes & Canvas Templates

> Curated WCAG 2.2 AA design tokens, 4 intentional themes, CSS/Tailwind exporters, and 7 single-undo FigCraft canvas component templates.

**English** | [Baca dalam Bahasa Indonesia](TOKENS.id.md)

---

## Table of Contents
1. [Overview](#1-overview)
2. [Curated Themes (WCAG 2.2 AA Verified)](#2-curated-themes-wcag-22-aa-verified)
3. [Token Scales Reference](#3-token-scales-reference)
4. [CLI & MCP Tool Usage](#4-cli--mcp-tool-usage)
5. [Python API & Exporters](#5-python-api--exporters)

---

## 1. Overview

`tokens.json` (v2.0.0) and `tokens.py` form the visual foundation of `figcraft-mcp`. Every theme preset and semantic status pair is mathematically audited to pass **WCAG 2.2 AA (>= 4.5:1)** contrast, and every template builder emits valid single-undo FigCraft `batch` commands with proper `$ref` parent hierarchy and explicit `fill: "none"` structural wrappers.

---

## 2. Curated Themes (WCAG 2.2 AA Verified)

Each theme commits to 2-3 neutral surfaces and 1 deliberate focal accent:

| Theme Name | Mode | Surface / Elevated | Accent | Character |
| :--- | :--- | :--- | :--- | :--- |
| `editorial-paper` | light | `#FAFAF9` / `#FFFFFF` | `#B45309` | Warm ink-on-stone editorial clarity |
| `obsidian-studio` | dark | `#09090B` / `#18181B` | `#0369A1` | Neutral graphite studio with deep-sky focal accent |
| `slate-instrument` | dark | `#0F172A` / `#1E293B` | `#4F46E5` | Precision dark-slate interface system |
| `botanical-ledger` | light | `#F8FAFC` / `#FFFFFF` | `#047857` | High-clarity light operational & financial theme |

---

## 3. Token Scales Reference

### A. Color Palettes (Shades 50 to 950)
8 palettes: `slate`, `zinc`, `stone`, `indigo`, `sky`, `emerald`, `amber`, and `rose`.

### B. Semantic Status Tokens (`dark` & `light`)
Verified foreground/background/border triplets for `success`, `warning`, `danger`, and `info`.

### C. Spacing Scale (4px Grid)
`0` (0px), `1` (4px), `2` (8px), `3` (12px), `4` (16px), `5` (20px), `6` (24px), `8` (32px), `10` (40px), `12` (48px), `16` (64px), `20` (80px), `24` (96px).

### D. Border Radius Scale
`none` (0px), `sm` (2px), `default` (4px), `md` (6px), `lg` (8px), `xl` (12px), `2xl` (16px), `3xl` (24px), `full` (9999px).

---

## 4. CLI & MCP Tool Usage

### Via CLI (`tokens.py`)
```bash
# List all palettes, themes, and templates
python tokens.py --list

# Audit all 32 color pairs for WCAG 2.2 AA contrast
python tokens.py --audit-contrast

# Render component kits directly onto the FigCraft canvas
python tokens.py --palette stone
python tokens.py --starter-buttons --theme editorial-paper
python tokens.py --starter-badges --theme obsidian-studio
python tokens.py --segmented-control --theme slate-instrument
python tokens.py --data-table --theme botanical-ledger
python tokens.py --state-cards --theme obsidian-studio
python tokens.py --theme-board --theme editorial-paper

# Export tokens to Tailwind CSS or CSS Custom Properties
python tokens.py --export-tailwind
python tokens.py --export-css --theme editorial-paper
```

### Via MCP Tool (`figcraft_render_template` & `figcraft_get_tokens`)
AI assistants can render any template directly through MCP without running shell commands:
- `figcraft_render_template(template="state_cards", theme="editorial-paper")`
- `figcraft_render_template(template="data_table", theme="obsidian-studio", dry_run=true)` (returns batch JSON headlessly)
- `figcraft_get_tokens(category="themes", response_format="markdown")`

---

## 5. Python API & Exporters

```python
from tokens import (
    audit_theme_contrast,
    build_template_commands,
    export_css_variables,
    export_tailwind_theme,
    get_color,
    get_theme,
)

theme = get_theme("editorial-paper")
primary_hex = get_color("indigo-600")
batch_steps = build_template_commands("buttons", theme_name="obsidian-studio")
css_vars = export_css_variables("botanical-ledger")
```
