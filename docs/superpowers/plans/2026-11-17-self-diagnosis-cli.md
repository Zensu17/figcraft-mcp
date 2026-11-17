# Self-Diagnosis Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone environment diagnostic tool (`check.py`, `check.bat`, `check.sh`) that verifies all FigCraft MCP prerequisites, paths, port states, and AI configurations with zero emojis.

**Architecture:** Pure Python standard library script performing 6 non-destructive system inspections with plain-text status labels (`[OK]`, `[FAIL]`, `[WARN]`), accompanied by 1-click batch/shell wrappers and bilingual documentation.

**Tech Stack:** Python 3.8+ (standard library: `sys`, `os`, `pathlib`, `socket`, `json`, `subprocess`), Windows Batch (`.bat`), POSIX Shell (`.sh`).

**Spec:** `docs/superpowers/specs/2026-11-17-self-diagnosis-cli-design.md`

## Global Constraints

- Absolute prohibition of emojis and emoticon glyphs across all console output, scripts, and documentation.
- Zero third-party Python dependencies (must run on vanilla Python 3.8+).
- Non-destructive execution: read-only diagnostics without altering configuration files.
- No hardcoded personal user paths.

## Review Focus

- Emojis appearing in stdout/stderr during CLI execution.
- False positive failures when port 1984 is free (normal state prior to on-demand launch).
- Handling missing AI configuration files gracefully as `[WARN]` rather than fatal failures.
- Cross-platform file path resolution across Windows and Unix.
- Clean exit code handling: 0 for all passed, 1 for fatal requirement failure.

---

### Task 1: Implement Self-Diagnosis Script (`check.py`)

**Files:**
- Create: `D:\Code\figcraft-mcp\check.py`

**Interfaces:**
- Produces: CLI diagnostic tool executed via `python check.py`.
- Return codes: 0 if all required checks pass, 1 if any critical check fails.

- [ ] **Step 1: Write `check.py`**
  Implement 6 checks:
  1. `check_python()`: Python version >= 3.8.
  2. `check_figcraft_binaries()`: Locates `figcraft.exe` and `figcraft-cli.exe`.
  3. `check_port_1984()`: Probes TCP socket on 127.0.0.1:1984 (distinguishes listening vs free).
  4. `check_windows_shortcuts()`: Checks desktop and start menu shortcuts for `--control 1984` (on Windows).
  5. `check_ai_configs()`: Verifies FigCraft bridge registration in AntiGravity, OpenCode, Cursor, and Claude Desktop.
  6. `check_cli_handshake()`: Spawns `figcraft-cli mcp` and tests JSON-RPC `initialize`.
  Formatting: Plain text table with ANSI colors and labels `[OK]`, `[FAIL]`, `[WARN]`. Zero emojis.

- [ ] **Step 2: Verify `check.py` syntax and execution**
  Run: `python check.py`
  Expected: All checks run and report status cleanly without errors or emojis.

- [ ] **Step 3: Commit**
  Run: `git add check.py && git commit -m "feat: add self-diagnosis script check.py"`

---

### Task 2: Create 1-Click Launchers (`check.bat` and `check.sh`)

**Files:**
- Create: `D:\Code\figcraft-mcp\check.bat`
- Create: `D:\Code\figcraft-mcp\check.sh`

**Interfaces:**
- Produces: 1-click runners for Windows and macOS/Linux.

- [ ] **Step 1: Write `check.bat`**
  Windows batch script:
  - Echo clean header.
  - Execute `python check.py`.
  - Pause on exit so window stays open when double-clicked from File Explorer.

- [ ] **Step 2: Write `check.sh`**
  POSIX shell script:
  - Execute `python3 check.py`.

- [ ] **Step 3: Commit**
  Run: `git add check.bat check.sh && git commit -m "feat: add check.bat and check.sh launchers"`

---

### Task 3: Update Documentation Across All Languages

**Files:**
- Modify: `D:\Code\figcraft-mcp\README.md`
- Modify: `D:\Code\figcraft-mcp\README.id.md`
- Modify: `D:\Code\figcraft-mcp\INSTALLATION.md`
- Modify: `D:\Code\figcraft-mcp\INSTALLATION.id.md`

**Interfaces:**
- Consumes: `check.py` and `check.bat`.
- Produces: Updated documentation referencing the health-check tool in both English and Indonesian.

- [ ] **Step 1: Update README files**
  Add `check.bat` and `check.py` to directory tree and "Testing and Verification" section.

- [ ] **Step 2: Update INSTALLATION files**
  Add environment diagnosis instructions to Troubleshooting and Verification sections.

- [ ] **Step 3: Commit**
  Run: `git add README.md README.id.md INSTALLATION.md INSTALLATION.id.md && git commit -m "docs: document self-diagnosis check tool across all guides"`

---

### Task 4: Automated Verification and Review

**Files:**
- Verification via regex scan and execution test.

- [ ] **Step 1: Run regex emoji scan on all files**
  Confirm 0 emojis across `check.py`, `check.bat`, `check.sh`, and all `.md` files.

- [ ] **Step 2: Execute `python check.py` and verify exit code**
  Confirm exit code is 0 on valid environment.
