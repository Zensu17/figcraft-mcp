# Prompt Cheat Sheet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide comprehensive, copy-pasteable prompt formula cheat sheets in dedicated English (`PROMPTS.md`) and Indonesian (`PROMPTS.id.md`) files with complete parity and zero emojis.

**Architecture:** Create standalone reference guides documenting prompt anatomy and 6 curated UI categories (Navigation, Forms, Cards/Widgets, Dashboards, Modals, and Design-to-Code), cross-linked to README files.

**Tech Stack:** Markdown (GitHub Flavored Markdown), Python (regex verification).

**Spec:** `docs/superpowers/specs/2026-11-17-prompt-cheat-sheet-design.md`

## Global Constraints

- Absolute prohibition of emojis and emoticon glyphs across all documentation.
- All prompt examples must use valid design tokens, hex colors, and layout structures compatible with FigCraft.
- 100% content and structural parity between `PROMPTS.md` and `PROMPTS.id.md`.
- No hardcoded personal user paths.

## Review Focus

- Undetected emoji or Unicode decorative symbols remaining in Markdown files.
- Broken links between README files and prompt cheat sheet files.
- Unclear prompt instructions that lack container dimensions or styling cues.
- Discrepancies between the English and Indonesian prompt templates.

---

### Task 1: Create Indonesian Prompt Cheat Sheet (`PROMPTS.id.md`)

**Files:**
- Create: `D:\Code\figcraft-mcp\PROMPTS.id.md`

**Interfaces:**
- Produces: Indonesian prompt cheat sheet reference for users.

- [ ] **Step 1: Write `PROMPTS.id.md`**
  Include:
  - Header and switcher link: `[Read in English](PROMPTS.md)`.
  - Anatomi Formula Prompt (Peran + Wadah/Layout + Gaya Visual/Token + Aksi).
  - Kategori 1: Navigasi dan Menu (Navbar desktop modern, mobile bottom bar, breadcrumb).
  - Kategori 2: Formulir dan Autentikasi (Card login mode gelap, formulir pendaftaran, reset password).
  - Kategori 3: Kartu Konten dan Media (Kartu e-commerce sneaker, pemutar musik, kartu cuaca, kartu paket langganan).
  - Kategori 4: Dashboard dan Statistik (Kartu pendapatan bulanan, ringkasan metrik 3-kolom).
  - Kategori 5: Modal dan Dialog (Modal konfirmasi hapus, popup info, drawer menu).
  - Kategori 6: Konversi Desain ke Kode (React Tailwind CSS, Flutter, tailwind.config.js).
  - Tips Praktis Desain (Penamaan frame, penggunaan tata letak flex/stack, kontras warna).
  - Zero emojis throughout.

- [ ] **Step 2: Verify file existence and absence of emojis**
  Ensure file exists and regex check finds no emoji glyphs.

- [ ] **Step 3: Commit**
  Run: `git add PROMPTS.id.md && git commit -m "docs: add Indonesian prompt cheat sheet PROMPTS.id.md"`

---

### Task 2: Create English Prompt Cheat Sheet (`PROMPTS.md`)

**Files:**
- Create: `D:\Code\figcraft-mcp\PROMPTS.md`

**Interfaces:**
- Produces: English prompt cheat sheet reference for users.

- [ ] **Step 1: Write `PROMPTS.md`**
  Include:
  - Header and switcher link: `[Baca dalam Bahasa Indonesia](PROMPTS.id.md)`.
  - Anatomy of a High-Impact Prompt (Role + Container Layout + Visual Tokens + Action).
  - Category 1: Navigation and Menus.
  - Category 2: Forms and Authentication.
  - Category 3: Content Cards and Media Widgets.
  - Category 4: Dashboards and Metric Displays.
  - Category 5: Modals and Dialog Overlays.
  - Category 6: Design-to-Code Conversion Prompts.
  - Practical Tips for FigCraft Canvas Prompts.
  - Zero emojis throughout.

- [ ] **Step 2: Verify file completeness and absence of emojis**
  Ensure 100% structural parity with `PROMPTS.id.md`.

- [ ] **Step 3: Commit**
  Run: `git add PROMPTS.md && git commit -m "docs: add English prompt cheat sheet PROMPTS.md"`

---

### Task 3: Link Prompt Cheat Sheets in README Files

**Files:**
- Modify: `D:\Code\figcraft-mcp\README.md`
- Modify: `D:\Code\figcraft-mcp\README.id.md`

**Interfaces:**
- Consumes: `PROMPTS.md` and `PROMPTS.id.md`.
- Produces: Updated repository overview files with clear links to the prompt guide.

- [ ] **Step 1: Update `README.md`**
  Add a link to `PROMPTS.md` under the "How to Use" section.

- [ ] **Step 2: Update `README.id.md`**
  Add a link to `PROMPTS.id.md` under the "Cara Penggunaan" section.

- [ ] **Step 3: Commit**
  Run: `git add README.md README.id.md && git commit -m "docs: link prompt cheat sheets in README files"`

---

### Task 4: Automated Verification and Review

**Files:**
- Verification via regex scanner script.

- [ ] **Step 1: Run regex emoji scan on all `.md` files**
  Confirm 0 emojis across all markdown documentation files.

- [ ] **Step 2: Verify cross-links**
  Confirm links between README and PROMPTS files resolve correctly.
