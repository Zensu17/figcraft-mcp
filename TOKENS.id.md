# Panduan Token Desain dan Generator Kanvas FigCraft

> Pustaka token desain standar dan alat bantu otomatis untuk menggambar palet warna, tombol, dan lencana status langsung di kanvas FigCraft.

[Read in English](TOKENS.md) | **Bahasa Indonesia**

---

## Daftar Isi
1. [Gambaran Umum](#1-gambaran-umum)
2. [Tabel Skala Token Desain](#2-tabel-skala-token-desain)
3. [Penggunaan Melalui Baris Perintah (CLI)](#3-penggunaan-melalui-baris-perintah-cli)
4. [Penggunaan Modul Python di Skrip Anda](#4-penggunaan-modul-python-di-skrip-anda)
5. [Ekspor Konfigurasi ke Tailwind CSS](#5-ekspor-konfigurasi-ke-tailwind-css)

---

## 1. Gambaran Umum

Untuk menjaga konsistensi antarmuka pengguna, proyek ini dilengkapi dengan **FigCraft Design Tokens** yang tersimpan di berkas `tokens.json`.

Dengan token ini, komponen antarmuka yang digambar oleh asisten AI maupun pengembang selalu mengikuti standar industri (seperti palet warna Tailwind CSS dan skala spasi 4px) tanpa ukuran acak atau warna yang tidak konsisten.

---

## 2. Tabel Skala Token Desain

### A. Palet Warna Standar (Shades 50 hingga 950)
Tersedia 7 tema warna utama yang mencakup spektrum lengkap:
- **`slate`**: Abu-abu kebiruan netral (`#F8FAFC` hingga `#020617`).
- **`zinc`**: Abu-abu monokrom netral (`#FAFAFA` hingga `#09090B`).
- **`indigo`**: Aksen utama modern (`#EEF2FF` hingga `#1E1B4B`).
- **`sky`**: Biru cerah untuk informasi atau status aktif (`#F0F9FF` hingga `#082F49`).
- **`emerald`**: Hijau untuk status sukses dan konfirmasi positif (`#ECFDF5` hingga `#022C22`).
- **`amber`**: Kuning oranye untuk status peringatan atau pending (`#FFFBEB` hingga `#451A03`).
- **`rose`**: Merah muda dan merah tua untuk status bahaya atau error (`#FFF1F2` hingga `#4C0519`).

### B. Skala Jarak dan Padding (Spacing)
Menggunakan kelipatan basis 4 piksel:
- `1`: 4px
- `2`: 8px
- `3`: 12px
- `4`: 16px
- `5`: 20px
- `6`: 24px
- `8`: 32px
- `10`: 40px
- `12`: 48px
- `16`: 64px

### C. Skala Radius Sudut (Border Radius)
- `none`: 0px
- `sm`: 2px
- `default`: 4px
- `md`: 6px
- `lg`: 8px
- `xl`: 12px
- `2xl`: 16px
- `3xl`: 24px
- `full`: 9999px (lingkaran penuh / kapsul)

---

## 3. Penggunaan Melalui Baris Perintah (CLI)

Modul `tokens.py` dapat dijalankan secara langsung dari terminal untuk menggambar fondasi desain di atas kanvas FigCraft yang sedang terbuka:

```bash
# 1. Menampilkan ringkasan token yang tersedia
python tokens.py --list

# 2. Menggambar kartu swatch palet warna di kanvas FigCraft (misal: indigo, slate, sky, emerald)
python tokens.py --palette indigo

# 3. Menggambar pustaka tombol komponen standar (Primary, Secondary, Outline, Danger)
python tokens.py --starter-buttons

# 4. Menggambar lencana status standar (Success, Warning, Danger, Info)
python tokens.py --starter-badges

# 5. Menampilkan cuplikan konfigurasi theme.extend untuk tailwind.config.js
python tokens.py --export-tailwind
```

---

## 4. Penggunaan Modul Python di Skrip Anda

Anda juga dapat mengimpor `tokens.py` ke dalam skrip Python buatan Anda sendiri:

```python
from tokens import get_color, get_spacing, get_radius

# Mengambil warna hex
primary_color = get_color("indigo-600")   # Mengembalikan '#4F46E5'
bg_dark = get_color("slate-900")          # Mengembalikan '#0F172A'

# Mengambil nilai spasi dan radius sudut
card_padding = get_spacing(4)             # Mengembalikan 16
button_radius = get_radius("lg")          # Mengembalikan 8
```

---

## 5. Ekspor Konfigurasi ke Tailwind CSS

Untuk menyelaraskan proyek frontend web Anda dengan kanvas FigCraft, jalankan perintah:
```bash
python tokens.py --export-tailwind
```

Salin hasil keluaran JSON tersebut ke dalam properti `theme.extend` pada berkas `tailwind.config.js` di proyek frontend Anda.
