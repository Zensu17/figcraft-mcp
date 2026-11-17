# FigCraft Universal MCP Bridge

Jembatan Model Context Protocol (MCP) untuk menghubungkan AI Coding Agent dengan aplikasi desain interface FigCraft.

Dengan repositori ini, berbagai AI assistant di komputer Anda (Google AntiGravity CLI/IDE, OpenCode CLI, Cursor, Claude Desktop) dapat langsung merancang dan memodifikasi komponen visual di kanvas desktop FigCraft secara real-time.

---

## Fitur Utama

- **100% Portabel & Dinamis**: Tidak ada path user yang di-hardcode. Setiap laptop atau komputer akan otomatis menggunakan direktori dan Python miliknya masing-masing.
- **Deteksi Otomatis (Windows, macOS, Linux)**: Mencari lokasi instalasi FigCraft GUI dan CLI secara mandiri.
- **Auto-Launch GUI**: Jika aplikasi FigCraft belum dibuka saat Anda memberi prompt ke AI, bridge akan otomatis membukanya dengan loopback control port (`--control 1984`).
- **Pewarisan Protokol stdio**: Mengalirkan instruksi JSON-RPC langsung ke engine `figcraft-cli mcp --attach 1984` dengan fallback ke mode headless jika diperlukan.

---

## Struktur File

```
figcraft-mcp/
├── bridge.py           # Core smart bridge runner (zero hardcoded paths)
├── install.py          # Script konfigurasi otomatis untuk semua AI client
├── install.bat         # Installer 1-klik untuk pengguna Windows
├── install.sh          # Installer untuk macOS / Linux
├── test_connection.py  # Script pengujian koneksi & pembuatan elemen kanvas
├── INSTALLATION.md     # Panduan instalasi mendalam (manual & otomatis)
├── .gitignore          # Pengabaian file cache & temporer
└── README.md           # Ringkasan proyek
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
python test_connection.py
```
Script akan memeriksa handshake MCP, menghitung 19 tool desain, dan langsung menggambar sebuah badge tes hijau di kanvas FigCraft.

---

## Contoh Prompt Penggunaan

Setelah terpasang, Anda bisa langsung mengetikkan instruksi desain di AI client pilihan Anda:

- *"Buat komponen kartu login modern dengan latar gelap, input email, input password, dan tombol masuk di FigCraft."*
- *"Rancang navbar aplikasi web responsif lengkap dengan logo dan tautan menu di kanvas FigCraft."*
- *"Buat dashboard card metrik penjualan bulanan dengan indikator persentase pertumbuhan."*
- *"Buat card profil minimalis dengan avatar, nama, status ketersediaan, dan tombol kontak."*
