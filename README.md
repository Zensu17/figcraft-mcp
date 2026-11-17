# FigCraft Universal MCP Bridge

> **Connect any AI Coding Agent to FigCraft with Two-Way Design & Code capabilities.**  
> *Hubungkan AI Coding Agent ke FigCraft dengan kemampuan desain dan konversi kode dua arah.*

[English](#english) | [Bahasa Indonesia](#bahasa-indonesia)

---

<a name="english"></a>
## English

### Overview
**FigCraft Universal MCP Bridge** connects AI coding assistants (Google AntiGravity CLI/IDE, OpenCode CLI, Cursor, Claude Desktop) to **FigCraft** (the fast, native open-source Figma alternative written in pure Rust) via the Model Context Protocol (MCP).

It provides a complete **Two-Way Workflow**:
1. **Text-to-UI**: AI generates frames, buttons, layouts, and components directly onto the live FigCraft desktop canvas.
2. **Design-to-Code**: AI inspects visual designs on your FigCraft canvas and translates them into clean production code (React + Tailwind CSS, Flutter, or HTML/CSS).

---

### Key Features

- **⚡ Lazy / On-Demand Launch**: When you open your AI CLI or IDE, the bridge starts silently in headless mode (takes <50ms, zero windows opened). The FigCraft desktop GUI opens **ONLY** when you actually ask the AI to design something (`tools/call`).
- **🔄 Two-Way Design-to-Code**: Built-in AST cleaner (`codegen_helper.py`) strips noisy coordinates and extracts semantic tokens (`flex`, `padding`, `gap`, `colors`, `typography`), reducing token consumption by 50–70%.
- **💻 100% Portable**: No hardcoded usernames or paths. Runs dynamically on any computer (Windows, macOS, Linux).
- **🚀 1-Click Auto Installer**: Automatically registers the MCP server in AntiGravity, OpenCode, Cursor, and Claude Desktop, and configures desktop shortcuts.
- **🛡️ Clean Uninstaller**: One-click removal anytime without leaving residual files.

---

### File Structure

```
figcraft-mcp/
├── bridge.py                # Smart MCP bridge (lazy launch & dynamic paths)
├── codegen_helper.py        # AST cleaner & tokenizer for Design-to-Code
├── install.py               # Auto-installer across all AI clients
├── install.bat              # 1-click installer for Windows
├── install.sh               # 1-click installer for macOS / Linux
├── uninstall.bat            # 1-click uninstaller
├── test_connection.py       # Handshake & canvas element creation test
├── test_design_to_code.py   # Automated Design-to-Code verification
├── examples/                # Generated code output (e.g., WeatherWidget.tsx)
├── skills/                  # AI instruction skills
│   ├── figcraft-designer/       # Rules for building clean UI on FigCraft canvas
│   └── figcraft-design-to-code/ # Rules for converting visual designs to React/Flutter
├── docs/                    # Architecture documentation
├── INSTALLATION.md          # Comprehensive step-by-step setup guide
└── README.md                # Project documentation
```

---

### Quick Installation (1-Click)

#### Windows
Double-click **`install.bat`**, or run in PowerShell:
```powershell
python install.py
```

#### macOS / Linux
```bash
chmod +x install.sh
./install.sh
```

For detailed manual instructions for each AI client, see **[INSTALLATION.md](./INSTALLATION.md)**.

---

### How to Use (Step-by-Step)

#### 1. Designing on FigCraft Canvas (Text-to-UI)
Ask any AI agent (AntiGravity, OpenCode, Cursor):
- *"Create a modern dark-mode login form with email, password, and an indigo submit button in FigCraft."*
- *"Design a responsive music player card with album art, progress bar, and playback controls in FigCraft."*
- *"Build an analytics revenue dashboard card with percentage growth indicators."*

*Result*: FigCraft automatically opens on demand and draws the components in real-time.

#### 2. Converting Canvas Designs to Code (Design-to-Code)
Select or point to any frame in FigCraft, then prompt your AI:
- *"Read the weather widget in FigCraft and convert it into a responsive React Tailwind CSS component."*
- *"Convert the selected card in FigCraft to a Flutter widget."*
- *"Extract colors and typography from FigCraft into a tailwind.config.js file."*

---

### Verification & Testing

Verify that your bridge and codegen pipeline work properly:
```bash
# 1. Test MCP connection and canvas badge creation
python test_connection.py

# 2. Test Design-to-Code conversion (outputs examples/WeatherWidget.tsx)
python test_design_to_code.py
```

### Uninstallation
Run `uninstall.bat` or:
```bash
python install.py --uninstall
```

---

<a name="bahasa-indonesia"></a>
## Bahasa Indonesia

### Gambaran Umum
**FigCraft Universal MCP Bridge** menghubungkan berbagai AI coding assistant (Google AntiGravity CLI/IDE, OpenCode CLI, Cursor, Claude Desktop) ke **FigCraft** (alternatif Figma open-source berbasis pure Rust yang sangat cepat dan ringan) melalui Model Context Protocol (MCP).

Menyediakan **Alur Kerja Dua Arah (Two-Way Workflow)**:
1. **Text-to-UI**: AI menggambar frame, tombol, teks, dan komponen langsung di kanvas desktop FigCraft secara real-time.
2. **Design-to-Code**: AI membaca elemen visual yang ada di FigCraft dan menerjemahkannya menjadi kode frontend siap pakai (React + Tailwind CSS, Flutter, atau HTML/CSS).

---

### Fitur Utama

- **⚡ Lazy / On-Demand Launch**: Saat membuka AI CLI atau IDE, bridge berjalan hening di background (<50ms, tanpa membuka jendela). Aplikasi GUI FigCraft **HANYA** akan terbuka ketika Anda benar-benar menyuruh AI mendesain (`tools/call`).
- **🔄 Two-Way Design-to-Code**: Dilengkapi helper AST cleaner (`codegen_helper.py`) yang memangkas ribuan baris koordinat mentah FigCraft menjadi token semantik ringkas (menghemat 50–70% token AI).
- **💻 100% Portabel**: Tidak ada hardcode path user. Bekerja otomatis di komputer mana pun (Windows, macOS, Linux).
- **🚀 Installer 1-Klik**: Mengonfigurasi AntiGravity, OpenCode, Cursor, dan Claude Desktop secara otomatis.
- **🛡️ Uninstaller Bersih**: Pencopotan konfigurasi kapan saja dengan sekali klik.

---

### Cara Pemasangan Cepat

#### Windows:
Klik ganda file **`install.bat`**, atau jalankan di terminal:
```powershell
python install.py
```

#### macOS / Linux:
```bash
chmod +x install.sh
./install.sh
```

Panduan manual langkah-demi-langkah tersedia di **[INSTALLATION.md](./INSTALLATION.md)**.

---

### Cara Menggunakan

#### 1. Membuat Desain di Kanvas FigCraft
Ketikkan prompt di AI apa pun yang terhubung:
- *"Buat komponen kartu login modern dengan latar gelap, input email, input password, dan tombol masuk di FigCraft."*
- *"Rancang music player card lengkap dengan album art, progress bar, dan tombol playback di FigCraft."*

#### 2. Mengubah Desain FigCraft Menjadi Kode
Pilih elemen di FigCraft lalu ketikkan:
- *"Baca card cuaca yang ada di FigCraft, lalu ubah menjadi komponen React Tailwind CSS yang responsif."*
- *"Konversikan frame terpilih di FigCraft menjadi widget Flutter."*

---

### Pengujian & Verifikasi

```bash
# Uji koneksi MCP & pembuatan elemen kanvas
python test_connection.py

# Uji konversi desain ke kode React (menghasilkan examples/WeatherWidget.tsx)
python test_design_to_code.py
```
