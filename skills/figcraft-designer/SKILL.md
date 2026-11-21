---
name: figcraft-designer
description: Expert interface designer for FigCraft. Use when the user asks to design, create, update, inspect, or export UI components, screens, or layouts in FigCraft.
---

# FigCraft Designer Skill

FigCraft is an open-source, pure-Rust collaborative interface design tool that speaks MCP natively.

## 1. Coordinate & Engine Rules (Mandatory)
- **Coordinates**: Page units (1 unit = 1 px at 100% zoom). X goes right, Y goes DOWN.
- **Parent Relative**: `x` and `y` are relative to the parent frame (or page if no parent).
- **Auto-Layout Alignment Enums**:
  - `mainAlign`: `"min"`, `"center"`, `"max"`, `"spaceBetween"`, `"spaceAround"`, `"spaceEvenly"`. Never use `"start"` or `"end"`.
  - `crossAlign`: `"min"`, `"center"`, `"max"`, `"baseline"`. Never use `"start"` or `"end"`.
  - When auto-layout is enabled on a parent frame, do NOT set manual `x`/`y` on its children.
- **MANDATORY: Transparent Layout Wrappers (`fill: "none"`)**:
  - Frames created without an explicit `fill` property default to solid opaque white (`#FFFFFF`).
  - Always set `fill: "none"` on structural layout wrappers (flex rows, button groups, header wrappers) unless an opaque surface card is intended.
- **Property Naming**:
  - Border: `stroke` (hex) and `strokeWeight` (number, NOT `strokeWidth`).
  - Typography: `fontSize` (number), `fill` (text hex color), and `fontStyle` (`"Bold"`, `"SemiBold"`, `"Medium"`, `"Regular"`). Do not use `fontWeight: 700`.

## 2. Visual Direction & Anti-Slop Craft Standards
- **Palette Discipline**: Commit to 2-3 neutral surfaces plus 1 deliberate focal accent (never scatter 5+ accent hues or default blue-purple gradients across every element).
- **Curated Themes (`tokens.json`)**: Prefer reading `figcraft://tokens` or calling `figcraft_get_tokens(category="themes")` to select an intentional theme (`editorial-paper`, `obsidian-studio`, `slate-instrument`, `botanical-ledger`).
- **WCAG 2.2 AA Contrast Floor**: Every normal text layer must meet >= 4.5:1 contrast against its direct background surface (>= 3.0:1 for 18px+ bold headings).
- **Content-Driven Hierarchy**:
  - Avoid generic template chrome: no decorative capsule eyebrows above headings, no fabricated statistics or fake testimonials, no emoji clutter in UI labels, and no identical copy-paste card grids.
  - Use active-verb, specific button copy ("Save changes", "Export CSV", "Delete project") instead of vague labels ("Submit", "Click here").
  - Include real UI states (Empty, Loading, Error) that state the cause and next action for data-driven screens.
  - Keep interactive buttons and touch targets at least 44px tall where mobile/touch usability applies.

## 3. Workflow & Single-Undo Templates
1. **Reusable Templates**: Use MCP tool `figcraft_render_template` (`buttons`, `badges`, `segmented_control`, `data_table`, `state_cards`, `theme_board`, `palette_swatch`) to drop WCAG-verified component kits onto the canvas in a single undo step.
2. **Custom Multi-Layer Layouts**: Combine steps with `batch` (`onError: "abort"`) and `{"$ref": "stepName"}` parent references.
3. **Visual Self-Verification**: Always call `screenshot` after creating or modifying frames to verify contrast, spacing, alignment, and absence of opaque wrapper leaks.
