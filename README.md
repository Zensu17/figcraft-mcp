# FigCraft Universal MCP Bridge

> Connect any AI coding assistant to FigCraft with complete two-way design and code generation workflows.

**English** | [Baca dalam Bahasa Indonesia](README.id.md)

---

## Overview

FigCraft Universal MCP Bridge connects modern AI coding tools (such as Google AntiGravity, OpenCode CLI, Cursor, and Claude Desktop) directly to FigCraft.

FigCraft is an open-source visual design application written from scratch in pure Rust, offering ultra-fast, lightweight, and independent local execution on your machine.

Through the Model Context Protocol (MCP), this bridge unlocks a complete two-way workflow:
1. **Text-to-UI**: AI draws components, forms, buttons, cards, and complex layouts directly onto the live FigCraft desktop canvas.
2. **Design-to-Code**: AI inspects visual designs on your FigCraft canvas and translates them into clean, production-ready frontend code (React with Tailwind CSS, or Flutter).

---

## Key Features

- **On-Demand Lazy Launch**: When you boot your AI assistant or terminal, the bridge starts silently in headless mode (taking under 50 milliseconds without opening any windows). The FigCraft desktop application opens automatically only when you explicitly instruct the AI to design or modify something on the canvas.
- **Token-Efficient Design-to-Code**: Includes an intelligent AST cleaner (`codegen_helper.py`) that filters out noisy raw coordinates and extracts semantic layout tokens (such as flex, padding, gap, colors, and typography), reducing AI token consumption by 50 to 70 percent.
- **Fully Portable and Free of Hardcoded Paths**: Contains zero personal username paths or machine-specific directories. Runs reliably across Windows, macOS, and Linux.
- **1-Click Automatic Installer**: Automatically detects your Python environment, locates FigCraft, and registers the server configuration into Google AntiGravity, OpenCode, Cursor, and Claude Desktop simultaneously.
- **Clean Uninstaller**: Provides a dedicated uninstaller that cleanly removes bridge registrations from all AI clients without leaving residual configuration files behind.

---

## Repository Structure

```
figcraft-mcp/
|-- bridge.py                # Smart MCP bridge (handles lazy launch and dynamic path discovery)
|-- codegen_helper.py        # AST cleaner and tokenizer for Design-to-Code translation
|-- install.py               # Cross-platform installation and configuration script
|-- install.bat              # 1-click Windows installer
|-- install.sh               # 1-click macOS and Linux installer
|-- uninstall.bat            # 1-click uninstaller script
|-- test_connection.py       # Handshake verification and canvas element creation test
|-- test_design_to_code.py   # Automated end-to-end verification of Design-to-Code pipeline
|-- skills/                  # Instruction skills for AI assistants
|   |-- figcraft-designer/       # Rules for building clean, well-aligned UI on FigCraft canvas
|   |-- figcraft-design-to-code/ # Rules for inspecting canvas designs and generating React/Flutter code
|-- docs/                    # Architecture documentation and technical specifications
|-- INSTALLATION.md          # Comprehensive installation guide (English)
|-- INSTALLATION.id.md       # Comprehensive installation guide (Bahasa Indonesia)
|-- PROMPTS.md               # Ready-to-use prompt formula cheat sheet (English)
|-- PROMPTS.id.md            # Ready-to-use prompt formula cheat sheet (Bahasa Indonesia)
|-- README.md                # Primary project overview (English)
`-- README.id.md             # Primary project overview (Bahasa Indonesia)
```

---

## Quick Installation

### Windows Users
Double-click **`install.bat`**, or execute in your terminal:
```powershell
python install.py
```

### macOS and Linux Users
Make the installer script executable and run it:
```bash
chmod +x install.sh
./install.sh
```

For manual setup instructions, step-by-step configuration for individual AI clients, and troubleshooting tips, see the **[INSTALLATION.md](./INSTALLATION.md)** guide.

---

## How to Use

For ready-to-use copy-pasteable prompt formulas across 6 core UI categories, see **[PROMPTS.md](./PROMPTS.md)**.

Once installed, open your preferred AI assistant (AntiGravity, Cursor, OpenCode, or Claude Desktop).

### 1. Designing on FigCraft Canvas (Text-to-UI)
Give plain-language design prompts to your AI:
- "Create a modern dark-mode login form in FigCraft with email input, password input, and an indigo submit button."
- "Design a responsive mobile music player card in FigCraft with album artwork, a track progress bar, and playback controls."
- "Build a monthly revenue analytics dashboard card in FigCraft featuring positive growth indicators."

Result: FigCraft launches automatically and renders your requested UI components directly onto the active canvas.

### 2. Converting Canvas Designs to Code (Design-to-Code)
Select any frame or component in FigCraft, then prompt your AI:
- "Read the active weather widget in FigCraft and convert it into a clean, responsive React Tailwind CSS component."
- "Convert the selected user profile card in FigCraft into a Flutter widget."
- "Extract the color palette and typography rules from the current FigCraft design into a tailwind.config.js file."

---

## Testing and Verification

Verify that your bridge and code generation pipeline are working properly by running these two automated tests:

```bash
# 1. Test MCP connection and create a test badge on the FigCraft canvas
python test_connection.py

# 2. Test the Design-to-Code extraction and code generation pipeline
python test_design_to_code.py
```

Check your FigCraft window: the test element will appear directly on your canvas.

---

## Uninstallation

To remove the FigCraft bridge configuration from all AI tools:
- On Windows: Double-click **`uninstall.bat`**.
- From terminal: Run `python install.py --uninstall`.
