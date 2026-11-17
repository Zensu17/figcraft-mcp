# Design Document: Standard Design Tokens and Canvas Starter Kit (Suggestion 4)

Date: 2026-11-17
Topic: Standard Design Tokens and Canvas Generator (`tokens.json` and `tokens.py`)
Status: Proposed

## 1. Intent and Why
Currently, when AI creates components or when users build UI on the FigCraft canvas, colors, border radii, and padding values are chosen ad-hoc. Providing a structured, standard design token catalog (matching Tailwind CSS and modern UI scales) along with a canvas generator script allows AI and developers to render consistent design token swatches and reusable component foundations (buttons, badges) directly onto the FigCraft canvas with a single command.

## 2. Goals, Non-Goals, and Anti-Goals
- Goals:
  - Create `tokens.json`: A comprehensive design token dictionary containing standard color palettes (Slate, Gray, Zinc, Indigo, Sky, Emerald, Amber, Rose) in shades 50 to 950, standard spacing scale (4px to 64px), border radius scale (0px to 24px, 9999px), and typography scales.
  - Create `tokens.py`: A standard-library Python utility that provides:
    1. Python API to query tokens: `get_color()`, `get_spacing()`, `get_radius()`, `get_typography()`.
    2. CLI Canvas Generator:
       - `python tokens.py --palette <name>`: Draws an aesthetic color swatch card on the live FigCraft canvas.
       - `python tokens.py --starter-buttons`: Draws standard button variants (Primary, Secondary, Outline, Danger) on the canvas.
       - `python tokens.py --starter-badges`: Draws standard status badges (Success, Warning, Danger, Info) on the canvas.
       - `python tokens.py --export-tailwind`: Outputs a ready-to-paste `theme.extend` snippet for `tailwind.config.js`.
  - Create bilingual reference guides: `TOKENS.md` (English) and `TOKENS.id.md` (Bahasa Indonesia).
  - Update `skills/figcraft-designer/SKILL.md` to instruct AI assistants to utilize these tokens.
  - Link token guides in `README.md` and `README.id.md`.
  - Strict constraint: 100% zero emojis across all code, CLI outputs, and documentation.
- Non-Goals:
  - Third-party Python dependencies (must remain 100% vanilla Python).
  - Replacing or altering the core MCP bridge logic in `bridge.py`.
- Anti-Goals:
  - Using emojis or graphical symbols.
  - Hardcoding personal user paths.

## 3. Constraints
- Pure Python 3.8+ standard library only (`json`, `sys`, `os`, `pathlib`, `argparse`, `socket`, `subprocess`).
- Strictly zero emojis in code, console outputs, and documentation.
- Non-destructive execution: canvas generation creates new named frames without altering existing layers.

## 4. Approaches Considered
- Approach A: Static JSON Token Library (`tokens.json` & docs only).
  - Rejected: Passive; does not provide interactive generation onto the FigCraft canvas.
- Approach B: Programmable Token Helper & Canvas Generator (`tokens.py` + `tokens.json` + `TOKENS.md` / `TOKENS.id.md`) (Chosen).
  - Provides a complete Design System Starter Kit with live canvas rendering capability.

## 5. Specification of Deliverables

### File: `tokens.json`
- Colors: `slate`, `zinc`, `indigo`, `sky`, `emerald`, `amber`, `rose` (shades 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950).
- Spacing: `0` (0px), `1` (4px), `2` (8px), `3` (12px), `4` (16px), `5` (20px), `6` (24px), `8` (32px), `10` (40px), `12` (48px), `16` (64px).
- Radius: `none` (0px), `sm` (2px), `default` (4px), `md` (6px), `lg` (8px), `xl` (12px), `2xl` (16px), `3xl` (24px), `full` (9999px).
- Typography: `xs` (12px), `sm` (14px), `base` (16px), `lg` (18px), `xl` (20px), `2xl` (24px), `3xl` (30px), `4xl` (36px).

### File: `tokens.py`
- Programmatic helper:
  - `load_tokens() -> dict`
  - `get_color(name_or_key: str) -> str`
  - `get_spacing(key: str) -> int`
  - `get_radius(key: str) -> int`
- Canvas generation functions:
  - Connects to FigCraft control port (1984) via loopback socket or CLI bridge.
  - `render_palette_swatch(palette_name: str)`
  - `render_starter_buttons()`
  - `render_starter_badges()`
- CLI argument parser (`--palette`, `--starter-buttons`, `--starter-badges`, `--export-tailwind`, `--list`).

### Files: `TOKENS.md` and `TOKENS.id.md`
- Token lookup table and naming conventions.
- CLI usage guide for rendering components to the FigCraft canvas.
- Code examples for importing `tokens.py` in custom scripts.

### Skill Update: `skills/figcraft-designer/SKILL.md`
- Add section pointing AI to `tokens.json` for consistent styling.

## 6. Implementation Sequence
1. Create `tokens.json` with standard design scales.
2. Create `tokens.py` with lookup functions, CLI runner, and FigCraft canvas generator.
3. Test `tokens.py` locally (verify lookup and canvas generation).
4. Create `TOKENS.id.md` (Bahasa Indonesia) and `TOKENS.md` (English).
5. Update `skills/figcraft-designer/SKILL.md` to reference standard tokens.
6. Update `README.md` and `README.id.md` to reference the tokens toolkit.
7. Verify zero emojis across all newly created and updated files.
8. Commit changes to git branch `main`.
