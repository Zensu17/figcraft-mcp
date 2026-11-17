# FigCraft Universal MCP Bridge

> Hubungkan AI Coding Assistant ke FigCraft dengan alur kerja desain dan konversi kode dua arah.

[Read in English](README.md) | **Bahasa Indonesia**

---

## Gambaran Umum

FigCraft Universal MCP Bridge menghubungkan berbagai asisten kecerdasan buatan (seperti Google AntiGravity, OpenCode, Cursor, dan Claude Desktop) langsung ke aplikasi FigCraft.

FigCraft adalah aplikasi desain antarmuka open-source yang dibangun menggunakan bahasa pemrograman Rust sehingga beroperasi secara cepat, ringan, dan mandiri di komputer lokal Anda.

Melalui integrasi Model Context Protocol (MCP), Anda mendapatkan alur kerja dua arah yang lengkap:
1. **Text-to-UI (Teks ke Desain)**: AI menggambar komponen antarmuka, tombol, formulir, dan layout langsung di kanvas visual FigCraft secara otomatis.
2. **Design-to-Code (Desain ke Kode)**: AI membaca elemen visual yang ada di kanvas FigCraft dan menerjemahkannya menjadi kode frontend siap pakai (React dengan Tailwind CSS, atau Flutter).

---

## Fitur Utama

- **Peluncuran Berdasarkan Permintaan (Lazy Launch)**: Saat Anda membuka terminal atau IDE, jembatan penghubung berjalan hening tanpa membuka jendela baru (kurang dari 50 milidetik). Antarmuka FigCraft hanya akan terbuka otomatis ketika Anda memberi perintah mendesain kepada AI.
- **Konversi Desain ke Kode yang Hemat Token**: Dilengkapi pembersih pohon sintaks visual (`codegen_helper.py`) yang mereduksi data koordinat mentah hingga 50-70%, sehingga pemakaian kuota token AI menjadi jauh lebih hemat dan efisien.
- **Portabel dan Bebas Hardcode**: Tidak bergantung pada nama pengguna atau direktori tertentu. Dapat dijalankan secara dinamis di Windows, macOS, dan Linux.
- **Pemasang Otomatis 1-Klik**: Secara otomatis mendeteksi Python, lokasi instalasi FigCraft, dan mendaftarkan konfigurasi ke Google AntiGravity, OpenCode, Cursor, dan Claude Desktop sekaligus.
- **Pencopot Pemasangan Bersih**: Dilengkapi skrip pembersih yang dapat mengembalikan seluruh konfigurasi AI ke kondisi awal tanpa meninggalkan sisa file konfigurasi.

---

## Struktur Direktori

```
figcraft-mcp/
|-- bridge.py                # Jembatan cerdas MCP (lazy launch dan resolusi jalur otomatis)
|-- codegen_helper.py        # Pembersih AST dan tokenizer untuk konversi Desain-ke-Kode
|-- check.py                 # Alat diagnosis mandiri status sistem dan konfigurasi AI
|-- check.bat                # Runner 1-klik diagnosis kesehatan untuk Windows
|-- check.sh                 # Runner 1-klik diagnosis kesehatan untuk macOS dan Linux
|-- install.py               # Logika pemasang otomatis lintas platform
|-- install.bat              # Pemasang 1-klik untuk Windows
|-- install.sh               # Pemasang 1-klik untuk macOS dan Linux
|-- uninstall.bat            # Pencopot pemasangan 1-klik
|-- test_connection.py       # Pengujian koneksi jembatan dan pembuatan elemen kanvas
|-- test_design_to_code.py   # Pengujian otomatis alur kerja konversi Desain-ke-Kode
|-- skills/                  # Kumpulan aturan instruksi untuk asisten AI
|   |-- figcraft-designer/       # Aturan menggambar UI rapi di kanvas FigCraft
|   |-- figcraft-design-to-code/ # Aturan membaca desain visual menjadi kode React/Flutter
|-- docs/                    # Dokumentasi arsitektur dan spesifikasi teknis
|-- INSTALLATION.md          # Panduan instalasi lengkap (Bahasa Inggris)
|-- INSTALLATION.id.md       # Panduan instalasi lengkap (Bahasa Indonesia)
|-- tokens.py                # Modul API token desain dan generator komponen kanvas
|-- tokens.json              # Kamus token desain standar (warna, spasi, radius)
|-- TOKENS.md                # Panduan referensi token desain (Bahasa Inggris)
|-- TOKENS.id.md             # Panduan referensi token desain (Bahasa Indonesia)
|-- PROMPTS.md               # Kumpulan formula prompt siap pakai (Bahasa Inggris)
|-- PROMPTS.id.md            # Kumpulan formula prompt siap pakai (Bahasa Indonesia)
|-- README.md                # Dokumentasi utama (Bahasa Inggris)
`-- README.id.md             # Dokumentasi utama (Bahasa Indonesia)
```

---

## Panduan Pemasangan Cepat

### Pengguna Windows
Klik ganda pada file **`install.bat`**, atau jalankan perintah berikut melalui PowerShell:
```powershell
python install.py
```

### Pengguna macOS dan Linux
Berikan izin eksekusi pada skrip lalu jalankan:
```bash
chmod +x install.sh
./install.sh
```

Untuk panduan pemasangan manual atau konfigurasi lanjutan, silakan baca [PANDUAN LENGKAP INSTALASI (INSTALLATION.id.md)](./INSTALLATION.id.md).

---

## Cara Penggunaan

Untuk kumpulan formula prompt siap pakai pada 6 kategori antarmuka, lihat panduan **[PROMPTS.id.md](./PROMPTS.id.md)**.

Setelah terpasang, buka asisten AI yang Anda gunakan (AntiGravity, Cursor, OpenCode, atau Claude Desktop).

### 1. Membuat Desain Baru di Kanvas (Text-to-UI)
Ketikkan instruksi dalam bahasa sehari-hari. Contoh perintah:
- "Buat formulir login modern dengan tema gelap di FigCraft, lengkap dengan input email, password, dan tombol masuk berwarna biru indigo."
- "Rancang kartu pemutar musik responsif di FigCraft dengan album art, indikator durasi lagu, dan tombol kendali putar musik."
- "Buat kartu dashboard analitik pendapatan bulanan di FigCraft dengan persentase pertumbuhan hijau."

Hasilnya: Aplikasi FigCraft akan terbuka secara otomatis dan elemen-elemen tersebut langsung digambar di atas kanvas.

### 2. Mengubah Desain Kanvas Menjadi Kode (Design-to-Code)
Pilih elemen di kanvas FigCraft, lalu minta AI untuk membacanya:
- "Baca elemen kartu cuaca yang sedang aktif di FigCraft, lalu ubah menjadi komponen React Tailwind CSS yang responsif."
- "Konversikan kartu profil yang ada di kanvas FigCraft menjadi widget Flutter."
- "Ekstrak palet warna dan tipografi dari desain FigCraft ke dalam format file tailwind.config.js."

---

## Pengujian dan Verifikasi

Pastikan kesehatan sistem, koneksi jembatan, dan alur pembuatan kode berfungsi dengan menjalankan pengujian berikut:

```bash
# 1. Menjalankan diagnosis mandiri status Python, lokasi FigCraft, dan konfigurasi AI
python check.py
# (Pada Windows, Anda juga cukup klik ganda check.bat)

# 2. Menguji koneksi MCP dan membuat badge penanda di kanvas FigCraft
python test_connection.py

# 3. Menguji alur pembacaan desain dan pembuatan kode React
python test_design_to_code.py
```

Periksa jendela aplikasi FigCraft Anda: elemen uji akan digambar secara langsung di atas kanvas.

---

## Menghapus Pemasangan (Uninstall)

Untuk mencopot konfigurasi jembatan dari seluruh asisten AI:
- Pada Windows: Klik ganda **`uninstall.bat`**.
- Melalui terminal: Jalankan perintah `python install.py --uninstall`.
