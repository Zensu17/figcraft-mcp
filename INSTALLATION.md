# Panduan Lengkap Pemasangan (Installation Guide)

Panduan langkah demi langkah untuk memasang dan menghubungkan **FigCraft Universal MCP Bridge** ke berbagai AI Coding Assistant di komputer Anda atau rekan Anda.

---

## Daftar Isi
1. [Prasyarat Sistem](#1-prasyarat-sistem)
2. [Unduh Repositori](#2-unduh-repositori)
3. [Metode 1: Pemasangan Otomatis (Rekomendasi)](#3-metode-1-pemasangan-otomatis-rekomendasi)
4. [Metode 2: Pemasangan Manual per AI Client](#4-metode-2-pemasangan-manual-per-ai-client)
   - [Google AntiGravity (CLI & IDE)](#a-google-antigravity-cli--ide)
   - [OpenCode CLI](#b-opencode-cli)
   - [Cursor IDE](#c-cursor-ide)
   - [Claude Desktop](#d-claude-desktop)
5. [Konfigurasi Shortcut FigCraft Desktop (Windows)](#5-konfigurasi-shortcut-figcraft-desktop-windows)
6. [Pengujian & Verifikasi Koneksi](#6-pengujian--verifikasi-koneksi)
7. [Penyelesaian Masalah (Troubleshooting)](#7-penyelesaian-masalah-troubleshooting)
8. [Referensi Tool MCP FigCraft](#8-referensi-tool-mcp-figcraft)

---

## 1. Prasyarat Sistem

Sebelum memulai, pastikan dua aplikasi ini sudah terpasang di komputer:

### A. Python 3.8 ke atas
- Unduh dari situs resmi [python.org](https://www.python.org/downloads/).
- **PENTING (Khusus Windows)**: Saat menjalankan installer Python, pastikan memberi centang pada opsi **"Add python.exe to PATH"** di halaman awal installer.
- Periksa di terminal:
  ```bash
  python --version
  ```

### B. Aplikasi FigCraft
- Pastikan FigCraft telah terpasang. Di Windows, installer resmi meletakkan program di:
  `C:\Program Files\ArtCraft\FigCraft\` (berisi `figcraft.exe` dan `figcraft-cli.exe`).
- Jika Anda memasangnya di direktori non-standar, cukup daftarkan foldernya ke PATH sistem atau atur variabel lingkungan `FIGCRAFT_PATH` dan `FIGCRAFT_CLI_PATH`.

---

## 2. Unduh Repositori

Pilih salah satu cara:

### Cara A: Menggunakan Git (Direkomendasikan)
Buka terminal dan jalankan:
```bash
git clone https://github.com/<username-anda>/figcraft-mcp.git
cd figcraft-mcp
```

### Cara B: Download ZIP
1. Buka halaman GitHub repositori.
2. Klik tombol hijau **Code** > **Download ZIP**.
3. Ekstrak file ZIP ke folder pilihan Anda (misal `D:\Code\figcraft-mcp` atau `C:\Projects\figcraft-mcp`).
4. Buka terminal di dalam folder hasil ekstraksi tersebut.

---

## 3. Metode 1: Pemasangan Otomatis (Rekomendasi)

Installer otomatis akan mendeteksi path Python Anda, mencari instalasi FigCraft, dan menulis konfigurasi ke semua AI client yang terpasang di komputer Anda.

### Di Windows
Cukup **klik ganda** file `install.bat`, atau jalankan di Command Prompt / PowerShell:
```powershell
python install.py
```

### Di macOS / Linux
Jalankan script bash:
```bash
chmod +x install.sh
./install.sh
```

**Apa yang dilakukan installer ini secara otomatis?**
1. Mencari file `figcraft.exe` dan `figcraft-cli.exe` di sistem Anda.
2. Mendaftarkan server MCP ke file config Google AntiGravity: `~/.gemini/config/mcp_config.json`.
3. Mendaftarkan server MCP ke file config OpenCode: `~/.config/opencode/opencode.json` (dan menjalankan `opencode mcp add` jika OpenCode ada di PATH).
4. Mendaftarkan server MCP ke file config Cursor: `~/.cursor/mcp.json`.
5. Mendaftarkan server MCP ke Claude Desktop (jika terpasang).
6. Di Windows: Memperbarui shortcut Start Menu FigCraft agar selalu membuka dengan parameter `--control 1984`.

---

## 4. Metode 2: Pemasangan Manual per AI Client

Jika Anda ingin mengonfigurasi AI client secara spesifik atau manual, gunakan konfigurasi berikut:

> **Catatan**: Ganti `<PATH_FOLDER_REPOSITORI>` dengan lokasi absolut folder proyek ini di laptop Anda (misal `D:\\Code\\figcraft-mcp` atau `/home/user/figcraft-mcp`). Gunakan double backslash `\\` jika di Windows.

### A. Google AntiGravity (CLI & IDE)
Buka atau buat file:
- **Windows**: `%USERPROFILE%\.gemini\config\mcp_config.json`
- **macOS / Linux**: `~/.gemini/config/mcp_config.json`

Tambahkan entri `"FigCraft"` di dalam blok `"mcpServers"`:
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": [
        "<PATH_FOLDER_REPOSITORI>\\bridge.py"
      ]
    }
  }
}
```

### B. OpenCode CLI
Jalankan perintah langsung di terminal:
```bash
opencode mcp add --global FigCraft -- python <PATH_FOLDER_REPOSITORI>/bridge.py
```

Atau edit file `~/.config/opencode/opencode.json`:
```json
{
  "mcp": {
    "FigCraft": {
      "type": "local",
      "command": [
        "python",
        "<PATH_FOLDER_REPOSITORI>\\bridge.py"
      ],
      "enabled": true
    }
  }
}
```

### C. Cursor IDE
Buka atau buat file:
- **Windows**: `%USERPROFILE%\.cursor\mcp.json`
- **macOS / Linux**: `~/.cursor/mcp.json`

Tambahkan entri `"FigCraft"`:
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": [
        "<PATH_FOLDER_REPOSITORI>\\bridge.py"
      ]
    }
  }
}
```
*(Atau melalui UI Cursor: Masuk ke **Settings** > **Cursor Settings** > **Features** > **MCP** > klik **Add New MCP Server**).*

### D. Claude Desktop
Buka file konfigurasi Claude Desktop:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Tambahkan entri:
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": [
        "<PATH_FOLDER_REPOSITORI>\\bridge.py"
      ]
    }
  }
}
```

---

## 5. Konfigurasi Shortcut FigCraft Desktop (Windows)

Agar setiap kali Anda membuka FigCraft secara manual dari menu Windows, FigCraft sudah siap mendengarkan perintah AI:

1. Buka folder shortcut: Tekan `Win + R`, ketik `shell:programs`, tekan Enter.
2. Cari shortcut **FigCraft**, klik kanan lalu pilih **Properties**.
3. Pada tab **Shortcut**, lihat kolom **Target**.
4. Tambahkan argumen `--control 1984` di ujung teks target:
   - Sebelum: `"C:\Program Files\ArtCraft\FigCraft\figcraft.exe"`
   - Sesudah: `"C:\Program Files\ArtCraft\FigCraft\figcraft.exe" --control 1984`
5. Klik **Apply** lalu **OK**.

*(Catatan: Script `install.py` sudah melakukan hal ini secara otomatis).*

---

## 6. Pengujian & Verifikasi Koneksi

Setelah instalasi selesai, uji jembatan dengan menjalankan:
```bash
python test_connection.py
```

**Indikator Keberhasilan:**
```
Testing FigCraft MCP Connection...
[1/3] Sending MCP Handshake...
  ✔ Connected to: FigCraft v0.18.1
[2/3] Querying MCP Tools...
  ✔ Total 19 tools available: list_commands, run_command, batch, create_node, set_properties...
[3/3] Drawing Test Element in FigCraft...
  ✔ Successfully created Test Badge on FigCraft canvas!

=== All Tests Passed! FigCraft MCP is 100% Ready! ===
```

Periksa jendela FigCraft Anda. Anda akan melihat sebuah badge hijau bertuliskan **"✦ FigCraft MCP Connected! ✦"** di kanvas!

---

## 7. Penyelesaian Masalah (Troubleshooting)

### Q: Muncul pesan `python is not recognized` di terminal Windows
- **Penyebab**: Python belum dimasukkan ke environment variable `PATH`.
- **Solusi**: Buka Windows Search > ketik *"Edit the system environment variables"* > Environment Variables > pilih `Path` > Tambahkan path folder Python Anda (misal `C:\Python312\` dan `C:\Python312\Scripts\`).

### Q: Muncul pesan `figcraft-cli executable not found`
- **Penyebab**: FigCraft terpasang di lokasi non-standar.
- **Solusi**: Tentukan lokasinya secara eksplisit menggunakan environment variable:
  ```bash
  # Di Windows PowerShell:
  $env:FIGCRAFT_CLI_PATH = "D:\CustomPath\FigCraft\figcraft-cli.exe"
  $env:FIGCRAFT_PATH = "D:\CustomPath\FigCraft\figcraft.exe"
  ```

### Q: Port 1984 bentrok dengan aplikasi lain
- **Solusi**: Anda dapat mengubah port dengan menyetel environment variable `FIGCRAFT_PORT`:
  ```bash
  # Mengubah ke port 2000
  $env:FIGCRAFT_PORT = "2000"
  ```
  Dan pastikan menjalankan FigCraft dengan `figcraft --control 2000`.

---

## 8. Referensi Tool MCP FigCraft

Ketika terhubung, AI Anda memiliki akses ke **19 tools native FigCraft**:

| Tool | Fungsi |
| :--- | :--- |
| `create_node` | Membuat elemen baru (frame, text, rectangle, vector, component, dsb.) |
| `set_properties` | Mengubah properti (warna/fill, cornerRadius, layout, padding, font, dsb.) |
| `batch` | Menjalankan beberapa perintah canvas sekaligus dalam satu langkah undo |
| `inspect_document` | Membaca struktur node dan hierarki layer pada canvas |
| `get_node` | Mengambil data detail suatu node spesifik berdasarkan ID |
| `screenshot` | Mengambil gambar hasil render visual canvas atau layer tertentu (PNG) |
| `export` | Mengekspor desain ke berbagai format (PNG, SVG, JPG, PDF) |
| `run_command` | Menjalankan command internal dari 400+ command registry FigCraft |
| `undo` / `redo` | Membatalkan atau mengulangi perubahan desain |
| `open_file` / `save_file` | Membuka atau menyimpan dokumen `.figcraft` |
| `select` | Mengubah elemen yang sedang dipilih di canvas |
| `pointer` / `key` / `type_text` | Mengirim interaksi input untuk prototipe atau pengujian UI |
