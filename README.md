# FigCraft Universal MCP Bridge

Jembatan Model Context Protocol (MCP) dua arah (*Two-Way Design & Code*) untuk menghubungkan AI Coding Agent dengan aplikasi desain interface FigCraft.

Dengan repositori ini, berbagai AI assistant di komputer Anda (Google AntiGravity CLI/IDE, OpenCode CLI, Cursor, Claude Desktop) dapat:
1. **Text-to-UI**: Merancang dan memodifikasi komponen visual di kanvas desktop FigCraft secara real-time.
2. **Design-to-Code**: Membaca elemen desain visual di FigCraft dan mengonversinya secara presisi menjadi kode frontend (React + Tailwind CSS, Flutter, atau HTML/CSS).

---

## Fitur Utama

- **Two-Way Design-to-Code**: Dilengkapi helper AST cleaner (`codegen_helper.py`) yang memangkas ribuan baris dump JSON mentah menjadi token semantik ringkas (hemat token AI hingga 50-70%).
- **Lazy / On-Demand Launch**: Jendela GUI FigCraft **hanya terbuka ketika AI benar-benar memanggil tool desain (`tools/call`)**. Booting AI CLI/IDE tetap hening, cepat, dan bersih.
- **100% Portabel & Dinamis**: Nol path user yang di-hardcode. Bekerja otomatis menggunakan path Python dan profil user di laptop masing-masing.
- **Deteksi Otomatis Multi-Platform**: Mendukung Windows, macOS, dan Linux.
- **Auto-Config 1-Klik**: Mengonfigurasi AntiGravity, OpenCode, Cursor, dan Claude Desktop secara otomatis.

---

## Struktur File

```
figcraft-mcp/
├── bridge.py                # Smart MCP bridge runner (lazy launch & dynamic paths)
├── codegen_helper.py        # Tokenizer & AST cleaner untuk workflow Design-to-Code
├── install.py               # Auto-installer untuk seluruh AI client
├── install.bat              # Installer 1-klik untuk pengguna Windows
├── install.sh               # Installer untuk macOS / Linux
├── uninstall.bat            # Uninstaller 1-klik jika ingin mencopot konfigurasi
├── test_connection.py       # Script verifikasi koneksi & tes pembuatan badge kanvas
├── test_design_to_code.py   # Script verifikasi konversi desain FigCraft ke React
├── examples/                # Contoh komponen hasil konversi (WeatherWidget.tsx)
├── skills/                  # Kumpulan skill panduan AI
│   ├── figcraft-designer/       # Panduan pembuatan desain di kanvas FigCraft
│   └── figcraft-design-to-code/ # Panduan konversi desain kanvas ke kode frontend
├── INSTALLATION.md          # Panduan instalasi mendalam (manual & otomatis)
├── .gitignore               # Pengabaian file cache & temporer
└── README.md                # Dokumentasi proyek
```

---

## Panduan Pemasangan

Untuk panduan mendalam dan langkah demi langkah (termasuk instalasi manual per AI client, konfigurasi shortcut, dan pemecahan masalah), silakan baca:
👉 **[INSTALLATION.md](./INSTALLATION.md)**

### Ringkasan Cepat (1-Klik):

#### Di Windows:
Cukup klik ganda file **`install.bat`**, atau jalankan di terminal:
```powershell
python install.py
```

#### Di macOS / Linux:
```bash
chmod +x install.sh
./install.sh
```

---

## Verifikasi Instalasi

Jalankan script verifikasi untuk memastikan koneksi berjalan lancar:
```bash
# Uji koneksi MCP & pembuatan elemen di kanvas
python test_connection.py

# Uji pipeline Design-to-Code (menghasilkan examples/WeatherWidget.tsx)
python test_design_to_code.py
```

---

## Contoh Prompt Penggunaan

### 1. Membuat Desain di FigCraft (Text-to-UI)
- *"Buat komponen kartu login modern dengan latar gelap, input email, input password, dan tombol masuk di FigCraft."*
- *"Rancang navbar aplikasi web responsif lengkap dengan logo dan tautan menu di kanvas FigCraft."*
- *"Buat dashboard card metrik penjualan bulanan dengan indikator persentase pertumbuhan."*

### 2. Mengubah Desain FigCraft Menjadi Kode (Design-to-Code)
- *"Baca card cuaca yang ada di FigCraft, lalu ubah menjadi komponen React Tailwind CSS yang responsif."*
- *"Konversikan frame terpilih di FigCraft menjadi widget Flutter."*
- *"Ekstrak token warna dan typography dari kanvas FigCraft ke dalam file tailwind.config.js."*
