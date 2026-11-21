# FigCraft Universal MCP Bridge

> Hubungkan AI Coding Assistant ke FigCraft dengan MCP Primitives lengkap, Design-to-Code multi-framework, template terverifikasi WCAG, dan keamanan STRIDE.

[Read in English](README.md) | **Bahasa Indonesia**

---

## Gambaran Umum

FigCraft Universal MCP Bridge menghubungkan asisten AI modern (Google AntiGravity, OpenCode CLI, Cursor, dan Claude Desktop) langsung ke FigCraft, aplikasi desain antarmuka open-source berbasis Rust.

Lebih dari sekadar proxy pass-through, jembatan ini berperan sebagai **MCP Protocol Middleware** (100% Python standard library, tanpa dependensi eksternal) yang menyediakan:
1. **Text-to-UI & Template Terkurasi**: Menggambar layout kustom atau merender kit komponen terverifikasi WCAG 2.2 AA langsung ke kanvas FigCraft dalam satu langkah undo.
2. **Design-to-Code Multi-Framework**: Membaca frame kanvas, mengekstrak semantic UI AST dan typed props (pola Code Connect), lalu menghasilkan kode **React + Tailwind CSS**, **Vue 3 SFC**, **Flutter**, atau **HTML/CSS semantik**.
3. **MCP Resources, Prompts & Guardrails**: Mengekspos token desain, panduan engine, dan semantic AST langsung via protokol MCP sekaligus menormalisasi ketidakcocokan nama properti dari LLM secara otomatis.
4. **Hardening Keamanan STRIDE**: Memvalidasi ukuran/kedalaman payload JSON-RPC, membatasi port loopback unprivileged, memblokir path UNC/traversal, serta mensterilkan output codegen dari XSS dan CSS injection.

---

## Fitur Utama

- **Peluncuran Berdasarkan Permintaan (Lazy Launch)**: Berjalan hening dalam mode headless saat CLI boot (< 50 ms tanpa membuka jendela). GUI FigCraft hanya diluncurkan otomatis ketika tool kanvas live atau resource kanvas live (`figcraft://document`, `figcraft://node/...`, `figcraft://canvas/semantic`) dipanggil.
- **MCP Primitives Middleware (`mcp_primitives.py`)**:
  - **Custom Resources**: `figcraft://tokens`, `figcraft://guidelines`, `figcraft://canvas/semantic`, dan template `figcraft://node/{id}/semantic`.
  - **Custom Prompts**: `figcraft_dashboard_card`, `figcraft_auth_screen`, `figcraft_navbar`, dan `figcraft_design_to_code`.
  - **Bridge Workflow Tools**: `figcraft_get_tokens`, `figcraft_extract_semantic_ast`, `figcraft_generate_code`, dan `figcraft_render_template`.
  - **Guardrails Engine Otomatis**: Menormalisasi `strokeWidth` -> `strokeWeight`, `start`/`end`/`space-between` -> `min`/`max`/`spaceBetween`, serta `fontWeight` numerik -> `fontStyle` sebelum dikirim ke FigCraft.
- **Design-to-Code Multi-Framework (`codegen_helper.py`)**:
  - Reverse lookup warna, spacing, radius, dan tipografi dari `tokens.json` ke kelas Tailwind.
  - Ekstraksi typed props (`TEXT`, `BOOLEAN`, `VARIANT`, `SLOT`) untuk **React + Tailwind**, **Vue 3**, **Flutter**, dan **HTML/CSS**.
- **Sistem Desain WCAG 2.2 AA & 7 Template (`tokens.json`, `tokens.py`)**:
  - 4 tema terkurasi (`editorial-paper`, `obsidian-studio`, `slate-instrument`, `botanical-ledger`) dengan seluruh 32 pasangan warna lolos audit kontras >= 4.5:1.
  - 7 template komponen kanvas satu-undo (`palette_swatch`, `buttons`, `badges`, `segmented_control`, `data_table`, `state_cards`, `theme_board`).
- **Hardening Keamanan (`security.py`)**:
  - Pembatasan ukuran JSON-RPC (2 MiB), kedalaman objek (48), dan jumlah perintah batch (500).
  - Pemblokiran path UNC Windows (`\\host\share`), null byte, traversal `..`, serta dukungan allowlist direktori via `FIGCRAFT_ALLOWED_ROOTS`.
  - Validasi warna hex ketat dan escaping mustache Vue/entitas HTML pada generator kode.
- **Portabel Penuh**: Bebas hardcoded path, berjalan di Windows, macOS, dan Linux (Python 3.10+).

---

## Struktur Direktori

```
figcraft-mcp/
|-- bridge.py                # Smart MCP bridge (lazy launch, JSON-RPC multiplexing, batas keamanan)
|-- mcp_primitives.py        # Custom MCP Resources, Prompts, Workflow Tools & input guardrails
|-- security.py              # Validasi keamanan STRIDE, proteksi path, hex & log sanitizer
|-- codegen_helper.py        # Pembersih semantic AST, ekstraktor props & generator 4 framework
|-- tokens.py                # API token desain, auditor kontras WCAG AA, exporter CSS/Tailwind & 7 template
|-- tokens.json              # Kamus token desain, 4 tema terkurasi & token status dark/light
|-- check.py                 # Alat diagnosis mandiri sistem dan konfigurasi AI
|-- check.bat                # Runner 1-klik diagnosis kesehatan untuk Windows
|-- check.sh                 # Runner 1-klik diagnosis kesehatan untuk macOS dan Linux
|-- install.py               # Pemasang otomatis lintas platform
|-- install.bat              # Pemasang 1-klik untuk Windows
|-- install.sh               # Pemasang 1-klik untuk macOS dan Linux
|-- uninstall.bat            # Pencopot pemasangan 1-klik
|-- tests/                   # Suite unit test headless (tanpa perlu GUI)
|   |-- test_security_and_bridge.py  # Uji keamanan, XSS codegen, loopback socket & middleware bridge
|   `-- test_core_unit.py            # Unit test mcp_primitives, tokens & codegen_helper
|-- test_mcp_primitives.py   # Pengujian E2E stdio JSON-RPC terhadap bridge.py
|-- test_design_system.py    # Audit kontras WCAG & validasi skema batch 28 kombinasi template x tema
|-- test_design_to_code.py   # Pengujian pipeline Design-to-Code multi-framework
|-- test_connection.py       # Pengujian koneksi kanvas FigCraft live
|-- skills/                  # Instruksi skill untuk asisten AI
|   |-- figcraft-designer/       # Aturan engine, kontras WCAG & standar anti-slop UI
|   `-- figcraft-design-to-code/ # Alur Design-to-Code & pemetaan multi-framework
|-- docs/                    # Dokumentasi arsitektur dan spesifikasi teknis
|-- INSTALLATION.md          # Panduan instalasi lengkap (Bahasa Inggris)
|-- INSTALLATION.id.md       # Panduan instalasi lengkap (Bahasa Indonesia)
|-- TOKENS.md                # Referensi token, tema & template (Bahasa Inggris)
|-- TOKENS.id.md             # Referensi token, tema & template (Bahasa Indonesia)
|-- PROMPTS.md               # Formula prompt siap pakai (Bahasa Inggris)
|-- PROMPTS.id.md            # Formula prompt siap pakai (Bahasa Indonesia)
|-- README.md                # Dokumentasi utama (Bahasa Inggris)
`-- README.id.md             # Dokumentasi utama (Bahasa Indonesia)
```

---

## Panduan Pemasangan Cepat

### Pengguna Windows
Klik ganda **`install.bat`**, atau jalankan di PowerShell:
```powershell
python install.py
```

### Pengguna macOS dan Linux
```bash
chmod +x install.sh
./install.sh
```

Untuk pemasangan manual dan troubleshooting, baca **[INSTALLATION.id.md](./INSTALLATION.id.md)**.

---

## Variabel Environment Konfigurasi

| Variabel | Default | Fungsi |
| :--- | :--- | :--- |
| `FIGCRAFT_PORT` | `1984` | Port kontrol TCP loopback (divalidasi dalam rentang `1024..65535`). |
| `FIGCRAFT_PATH` | Deteksi otomatis | Override path binary GUI `figcraft`. |
| `FIGCRAFT_CLI_PATH` | Deteksi otomatis | Override path binary `figcraft-cli`. |
| `FIGCRAFT_ALLOWED_ROOTS` | Kosong (semua path lokal) | Daftar direktori yang diizinkan (dipisah path separator OS) untuk `open_file`/`save_file`/`export`. |
| `FIGCRAFT_DEBUG` | Kosong | Set ke `1` untuk mengaktifkan log debug ter-sanitasi ke `figcraft_bridge.log`. |

---

## Cara Penggunaan

Lihat **[PROMPTS.id.md](./PROMPTS.id.md)** untuk formula prompt siap pakai, dan **[TOKENS.id.md](./TOKENS.id.md)** untuk daftar tema, token, serta template komponen.

### 1. Render Template Terkurasi atau Desain Kustom (Text-to-UI)
- "Render template `state_cards` dengan tema `editorial-paper` di kanvas FigCraft."
- "Gunakan prompt `figcraft_dashboard_card` untuk membuat kartu metrik MRR `$148,520` dengan tren `+18.4%`."
- "Buat top navbar desktop di FigCraft dengan transparent flex wrappers (`fill: none`)."

### 2. Konversi Desain Kanvas ke Kode Produksi (Design-to-Code)
- "Jalankan `figcraft_generate_code` pada node 125 dengan framework `react-tailwind` dan typed props."
- "Konversikan node 125 ke `vue`, `flutter`, atau `html-css`."
- Alternatif CLI:
  ```bash
  python codegen_helper.py --node 125 --framework react-tailwind --out Card.tsx
  ```

---

## Pengujian dan Verifikasi

```bash
# 1. Suite unit test, keamanan & mock socket headless (tanpa perlu GUI FigCraft)
python -m unittest discover -s tests -v

# 2. Audit seluruh 32 pasangan warna tema & semantik terhadap WCAG 2.2 AA (>= 4.5:1)
python tokens.py --audit-contrast
python test_design_system.py

# 3. Verifikasi pipeline Design-to-Code multi-framework
python test_design_to_code.py

# 4. Verifikasi E2E MCP stdio middleware (23 tools, 6 resources, 3 templates, 10 prompts)
python test_mcp_primitives.py

# 5. Menjalankan diagnosis mandiri lingkungan
python check.py
```

---

## Menghapus Pemasangan (Uninstall)

- Windows: Klik ganda **`uninstall.bat`**.
- Terminal: Jalankan `python install.py --uninstall`.

---

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat berkas [LICENSE](LICENSE) untuk rincian lengkap.
