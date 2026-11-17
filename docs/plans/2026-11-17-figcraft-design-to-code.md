# FigCraft Two-Way Design-to-Code Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menambahkan kapabilitas dua arah (*Two-Way Design-to-Code*) ke FigCraft MCP Bridge: AI dapat membaca struktur visual frame di FigCraft kanvas dan mengonversinya secara presisi menjadi kode komponen frontend siap pakai (React + Tailwind, Flutter, HTML/CSS).

**Architecture:** Menggunakan Pendekatan 1 (Hybrid Mode). Script helper Python (`codegen_helper.py`) mengekstrak dan memangkas pohon node FigCraft menjadi struktur token UI semantik yang ringkas, lalu skill Markdown (`skills/figcraft-design-to-code/SKILL.md`) memandu AI memetakan token tersebut ke komponen framework yang diminta pengguna dengan fidelity tinggi.

**Tech Stack:** Python 3.8+ (standard library: json, subprocess, sys, pathlib), React / Tailwind CSS / Flutter, Model Context Protocol (MCP).

**Spec:** [docs/design-to-code-design.md](file:///D:/Code/figcraft-mcp/docs/design-to-code-design.md)

## Global Constraints

- Menggunakan standard library Python saja (tanpa dependensi third-party tambahan).
- Portabel lintas platform (Windows, macOS, Linux).
- Bekerja mulus dengan arsitektur Lazy Launch MCP bridge yang sudah ada.

## Review Focus

1. **Node Tree Filtering**: Node teks dan node frame bersarang harus mempertahankan hierarki tanpa kehilangan properti padding dan gap.
2. **Auto-layout Translation**: Frame vertikal/horizontal harus dipetakan ke flexbox yang valid (`flex-col` / `flex-row`).
3. **Color & Radius Formatting**: Nilai hex warna `#RRGGBB` dan corner radius piksel harus dinormalisasi menjadi utility class yang bersih.
4. **Token Optimization**: Output JSON hasil pembersihan harus memangkas minimal 70% ukuran raw JSON agar hemat context window AI.
5. **Multi-framework Extensibility**: Aturan pemetaan harus mencakup React + Tailwind dan Flutter.

---

### Task 1: AST Cleaner & UI Token Extractor (`codegen_helper.py`)

**Files:**
- Create: `D:\Code\figcraft-mcp\codegen_helper.py`
- Test: Self-contained test block di dalam `codegen_helper.py`

**Steps:**
- [ ] 1. Buat fungsi `clean_node(raw_node)` yang mengekstrak atribut semantik: `type`, `name`, `layout`, `gap`, `padding`, `align`, `justify`, `bg`, `radius`, `text`, dan `children`.
- [ ] 2. Buat fungsi `simplify_tree(doc_json)` yang membuang metadata koordinat absolut yang berisik.
- [ ] 3. Tambahkan fungsi CLI: dapat membaca dari stdin, membaca file JSON, atau langsung query ke node FigCraft jika parameter `--node <id>` diberikan.
- [ ] 4. Jalankan verifikasi mandiri menggunakan dummy JSON node FigCraft.
- [ ] 5. Commit perubahan ke git.

---

### Task 2: AI Guidance Skill (`skills/figcraft-design-to-code/SKILL.md`)

**Files:**
- Create: `D:\Code\figcraft-mcp\skills\figcraft-design-to-code\SKILL.md`

**Steps:**
- [ ] 1. Tulis petunjuk aktivasi skill (triggers: "convert to code", "figcraft to react", "export flutter", "generate component from figcraft").
- [ ] 2. Tulis tabel pemetaan token FigCraft ke Tailwind CSS (layout, padding, gap, background, text styles, rounded).
- [ ] 3. Tulis tabel pemetaan token FigCraft ke Flutter Widgets (`Column`, `Row`, `Container`, `BoxDecoration`, `TextStyle`).
- [ ] 4. Tambahkan panduan visual feedback: AI menggunakan tool `screenshot` FigCraft untuk memverifikasi akurasi komponen yang digenerate.
- [ ] 5. Commit perubahan ke git.

---

### Task 3: Integration & Proof-of-Concept Test (`test_design_to_code.py`)

**Files:**
- Create: `D:\Code\figcraft-mcp\test_design_to_code.py`
- Create: `D:\Code\figcraft-mcp\examples\WeatherWidget.tsx` (hasil output uji coba)

**Steps:**
- [ ] 1. Buat script `test_design_to_code.py` yang terhubung via MCP bridge.
- [ ] 2. Query node ID 57 (Simple Weather Widget) dari kanvas FigCraft.
- [ ] 3. Bersihkan data node menggunakan `codegen_helper.py`.
- [ ] 4. Konversi token menjadi komponen React Tailwind murni dan simpan ke `examples/WeatherWidget.tsx`.
- [ ] 5. Lakukan assertion untuk memastikan komponen berisi syntax valid (`export default function`, tailwind class `flex`, `p-`, `rounded-`).
- [ ] 6. Jalankan test dan pastikan lolos 100%.
- [ ] 7. Commit perubahan ke git.

---

### Task 4: Dokumentasi & Sinkronisasi

**Files:**
- Modify: `D:\Code\figcraft-mcp\README.md`
- Modify: `D:\Code\figcraft-mcp\INSTALLATION.md`
- Copy: Sync skill ke `.gemini/config/plugins/` atau global skills jika diperlukan.

**Steps:**
- [ ] 1. Perbarui `README.md` dengan menambahkan section "Two-Way Design-to-Code Workflow" dan contoh prompt.
- [ ] 2. Perbarui `INSTALLATION.md`.
- [ ] 3. Lakukan commit git final ke branch `main`.
