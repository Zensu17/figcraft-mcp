# Design Document: Environment Self-Diagnosis Tool (Suggestion 3)

Date: 2026-11-17
Topic: Environment Self-Diagnosis Script (`check.py` and `check.bat`)
Status: Proposed

## 1. Intent and Why
When users encounter issues (for example, FigCraft not launching, canvas commands timing out, or an AI tool not discovering FigCraft tools), they often struggle to pinpoint the cause. An automated health-check script tests all prerequisites, binary paths, port bindings, and configuration files in seconds, providing plain-language recommendations if any item is misconfigured.

## 2. Goals, Non-Goals, and Anti-Goals
- Goals:
  - Create a standalone Python diagnostic script `check.py` with zero third-party dependencies (standard library only: `sys`, `os`, `pathlib`, `socket`, `json`, `subprocess`).
  - Create a 1-click Windows runner `check.bat` (and `check.sh` for Unix).
  - Verify 6 critical health checks:
    1. Python runtime version (>= 3.8) and standard library integrity.
    2. FigCraft executable discovery (`figcraft.exe` and `figcraft-cli.exe`).
    3. Network status of loopback port 1984 (is it listening, free, or blocked).
    4. FigCraft Desktop shortcut target configuration (verifying presence of `--control 1984`).
    5. AI assistant configuration discovery (verifying MCP registration in AntiGravity, OpenCode, Cursor, and Claude Desktop).
    6. End-to-end headless MCP handshake test (spawning `figcraft-cli mcp` and testing `initialize`).
  - Output results in a clean, professional, plain-text report using `[OK]`, `[FAIL]`, and `[WARN]` text labels (strictly zero emojis).
  - Provide actionable, human-readable remedy advice for any failed check.
  - Document `check.py` and `check.bat` in `README.md`, `README.id.md`, `INSTALLATION.md`, and `INSTALLATION.id.md`.
- Non-Goals:
  - Automatically altering user configuration without permission (this is a diagnostic, read-only inspection tool).
- Anti-Goals:
  - Using emojis or graphical Unicode symbols in CLI output.
  - Hardcoding personal user paths.

## 3. Constraints
- Pure Python 3.8+ standard library only.
- Strict prohibition of emoji and emoticon glyphs in CLI console output and documentation.
- Non-destructive and read-only: does not modify or corrupt existing configuration files.

## 4. Approaches Considered
- Approach A: Python CLI script only (`check.py`).
  - Trade-off: Requires users to open terminal manually.
- Approach B: Python CLI script (`check.py`) + 1-Click Batch Runner (`check.bat` and `check.sh`) (Chosen).
  - Trade-off: Two small extra wrapper files, but matches existing `install.bat` / `uninstall.bat` pattern and allows double-click execution for beginners.

## 5. Specification of Diagnosis Checks

### Check 1: Python Environment
- Check `sys.version_info >= (3, 8)`.
- Report Python path and version string.

### Check 2: FigCraft Binary Discovery
- Probe standard locations (`C:\Program Files\ArtCraft\FigCraft\` or `PATH` or environment variables `FIGCRAFT_PATH` / `FIGCRAFT_CLI_PATH`).
- Verify executable existence and executable permissions.

### Check 3: Port 1984 Availability & Status
- Probe `127.0.0.1:1984` via non-blocking TCP socket connection.
- Distinguish between:
  - State A: Port is actively listening (FigCraft GUI with control channel is currently open).
  - State B: Port is currently free (ready for on-demand lazy launch).
  - State C: Port is occupied by a foreign process that refuses FigCraft control handshakes.

### Check 4: FigCraft Desktop & Start Menu Shortcut Flags (Windows)
- Inspect Windows Start Menu and Desktop `.lnk` shortcut targets for `--control 1984` parameter.

### Check 5: AI Assistant MCP Client Configurations
- Inspect config files for:
  - Google AntiGravity (`~/.gemini/config/mcp_config.json`)
  - OpenCode CLI (`~/.config/opencode/opencode.json`)
  - Cursor IDE (`~/.cursor/mcp.json`)
  - Claude Desktop (`%APPDATA%\Claude\claude_desktop_config.json`)
- Report whether FigCraft server entry exists, points to `bridge.py`, and is valid JSON.

### Check 6: Headless CLI MCP Protocol Handshake
- Spawn `figcraft-cli mcp` in headless mode.
- Send JSON-RPC `initialize` request.
- Assert valid JSON-RPC 2.0 response with server capabilities and protocol version `2024-11-05`.
- Terminate process cleanly.

## 6. Implementation Sequence
1. Implement `check.py` with 6 modular checks, clean ANSI text formatting, and actionable remediation steps.
2. Implement `check.bat` (Windows 1-click runner with pause on exit) and `check.sh`.
3. Test `check.py` locally on current machine and verify all checks pass.
4. Update `README.md`, `README.id.md`, `INSTALLATION.md`, and `INSTALLATION.id.md` to document the diagnostic tool.
5. Verify zero emojis across all code output and markdown files.
6. Commit changes to git branch `main`.
