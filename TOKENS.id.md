# FigCraft Design Tokens, Tema & Template Kanvas

> Katalog token desain WCAG 2.2 AA, 4 tema terkurasi, exporter CSS/Tailwind, dan 7 template komponen kanvas FigCraft satu-undo.

[Read in English](TOKENS.md) | **Bahasa Indonesia**

---

## Daftar Isi
1. [Gambaran Umum](#1-gambaran-umum)
2. [Tema Terkurasi (Terverifikasi WCAG 2.2 AA)](#2-tema-terkurasi-terverifikasi-wcag-22-aa)
3. [Referensi Skala Token](#3-referensi-skala-token)
4. [Penggunaan CLI & MCP Tool](#4-penggunaan-cli--mcp-tool)
5. [Python API & Exporter](#5-python-api--exporter)

---

## 1. Gambaran Umum

`tokens.json` (v2.0.0) dan `tokens.py` menjadi fondasi visual `figcraft-mcp`. Setiap preset tema dan pasangan warna status telah diaudit secara matematis agar lolos kontras **WCAG 2.2 AA (>= 4.5:1)**, dan setiap builder template menghasilkan perintah `batch` FigCraft valid dengan hierarki parent `$ref` serta wrapper transparan `fill: "none"`.

---

## 2. Tema Terkurasi (Terverifikasi WCAG 2.2 AA)

Setiap tema dibatasi pada 2-3 permukaan netral dan 1 aksen fokus yang terukur:

| Nama Tema | Mode | Surface / Elevated | Aksen | Karakter |
| :--- | :--- | :--- | :--- | :--- |
| `editorial-paper` | light | `#FAFAF9` / `#FFFFFF` | `#B45309` | Editorial terang hangat berbasis stone & ochre |
| `obsidian-studio` | dark | `#09090B` / `#18181B` | `#0369A1` | Studio gelap grafit dengan aksen deep-sky |
| `slate-instrument` | dark | `#0F172A` / `#1E293B` | `#4F46E5` | Antarmuka teknis gelap slate & indigo |
| `botanical-ledger` | light | `#F8FAFC` / `#FFFFFF` | `#047857` | Tema terang operasional/finansial dengan emerald |

---

## 3. Referensi Skala Token

### A. Palet Warna (Shade 50 hingga 950)
8 palet: `slate`, `zinc`, `stone`, `indigo`, `sky`, `emerald`, `amber`, dan `rose`.

### B. Token Status Semantik (`dark` & `light`)
Pasangan foreground/background/border terverifikasi untuk status `success`, `warning`, `danger`, dan `info`.

### C. Skala Spacing (Grid 4px)
`0` (0px), `1` (4px), `2` (8px), `3` (12px), `4` (16px), `5` (20px), `6` (24px), `8` (32px), `10` (40px), `12` (48px), `16` (64px), `20` (80px), `24` (96px).

### D. Skala Border Radius
`none` (0px), `sm` (2px), `default` (4px), `md` (6px), `lg` (8px), `xl` (12px), `2xl` (16px), `3xl` (24px), `full` (9999px).

---

## 4. Penggunaan CLI & MCP Tool

### Melalui CLI (`tokens.py`)
```bash
# Menampilkan daftar palet, tema, dan template
python tokens.py --list

# Mengaudit seluruh 32 pasangan warna terhadap standar WCAG 2.2 AA
python tokens.py --audit-contrast

# Merender kit komponen langsung ke kanvas FigCraft
python tokens.py --palette stone
python tokens.py --starter-buttons --theme editorial-paper
python tokens.py --starter-badges --theme obsidian-studio
python tokens.py --segmented-control --theme slate-instrument
python tokens.py --data-table --theme botanical-ledger
python tokens.py --state-cards --theme obsidian-studio
python tokens.py --theme-board --theme editorial-paper

# Mengekspor token ke Tailwind CSS atau CSS Custom Properties
python tokens.py --export-tailwind
python tokens.py --export-css --theme editorial-paper
```

### Melalui MCP Tool (`figcraft_render_template` & `figcraft_get_tokens`)
Asisten AI dapat merender template langsung melalui protokol MCP tanpa menjalankan perintah shell:
- `figcraft_render_template(template="state_cards", theme="editorial-paper")`
- `figcraft_render_template(template="data_table", theme="obsidian-studio", dry_run=true)` (mengembalikan payload batch JSON secara headless)
- `figcraft_get_tokens(category="themes", response_format="markdown")`

---

## 5. Python API & Exporter

```python
from tokens import (
    audit_theme_contrast,
    build_template_commands,
    export_css_variables,
    export_tailwind_theme,
    get_color,
    get_theme,
)

theme = get_theme("editorial-paper")
primary_hex = get_color("indigo-600")
batch_steps = build_template_commands("buttons", theme_name="obsidian-studio")
css_vars = export_css_variables("botanical-ledger")
```
