# Design Document: Documentation Refactoring and Bilateral Parity

Date: 2026-11-17
Topic: Documentation Refactoring (Suggestion 1)
Status: Proposed

## 1. Intent and Why
The current documentation contains emoji symbols, has an incomplete Indonesian section in INSTALLATION.md (only 25 lines compared to 239 lines in English), and presents dense configuration details without a beginner-friendly onboarding flow. The goal is to provide clear, thorough, easy-to-understand, and completely emoji-free documentation in both English and Bahasa Indonesia.

## 2. Goals, Non-Goals, and Anti-Goals
- Goals:
  - Separate language documentation into dedicated files: README.md (EN), README.id.md (ID), INSTALLATION.md (EN), and INSTALLATION.id.md (ID).
  - Remove all emoji and emoticon symbols across all documentation files.
  - Complete the Indonesian documentation so it has 100% parity with the English version, including manual configuration, shortcut setup, testing, troubleshooting, and tool references.
  - Structure each guide into clear, chronological stages (Requirements -> 1-Click Installation -> Verification -> First UI Prompt -> Troubleshooting).
- Non-Goals:
  - Modifying the underlying Python bridge code (`bridge.py`, `install.py`, `codegen_helper.py`).
  - Changing the MCP protocol specification or tool definitions.
- Anti-Goals:
  - Using emojis, icons, or decorative ASCII glyphs.
  - Omitting configuration details or error handling scenarios in the translated version.

## 3. Constraints
- Strict prohibition of emojis/emoticons across all markdown files.
- Zero hardcoded personal user paths (all path references must use generic placeholders or relative paths).
- Clear, simple phrasing suitable for developers of all skill levels.

## 4. Approaches Considered
- Approach A: Unified Single-File Dual-Language (Current). Both languages in one large file separated by anchor links. Trade-off: files are overly long and Indonesian section felt like an afterthought.
- Approach B: Dedicated Language Files (Chosen). README.md and INSTALLATION.md in English; README.id.md and INSTALLATION.id.md in Bahasa Indonesia, with prominent header links to switch languages. Trade-off: requires an extra file click, but provides a focused, clean reading experience matching major open-source projects.

## 5. Specification of Documentation Files

### File: README.md (English) & README.id.md (Bahasa Indonesia)
- Header with direct language switcher link.
- Plain-text overview of the FigCraft Universal MCP Bridge.
- Core capabilities:
  - Text-to-UI on FigCraft live canvas.
  - Design-to-Code AST extraction to React/Tailwind and Flutter.
  - On-Demand Lazy Launch (GUI opens only when an AI tool call is made).
  - Cross-platform portability without hardcoded paths.
- Repository structure breakdown.
- Quick 1-click installation guide (Windows, macOS, Linux).
- Step-by-step first usage guide (Text-to-UI prompt examples and Design-to-Code prompt examples).
- Verification commands.
- Uninstallation commands.

### File: INSTALLATION.md (English) & INSTALLATION.id.md (Bahasa Indonesia)
Full bilateral parity across the following 8 sections:
1. Prerequisites (Python 3.8+ with PATH requirement, FigCraft installation paths).
2. Download and Clone methods (Git clone or ZIP).
3. Method 1: Automatic 1-Click Installer (`install.bat` / `install.sh` / `install.py`).
4. Method 2: Manual Setup per AI Client:
   - Google AntiGravity CLI/IDE (`~/.gemini/config/mcp_config.json`)
   - OpenCode CLI (`opencode mcp add` and `~/.config/opencode/opencode.json`)
   - Cursor IDE (`~/.cursor/mcp.json`)
   - Claude Desktop (`claude_desktop_config.json`)
5. Windows Desktop Shortcut configuration (`--control 1984` flag).
6. Testing and Verification (`test_connection.py` and `test_design_to_code.py`).
7. Troubleshooting and FAQ (Python PATH issues, FigCraft path resolution, Port 1984 conflicts, Firewall rules).
8. MCP Tools Reference Table (all 19 FigCraft tools explained clearly).

## 6. Implementation Sequence
1. Create `README.id.md` with complete, easy-to-read Indonesian documentation without emojis.
2. Update `README.md` in English, stripping all emojis and referencing `README.id.md`.
3. Create `INSTALLATION.id.md` with complete, 100% mirrored Indonesian instructions without emojis.
4. Update `INSTALLATION.md` in English, stripping all emojis and referencing `INSTALLATION.id.md`.
5. Verify that no emojis remain in the documentation.
6. Commit changes to git branch `main`.
