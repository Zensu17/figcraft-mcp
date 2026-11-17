# Documentation Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor project documentation into dedicated English and Indonesian files (Approach B) with complete bilateral parity, beginner-friendly phrasing, and zero emojis.

**Architecture:** Separate `README.md` / `README.id.md` and `INSTALLATION.md` / `INSTALLATION.id.md` with explicit top-level language navigation links, remove all decorative emoji glyphs, and provide exhaustive, step-by-step guidance across all 8 core setup sections.

**Tech Stack:** Markdown (GitHub Flavored Markdown), Python (regex verification script).

**Spec:** `docs/superpowers/specs/2026-11-17-documentation-refactor-design.md`

## Global Constraints

- Absolute prohibition of emojis and emoticon glyphs across all documentation.
- No hardcoded personal user paths (use `<REPO_PATH>` or generic relative paths).
- Complete 100% content parity between English and Indonesian versions of `INSTALLATION.md` and `INSTALLATION.id.md`.

## Review Focus

- Undetected emoji or Unicode decorative symbols remaining in Markdown files.
- Broken relative links between English and Indonesian files.
- Incomplete setup instructions for any of the 4 supported AI clients (AntiGravity, OpenCode, Cursor, Claude Desktop).
- Windows desktop shortcut instructions missing `--control 1984` target syntax.
- Discrepancies in the 19 FigCraft tools reference table between languages.

---

### Task 1: Create Indonesian README (`README.id.md`)

**Files:**
- Create: `D:\Code\figcraft-mcp\README.id.md`

**Interfaces:**
- Produces: Indonesian language overview for GitHub repository visitors.

- [ ] **Step 1: Write `README.id.md`**
  Include:
  - Top language switcher link: `[Read in English](README.md)`.
  - Plain-text overview of FigCraft Universal MCP Bridge.
  - Two-way workflow explanation (Text-to-UI and Design-to-Code).
  - Key features explained in plain language (Lazy on-demand launch, AST reduction, full portability, 1-click installer, clean uninstaller) with zero emojis.
  - Repository structure diagram.
  - Quick installation guide (Windows `install.bat`, macOS/Linux `install.sh`).
  - Clear first-time usage guide with copy-pasteable prompt examples.
  - Verification and testing commands (`test_connection.py`, `test_design_to_code.py`).
  - Uninstallation instructions.

- [ ] **Step 2: Verify file existence and readability**
  Check that `README.id.md` exists and contains no emojis.

- [ ] **Step 3: Commit**
  Run: `git add README.id.md && git commit -m "docs: add comprehensive Indonesian README.id.md"`

---

### Task 2: Refactor English README (`README.md`)

**Files:**
- Modify: `D:\Code\figcraft-mcp\README.md`

**Interfaces:**
- Consumes: `README.id.md` link.
- Produces: Pure English repository landing page.

- [ ] **Step 1: Update `README.md`**
  - Add top language switcher link: `[Baca dalam Bahasa Indonesia](README.id.md)`.
  - Remove all emoji characters (e.g. lightning, arrows, computer, rocket, shield).
  - Remove the inline Indonesian section from the bottom of the file (now housed in `README.id.md`).
  - Refine structure for clarity and beginner-friendliness.

- [ ] **Step 2: Verify file content and links**
  Verify link to `README.id.md` and `INSTALLATION.md` resolves properly.

- [ ] **Step 3: Commit**
  Run: `git add README.md && git commit -m "docs: refactor README.md to English-only without emojis"`

---

### Task 3: Create Indonesian Installation Guide (`INSTALLATION.id.md`)

**Files:**
- Create: `D:\Code\figcraft-mcp\INSTALLATION.id.md`

**Interfaces:**
- Produces: Exhaustive 8-section Indonesian installation guide.

- [ ] **Step 1: Write `INSTALLATION.id.md`**
  Provide complete parity with English guide across all 8 sections:
  1. Prasyarat Sistem (Python 3.8+ dengan opsi PATH, dan aplikasi FigCraft).
  2. Mengunduh dan Mengkloning Repositori (Git clone & Download ZIP).
  3. Metode 1: Pemasangan Otomatis 1-Klik (`install.bat` dan `install.sh`).
  4. Metode 2: Konfigurasi Manual per AI Client (Google AntiGravity, OpenCode CLI, Cursor IDE, Claude Desktop).
  5. Pengaturan Shortcut Desktop Windows (`--control 1984`).
  6. Pengujian dan Verifikasi (`test_connection.py` dan `test_design_to_code.py`).
  7. Pemecahan Masalah dan Tanya Jawab (Troubleshooting & FAQ).
  8. Tabel Referensi 19 Alat MCP FigCraft.
  Zero emojis used throughout.

- [ ] **Step 2: Verify file completeness**
  Check that all 8 sections are present with accurate code snippets and paths.

- [ ] **Step 3: Commit**
  Run: `git add INSTALLATION.id.md && git commit -m "docs: add comprehensive Indonesian INSTALLATION.id.md with 100% parity"`

---

### Task 4: Refactor English Installation Guide (`INSTALLATION.md`)

**Files:**
- Modify: `D:\Code\figcraft-mcp\INSTALLATION.md`

**Interfaces:**
- Consumes: `INSTALLATION.id.md` link.
- Produces: Pure English comprehensive installation guide.

- [ ] **Step 1: Update `INSTALLATION.md`**
  - Add top language switcher link: `[Baca dalam Bahasa Indonesia](INSTALLATION.id.md)`.
  - Remove the abbreviated Indonesian section from the bottom of the file.
  - Review all 8 sections to ensure complete clarity and zero emojis.

- [ ] **Step 2: Verify file content**
  Confirm file contains all 8 sections and links correctly to `INSTALLATION.id.md`.

- [ ] **Step 3: Commit**
  Run: `git add INSTALLATION.md && git commit -m "docs: refactor INSTALLATION.md to English-only without emojis"`

---

### Task 5: Automated Verification and Git Sync

**Files:**
- Create temporary check: regex scan script or command.

- [ ] **Step 1: Scan for remaining emojis**
  Run regex pattern check on all `.md` files in the repository:
  `README.md`, `README.id.md`, `INSTALLATION.md`, `INSTALLATION.id.md`.
  Ensure zero matches for emoji Unicode ranges.

- [ ] **Step 2: Verify all internal markdown links**
  Ensure cross-links between README and INSTALLATION files resolve accurately.

- [ ] **Step 3: Push to remote GitHub branch `main`**
  Run: `git push origin main`
