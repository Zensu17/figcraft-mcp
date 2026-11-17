# Panduan Pemasangan FigCraft Universal MCP Bridge

> Panduan komprehensif langkah demi langkah untuk menghubungkan FigCraft dengan asisten AI di komputer Anda.

[Read in English](INSTALLATION.md) | **Bahasa Indonesia**

---

## Daftar Isi
1. [Prasyarat Sistem](#1-prasyarat-sistem)
2. [Mengunduh atau Mengkloning Repositori](#2-mengunduh-atau-mengkloning-repositori)
3. [Metode 1: Pemasangan Otomatis 1-Klik (Direkomendasikan)](#3-metode-1-pemasangan-otomatis-1-klik-direkomendasikan)
4. [Metode 2: Konfigurasi Manual per Asisten AI](#4-metode-2-konfigurasi-manual-per-asisten-ai)
5. [Pengaturan Pintasan Desktop Windows](#5-pengaturan-pintasan-desktop-windows)
6. [Pengujian dan Verifikasi Koneksi](#6-pengujian-dan-verifikasi-koneksi)
7. [Pemecahan Masalah dan Tanya Jawab (FAQ)](#7-pemecahan-masalah-dan-tanya-jawab-faq)
8. [Tabel Referensi 19 Alat MCP FigCraft](#8-tabel-referensi-19-alat-mcp-figcraft)

---

## 1. Prasyarat Sistem

Sebelum melakukan pemasangan, pastikan komponen berikut sudah tersedia di komputer Anda:

### A. Python versi 3.8 atau Lebih Baru
- Unduh dari situs web resmi [python.org](https://www.python.org/downloads/).
- **Penting bagi pengguna Windows**: Pada jendela installer Python, beri tanda centang pada opsi **"Add python.exe to PATH"**.
- Periksa ketersediaan Python melalui terminal:
  ```bash
  python --version
  ```

### B. Aplikasi FigCraft Desktop dan CLI
- Unduh dan pasang aplikasi FigCraft di komputer Anda.
- Di sistem operasi Windows, lokasi standar instalasi berada di:
  `C:\Program Files\ArtCraft\FigCraft\` (berisi `figcraft.exe` dan `figcraft-cli.exe`).
- Jika Anda memasang FigCraft di direktori khusus atau partisi lain, pastikan folder tersebut ditambahkan ke variabel sistem `PATH`, atau atur variabel lingkungan `FIGCRAFT_PATH` dan `FIGCRAFT_CLI_PATH`.

---

## 2. Mengunduh atau Mengkloning Repositori

### Opsi A: Menggunakan Git (Direkomendasikan)
Buka terminal dan jalankan:
```bash
git clone https://github.com/Zensu17/figcraft-mcp.git
cd figcraft-mcp
```

### Opsi B: Unduh Berkas ZIP
1. Buka halaman repositori di GitHub.
2. Klik tombol **Code**, lalu pilih **Download ZIP**.
3. Ekstrak berkas ZIP ke folder pilihan Anda (contohnya `D:\Code\figcraft-mcp`).
4. Buka terminal di dalam folder hasil ekstraksi tersebut.

---

## 3. Metode 1: Pemasangan Otomatis 1-Klik (Direkomendasikan)

Skrip pemasang otomatis akan mendeteksi lokasi Python dan FigCraft secara mandiri, kemudian menuliskan konfigurasi ke seluruh asisten AI yang terpasang di komputer Anda.

### Pada Windows
Klik ganda file **`install.bat`**, atau jalankan perintah ini di PowerShell:
```powershell
python install.py
```

### Pada macOS dan Linux
Jalankan perintah berikut di terminal:
```bash
chmod +x install.sh
./install.sh
```

### Apa yang Dilakukan oleh Skrip Pemasang Otomatis?
1. Memeriksa ketersediaan dan lokasi `figcraft.exe` serta `figcraft-cli.exe`.
2. Mendaftarkan FigCraft ke Google AntiGravity pada file `~/.gemini/config/mcp_config.json`.
3. Mendaftarkan FigCraft ke OpenCode CLI pada file `~/.config/opencode/opencode.json`.
4. Mendaftarkan FigCraft ke Cursor IDE pada file `~/.cursor/mcp.json`.
5. Mendaftarkan FigCraft ke Claude Desktop (jika aplikasi Claude terpasang).
6. Memperbarui pintasan desktop dan Start Menu Windows agar menyertakan flag kendali `--control 1984`.

---

## 4. Metode 2: Konfigurasi Manual per Asisten AI

Jika Anda lebih memilih mendaftarkan jembatan secara manual ke masing-masing asisten AI, gunakan konfigurasi berikut.

Ganti teks `<REPO_PATH>` dengan alamat folder repositori ini di komputer Anda (contohnya `D:\\Code\\figcraft-mcp` pada Windows atau `/home/namauser/figcraft-mcp` pada Linux/macOS).

### A. Google AntiGravity (CLI dan IDE)
Buka atau buat file konfigurasi di: `~/.gemini/config/mcp_config.json`
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": ["<REPO_PATH>\\bridge.py"]
    }
  }
}
```

### B. OpenCode CLI
Jalankan perintah terminal berikut:
```bash
opencode mcp add --global FigCraft -- python <REPO_PATH>/bridge.py
```
Atau tambahkan langsung ke file `~/.config/opencode/opencode.json`:
```json
{
  "mcp": {
    "FigCraft": {
      "type": "local",
      "command": ["python", "<REPO_PATH>\\bridge.py"],
      "enabled": true
    }
  }
}
```

### C. Cursor IDE
Buka atau buat file konfigurasi di: `~/.cursor/mcp.json`
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": ["<REPO_PATH>\\bridge.py"]
    }
  }
}
```

### D. Claude Desktop
- Lokasi Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Lokasi macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": ["<REPO_PATH>\\bridge.py"]
    }
  }
}
```

---

## 5. Pengaturan Pintasan Desktop Windows

Agar aplikasi FigCraft selalu siap menerima perintah otomatis saat Anda membukanya secara manual:
1. Klik kanan pada shortcut **FigCraft** di Desktop atau Start Menu, lalu pilih **Properties**.
2. Pada kolom **Target**, tambahkan spasi dan tulisan `--control 1984` di bagian paling belakang.
   - Contoh susunan: `"C:\Program Files\ArtCraft\FigCraft\figcraft.exe" --control 1984`
3. Klik tombol **Apply**, lalu klik **OK**.

Catatan: Jika Anda menggunakan installer otomatis `install.bat`, langkah ini sudah dilakukan secara otomatis.

---

## 6. Pengujian dan Verifikasi Koneksi

Setelah pemasangan selesai, lakukan pengujian untuk memastikan komunikasi berjalan lancar:

```bash
# 1. Uji koneksi jembatan dan pembuatan lencana teks di kanvas
python test_connection.py

# 2. Uji konversi data desain visual menjadi kode React Tailwind
python test_design_to_code.py
```

Lihat jendela aplikasi FigCraft Anda: lencana pengujian akan otomatis muncul dan tergambar di atas kanvas.

---

## 7. Pemecahan Masalah dan Tanya Jawab (FAQ)

### Masalah 1: Muncul pesan error 'python' is not recognized
- **Penyebab**: Python belum terdaftar pada variabel sistem PATH di komputer Anda.
- **Solusi**: Jalankan kembali penginstal resmi Python, pilih opsi "Modify", lalu pastikan opsi **"Add python.exe to PATH"** dicentang sampai selesai.

### Masalah 2: Muncul pesan error 'figcraft-cli not found'
- **Penyebab**: Aplikasi FigCraft dipasang di lokasi non-standar sehingga skrip tidak dapat menemukannya secara otomatis.
- **Solusi**: Tetapkan alamat lokasi instalasi secara manual melalui variabel lingkungan:
  ```powershell
  $env:FIGCRAFT_CLI_PATH = "D:\Jalur\Ke\figcraft-cli.exe"
  $env:FIGCRAFT_PATH = "D:\Jalur\Ke\figcraft.exe"
  ```

### Masalah 3: Terjadi konflik port jaringan (Port 1984 sedang dipakai)
- **Penyebab**: Ada aplikasi lain yang menggunakan port jaringan 1984 di komputer Anda.
- **Solusi**: Anda dapat mengganti port dengan mengatur variabel lingkungan `FIGCRAFT_PORT`:
  ```powershell
  $env:FIGCRAFT_PORT = "2000"
  ```

### Masalah 4: Aplikasi FigCraft terbuka tetapi kanvas tidak merespons
- **Penyebab**: Antarmuka FigCraft dibuka tanpa parameter kendali `--control 1984`.
- **Solusi**: Tutup jendela FigCraft yang sedang terbuka. Biarkan jembatan MCP membukanya secara otomatis saat AI mulai bekerja, atau pastikan shortcut dibuka dengan parameter `--control 1984`.

---

## 8. Tabel Referensi 19 Alat MCP FigCraft

Ketika terhubung, asisten AI Anda memiliki akses ke 19 fungsi bawaan kanvas FigCraft:

| Nama Alat | Fungsi dan Kegunaan |
| :--- | :--- |
| `create_node` | Membuat frame, teks, bentuk geometris, vektor, atau komponen baru di kanvas |
| `set_properties` | Mengubah properti elemen (warna isi, radius sudut, layout, padding, font) |
| `batch` | Menjalankan banyak perintah sekaligus dalam 1 riwayat undo |
| `inspect_document` | Mengambil seluruh pohon hierarki layer dokumen dalam format JSON |
| `get_node` | Mengambil detail spesifik dan properti dari sebuah ID layer |
| `screenshot` | Mengambil tangkapan gambar visual (PNG) dari seluruh kanvas atau layer tertentu |
| `export` | Mengekspor frame pilihan ke berkas gambar (PNG, SVG, JPG, PDF) |
| `run_command` | Menjalankan perintah internal dari katalog 400+ fungsi FigCraft |
| `undo` / `redo` | Membatalkan atau mengulang langkah perubahan dokumen |
| `open_file` / `save_file` | Membuka atau menyimpan berkas dokumen berformat `.figcraft` |
| `select` | Memilih elemen tertentu yang sedang aktif di atas kanvas |
| `pointer` | Mensimulasikan klik, geser (drag), dan navigasi kursor mouse di kanvas |
| `key` / `type_text` | Mensimulasikan penekanan tombol keyboard dan pengetikan teks langsung |
| `inspect_ui` | Memeriksa status antarmuka pengguna aplikasi desktop |
| `wait_for_changes` | Menunggu perubahan status kanvas selesai diproses |
