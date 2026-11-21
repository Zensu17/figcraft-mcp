# FigCraft Universal MCP Bridge

> Connect any AI coding assistant to FigCraft with full MCP primitives, multi-framework Design-to-Code, WCAG-verified templates, and STRIDE boundary security.

**English** | [Baca dalam Bahasa Indonesia](README.id.md)

---

## Overview

FigCraft Universal MCP Bridge connects modern AI coding assistants (Google AntiGravity, OpenCode CLI, Cursor, and Claude Desktop) directly to FigCraft, an open-source visual interface design tool written in pure Rust.

Beyond a simple pass-through proxy, the bridge operates as an **MCP Protocol Middleware** (100% Python standard library, zero external dependencies) that provides:
1. **Text-to-UI & Curated Templates**: Draw custom layouts or drop WCAG 2.2 AA verified component kits onto the FigCraft canvas in a single undoable step.
2. **Multi-Framework Design-to-Code**: Inspect canvas frames, extract semantic UI tokens and typed component props (Code Connect pattern), and generate React + Tailwind CSS, Vue 3 SFC, Flutter, or semantic HTML/CSS code.
3. **MCP Resources, Prompts & Guardrails**: Expose design tokens, engine guidelines, and compact semantic ASTs directly via MCP while automatically normalizing common LLM property mismatches.
4. **STRIDE Boundary Hardening**: Validate JSON-RPC frame sizes/nesting depth, enforce unprivileged loopback ports, block UNC/traversal file paths, and sanitize generated frontend code against XSS and CSS injection.

---

## Key Features

- **On-Demand Lazy Launch**: Boots silently in headless mode (under 50 ms, no GUI window opened on CLI startup). Launches the FigCraft desktop GUI automatically only when a live canvas tool or live canvas resource (`figcraft://document`, `figcraft://node/...`, `figcraft://canvas/semantic`) is requested.
- **Full MCP Primitives Middleware (`mcp_primitives.py`)**:
  - **Custom Resources**: `figcraft://tokens`, `figcraft://guidelines`, `figcraft://canvas/semantic`, and template `figcraft://node/{id}/semantic`.
  - **Custom Prompts**: `figcraft_dashboard_card`, `figcraft_auth_screen`, `figcraft_navbar`, and `figcraft_design_to_code`.
  - **Bridge Workflow Tools**: `figcraft_get_tokens`, `figcraft_extract_semantic_ast`, `figcraft_generate_code`, and `figcraft_render_template`.
  - **Automatic Engine Guardrails**: Normalizes `strokeWidth` -> `strokeWeight`, `start`/`end`/`space-between` -> `min`/`max`/`spaceBetween`, and numeric `fontWeight` -> `fontStyle` before forwarding to FigCraft.
- **Multi-Framework Design-to-Code (`codegen_helper.py`)**:
  - Reverse-maps `tokens.json` colors, spacing, radius, and typography scales to Tailwind classes.
  - Extracts typed component props (`TEXT`, `BOOLEAN`, `VARIANT`, `SLOT`) and outputs **React + Tailwind**, **Vue 3**, **Flutter**, or **HTML/CSS**.
- **WCAG 2.2 AA Design System & 7 Templates (`tokens.json`, `tokens.py`)**:
  - 4 curated themes (`editorial-paper`, `obsidian-studio`, `slate-instrument`, `botanical-ledger`) with all 32 color pairs mathematically audited at >= 4.5:1 contrast.
  - 7 reusable single-undo canvas templates (`palette_swatch`, `buttons`, `badges`, `segmented_control`, `data_table`, `state_cards`, `theme_board`).
- **Security Hardening (`security.py`)**:
  - Enforces JSON-RPC payload cap (2 MiB), max nesting depth (48), and max batch commands (500).
  - Blocks Windows UNC paths (`\\host\share`), null bytes, `..` traversal, and supports optional directory allowlisting via `FIGCRAFT_ALLOWED_ROOTS`.
  - Validates hex colors and escapes Vue mustaches/HTML entities during code generation.
- **Fully Portable**: Zero hardcoded user paths; runs across Windows, macOS, and Linux with Python 3.10+.

---

## Repository Structure

```
figcraft-mcp/
|-- bridge.py                # Smart MCP bridge (lazy launch, JSON-RPC multiplexing, security boundary)
|-- mcp_primitives.py        # Custom MCP Resources, Prompts, Workflow Tools & input guardrails
|-- security.py              # STRIDE boundary validation, path safety, hex sanitizer & log sanitizer
|-- codegen_helper.py        # Semantic AST cleaner, props extractor & 4-framework code generator
|-- tokens.py                # Design tokens API, WCAG AA contrast auditor, CSS/Tailwind exporter & 7 templates
|-- tokens.json              # Design tokens, 4 curated themes & dark/light semantic status tokens
|-- check.py                 # Standalone system and environment self-diagnosis tool
|-- check.bat                # 1-click health check runner for Windows
|-- check.sh                 # 1-click health check runner for macOS and Linux
|-- install.py               # Cross-platform installation and configuration script
|-- install.bat              # 1-click Windows installer
|-- install.sh               # 1-click macOS and Linux installer
|-- uninstall.bat            # 1-click uninstaller script
|-- tests/                   # Headless unittest suite (no GUI required)
|   |-- test_security_and_bridge.py  # Security boundary, codegen XSS, loopback socket & bridge tests
|   `-- test_core_unit.py            # Unit tests for mcp_primitives, tokens & codegen_helper
|-- test_mcp_primitives.py   # End-to-end stdio JSON-RPC verification against bridge.py
|-- test_design_system.py    # WCAG contrast audit & 28 template x theme batch schema verification
|-- test_design_to_code.py   # Multi-framework codegen pipeline verification
|-- test_connection.py       # Live FigCraft canvas connection test
|-- skills/                  # Instruction skills for AI assistants
|   |-- figcraft-designer/       # Engine rules, WCAG contrast & anti-slop UI craft guidelines
|   `-- figcraft-design-to-code/ # Design-to-Code workflow & multi-framework mapping rules
|-- docs/                    # Architecture documentation and technical specifications
|-- INSTALLATION.md          # Comprehensive installation guide (English)
|-- INSTALLATION.id.md       # Comprehensive installation guide (Bahasa Indonesia)
|-- TOKENS.md                # Design tokens, themes & template reference (English)
|-- TOKENS.id.md             # Design tokens, themes & template reference (Bahasa Indonesia)
|-- PROMPTS.md               # Ready-to-use prompt formula cheat sheet (English)
|-- PROMPTS.id.md            # Ready-to-use prompt formula cheat sheet (Bahasa Indonesia)
|-- README.md                # Primary project overview (English)
`-- README.id.md             # Primary project overview (Bahasa Indonesia)
```

---

## Quick Installation

### Windows Users
Double-click **`install.bat`**, or execute in PowerShell:
```powershell
python install.py
```

### macOS and Linux Users
```bash
chmod +x install.sh
./install.sh
```

For manual setup, per-client configs, and troubleshooting, see **[INSTALLATION.md](./INSTALLATION.md)**.

---

## Configuration Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `FIGCRAFT_PORT` | `1984` | Loopback TCP control port (validated in range `1024..65535`). |
| `FIGCRAFT_PATH` | Auto-detected | Optional override path to the `figcraft` GUI binary. |
| `FIGCRAFT_CLI_PATH` | Auto-detected | Optional override path to the `figcraft-cli` binary. |
| `FIGCRAFT_ALLOWED_ROOTS` | Unset (all local paths) | Optional OS path-separated allowlist restricting `open_file`/`save_file`/`export` destinations. |
| `FIGCRAFT_DEBUG` | Unset | Set to `1` to enable sanitized debug logging to `figcraft_bridge.log`. |

---

## How to Use

For copy-pasteable prompt formulas across 6 UI categories, see **[PROMPTS.md](./PROMPTS.md)**. For design tokens, themes, and component templates, see **[TOKENS.md](./TOKENS.md)**.

### 1. Render Curated Templates or Custom UI (Text-to-UI)
- "Render the `state_cards` template using theme `editorial-paper` on the FigCraft canvas."
- "Use prompt `figcraft_dashboard_card` to design a dark revenue card with MRR `$148,520` and trend `+18.4%`."
- "Build a desktop top navbar in FigCraft with transparent flex wrappers (`fill: none`)."

### 2. Convert Canvas Designs to Production Code (Design-to-Code)
- "Call `figcraft_generate_code` on node 125 with framework `react-tailwind` and typed props."
- "Convert node 125 to `vue`, `flutter`, or `html-css`."
- CLI alternative:
  ```bash
  python codegen_helper.py --node 125 --framework react-tailwind --out Card.tsx
  ```

---

## Testing and Verification

```bash
# 1. Fast headless unit, security & mock-socket suite (no FigCraft GUI needed)
python -m unittest discover -s tests -v

# 2. Audit all 32 theme and semantic color pairs for WCAG 2.2 AA (>= 4.5:1)
python tokens.py --audit-contrast
python test_design_system.py

# 3. Verify multi-framework Design-to-Code pipeline
python test_design_to_code.py

# 4. Verify end-to-end MCP stdio middleware (23 tools, 6 resources, 3 templates, 10 prompts)
python test_mcp_primitives.py

# 5. Run full environment self-diagnosis
python check.py
```

---

## Uninstallation

- Windows: Double-click **`uninstall.bat`**.
- Terminal: Run `python install.py --uninstall`.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
