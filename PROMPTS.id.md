# Kumpulan Formula Prompt FigCraft

> Panduan formula prompt siap pakai untuk merancang UI di kanvas FigCraft dan mengekstrak desain menjadi kode frontend.

[Read in English](PROMPTS.md) | **Bahasa Indonesia**

---

## Daftar Isi
1. [Anatomi Formula Prompt yang Efektif](#1-anatomi-formula-prompt-yang-efektif)
2. [Kategori 1: Navigasi dan Menu](#2-kategori-1-navigasi-dan-menu)
3. [Kategori 2: Formulir dan Autentikasi](#3-kategori-2-formulir-dan-autentikasi)
4. [Kategori 3: Kartu Konten dan Media](#4-kategori-3-kartu-konten-dan-media)
5. [Kategori 4: Dashboard dan Statistik Data](#5-kategori-4-dashboard-dan-statistik-data)
6. [Kategori 5: Modal dan Dialog Interaktif](#6-kategori-5-modal-dan-dialog-interaktif)
7. [Kategori 6: Konversi Desain ke Kode (Design-to-Code)](#7-kategori-6-konversi-desain-ke-kode-design-to-code)
8. [Tips Praktis untuk Hasil Terbaik](#8-tips-praktis-untuk-hasil-terbaik)

---

## 1. Anatomi Formula Prompt yang Efektif

Agar asisten AI menggambar komponen antarmuka yang rapi, proporsional, dan mudah dikonversi ke kode, gunakan struktur perintah 5 bagian berikut:

```
[Peran] + [Nama Wadah & Ukuran] + [Struktur Layout] + [Gaya Visual & Warna] + [Detail Konten]
```

### Penjelasan Bagian Formula:
- **Peran**: Nyatakan bahwa AI bertindak sebagai desainer antarmuka ("Rancang di FigCraft...").
- **Nama Wadah & Ukuran**: Sebutkan nama frame dan estimasi dimensi (misalnya: "Frame kartu berukuran 380x480 piksel").
- **Struktur Layout**: Tentukan arah susunan elemen (vertikal flex-column atau horizontal flex-row) serta jarak antar elemen (`gap` dan `padding`).
- **Gaya Visual & Warna**: Cantumkan tema (gelap atau terang), radius sudut (`corner radius`), dan kode warna hex jika Anda memiliki preferensi.
- **Detail Konten**: Sebutkan teks judul, label tombol, ikon atau badge yang perlu ditampilkan.

---

## 2. Kategori 1: Navigasi dan Menu

### Formula A: Header / Top Navbar Desktop Modern
```
Rancang komponen Top Navbar desktop di FigCraft dengan spesifikasi:
- Wadah utama: Frame horizontal (flex-row), lebar 1200px, tinggi 72px, latar belakang gelap #0F172A, padding horizontal 32px, penjajaran tengah (align-items center), justify-between.
- Bagian kiri: Teks logo 'AcmeFlow' berukuran 20px tebal (font-bold) warna putih #FFFFFF.
- Bagian tengah: Menu navigasi berisi 4 tautan teks horizontal (Produk, Solusi, Harga, Dokumentasi) ukuran 14px warna abu-abu #94A3B8 dengan jarak antar menu (gap) 28px.
- Bagian kanan: Tombol aksi utama 'Mulai Gratis' dengan warna latar indigo #6366F1, teks putih 14px, radius sudut 8px, padding 10px 20px.
```

### Formula B: Bottom Navigation Bar Aplikasi Mobile
```
Buat komponen Bottom Navigation Bar mobile di FigCraft:
- Wadah: Frame horizontal lebar 375px, tinggi 64px, warna latar #1E293B, border atas 1px warna #334155.
- Item: Buat 4 menu navigasi berjarak seimbang (Home, Eksplorasi, Notifikasi, Profil).
- Status aktif: Menu 'Home' memiliki teks warna biru #38BDF8 dan indikator titik kecil di bawahnya. Tiga menu lainnya menggunakan teks warna abu-abu #64748B.
```

---

## 3. Kategori 2: Formulir dan Autentikasi

### Formula A: Kartu Login Mode Gelap
```
Rancang komponen Kartu Login mode gelap di FigCraft:
- Wadah utama: Frame vertikal (flex-col), lebar 400px, padding 32px, radius sudut 16px, latar belakang #18181B, border halus 1px #27272A.
- Header: Teks judul 'Masuk ke Akun Anda' ukuran 22px tebal warna putih, dan subjudul 'Masukkan email dan kata sandi Anda' ukuran 14px abu-abu #A1A1AA, gap 8px.
- Input Email: Label teks 'Alamat Email' ukuran 12px, diikuti kotak input (frame tinggi 44px, latar #27272A, radius 8px, padding horizontal 14px, teks placeholder 'nama@perusahaan.com' warna #71717A).
- Input Password: Label teks 'Kata Sandi' ukuran 12px, diikuti kotak input serupa dengan teks placeholder '••••••••'.
- Tautan: Teks kecil 'Lupa kata sandi?' ukuran 12px rata kanan warna #818CF8.
- Tombol Masuk: Frame tombol penuh (lebar 336px, tinggi 44px), latar biru indigo #4F46E5, radius 8px, teks putih 'Masuk Sekarang' berukuran 14px tebal rata tengah.
- Jarak antar blok input: gap 16px.
```

### Formula B: Formulir Registrasi dengan Status Validasi
```
Buat kartu formulir registrasi akun di FigCraft dengan wadah vertikal lebar 420px:
- Judul formulir: 'Buat Akun Baru' warna #0F172A pada latar kartu putih #FFFFFF.
- Input Nama Lengkap, Input Email, dan Input Kata Sandi.
- Tambahkan status validasi visual pada input kata sandi: indikator teks berwarna hijau #16A34A bertuliskan 'Kekuatan kata sandi: Kuat'.
- Tombol persetujuan syarat ketentuan (checkbox) dan tombol aksi 'Daftar Akun' warna hijau emerald #059669.
```

---

## 4. Kategori 3: Kartu Konten dan Media

### Formula A: Kartu Produk E-Commerce Modern
```
Rancang kartu produk e-commerce sneaker di FigCraft:
- Wadah kartu: Frame vertikal lebar 320px, radius 16px, latar belakang #18181B, padding 16px, gap 14px.
- Area Gambar: Frame placeholder gambar sneaker tinggi 200px warna #27272A, radius 12px, dengan badge diskon 'SALE 30%' warna merah #EF4444 di sudut kiri atas.
- Informasi Produk:
  - Teks kategori: 'SEPATU LARI PRIA' ukuran 11px warna abu-abu #71717A.
  - Teks judul produk: 'AeroGlide Pro Runner V2' ukuran 16px tebal warna putih #F4F4F5.
- Pilihan Ukuran: Baris tombol ukuran horizontal (flex-row, gap 8px) berisi kotak ukuran 40, 41, 42, 43, 44. Kotak ukuran 42 dalam kondisi terpilih (latar putih, teks hitam).
- Baris Harga dan Aksi:
  - Harga saat ini 'Rp 1.499.000' ukuran 18px tebal warna putih, dan harga coret 'Rp 2.199.000' ukuran 12px warna abu-abu.
  - Tombol aksi 'Beli' warna indigo #6366F1 dengan padding 8px 16px dan radius 8px.
```

### Formula B: Kartu Pemutar Musik Mini
```
Rancang komponen pemutar musik kompak di FigCraft:
- Wadah: Frame vertikal lebar 340px, latar #111827, radius 18px, padding 20px, gap 16px.
- Sampul Album: Frame gambar bujur sangkar 300x300px warna #1F2937 dengan radius 12px.
- Baris Judul Lagu: Teks 'Midnight Echoes' ukuran 18px tebal warna putih, dan nama artis 'Lunar Drift' ukuran 14px warna #9CA3AF.
- Bilah Durasi (Progress Bar): Garis latar abu-abu #374151 tinggi 4px lebar 300px, dengan garis progres aktif warna biru langit #38BDF8 sepanjang 180px. Teks durasi '2:15' di kiri dan '3:45' di kanan ukuran 11px.
- Tombol Kendali: Baris horizontal rata tengah berisi tombol Previous, tombol Play/Pause besar (lingkaran 48px latar putih dengan ikon gelap), dan tombol Next.
```

### Formula C: Kartu Paket Harga (Pricing Card)
```
Buat kartu paket harga langganan 'Paket Pro' di FigCraft:
- Wadah: Lebar 360px, padding 32px, radius 20px, warna latar #0F172A, border 2px #6366F1.
- Badge terpopuler di bagian atas: 'PILIHAN TERBAIK' latar #6366F1 warna teks putih ukuran 10px tebal.
- Nominal harga: Teks 'Rp 299.000' ukuran 36px tebal warna putih, diikuti teks '/bulan' ukuran 14px abu-abu.
- Daftar fitur: 5 baris daftar fitur dengan tanda centang (Dukungan 24/7, Ekspor Desain Tak Terbatas, Kolaborasi Tim, Akses API Penuh, Penyimpanan Cloud).
- Tombol aksi: 'Pilih Paket Pro' lebar penuh warna #6366F1 dengan teks putih 14px.
```

---

## 5. Kategori 4: Dashboard dan Statistik Data

### Formula A: Kartu Pertumbuhan Pendapatan (Revenue Card)
```
Rancang kartu metrik pendapatan analitik di FigCraft:
- Wadah: Frame vertikal lebar 280px, padding 20px, radius 14px, latar #1E293B, border 1px #334155, gap 12px.
- Baris Header: Teks judul 'Total Pendapatan' ukuran 13px warna #94A3B8, dan badge persentase hijau '+18.4%' (latar #064E3B, teks hijau #34D399, radius 6px, padding 4px 8px, ukuran 11px).
- Angka Utama: Teks nilai 'Rp 148.520.000' ukuran 26px tebal warna putih #F8FAFC.
- Keterangan Bawah: Teks pembanding 'Dibandingkan bulan lalu (Rp 125.400.000)' ukuran 12px warna #64748B.
```

### Formula B: Baris Tiga Metrik Dashboard (3-Column Stats Row)
```
Buat susunan 3 kartu ringkasan metrik dashboard secara horizontal di FigCraft:
- Wadah induk: Frame horizontal (flex-row, gap 16px).
- Kartu 1: 'Pengguna Aktif' bernilai '24.810' dengan tren '+12%'.
- Kartu 2: 'Tingkat Konversi' bernilai '3.42%' dengan tren '+0.8%'.
- Kartu 3: 'Waktu Respons Rata-rata' bernilai '142ms' dengan tren '-15ms (lebih cepat)'.
- Setiap kartu berukuran lebar 220px, latar gelap #1E293B, dan radius 12px.
```

---

## 6. Kategori 5: Modal dan Dialog Interaktif

### Formula A: Dialog Konfirmasi Penghapusan
```
Rancang modal dialog konfirmasi penghapusan di FigCraft:
- Wadah modal: Frame vertikal lebar 440px, padding 28px, radius 16px, latar #FFFFFF (atau gelap #18181B), gap 18px.
- Ikon Peringatan: Kotak atau lingkaran 48px warna latar merah muda #FEE2E2 dengan simbol peringatan merah #DC2626.
- Teks Konfirmasi: Judul 'Hapus Proyek Ini?' ukuran 18px tebal, dan teks deskripsi 'Tindakan ini tidak dapat dibatalkan. Seluruh data dan riwayat kanvas akan dihapus secara permanen.' ukuran 14px warna abu-abu.
- Baris Tombol Aksi: Frame horizontal (justify-end, gap 12px) berisi tombol 'Batal' (border abu-abu, teks gelap) dan tombol 'Ya, Hapus' (latar merah #DC2626, teks putih).
```

---

## 7. Kategori 6: Konversi Desain ke Kode (Design-to-Code)

Setelah komponen antarmuka terbentuk di kanvas FigCraft, gunakan formula prompt berikut untuk mengubahnya menjadi kode pemrograman frontend.

### Formula A: Konversi Elemen ke Komponen React Tailwind CSS
```
Periksa elemen kartu yang sedang aktif di kanvas FigCraft. Ekstrak struktur hierarki layout, warna hex, radius, jarak padding, dan tipografinya, kemudian buatkan komponen React fungsional TypeScript mandiri dengan Tailwind CSS yang responsif.
```

### Formula B: Konversi Elemen ke Widget Flutter
```
Baca frame komponen yang dipilih di FigCraft. Terjemahkan susunan container, flex column, flex row, border radius, dan warnanya menjadi kode widget Flutter (StatelessWidget) yang bersih dan terstruktur.
```

### Formula C: Ekstrak Token Desain ke tailwind.config.js
```
Analisis seluruh palet warna dan ukuran tipografi yang digunakan pada halaman kanvas FigCraft ini. Buatkan objek konfigurasi theme.extend untuk file tailwind.config.js yang merangkum token warna latar belakang, warna teks, dan border radius tersebut.
```

---

## 8. Tips Praktis untuk Hasil Terbaik

1. **Gunakan Nama Frame yang Jelas**: Minta AI memberi nama frame yang semantik seperti `Navbar`, `LoginCard`, atau `PricingCard` agar pohon layer di FigCraft mudah dikelola.
2. **Spesifikasikan Mode Layout**: Selalu sebutkan apakah susunan elemen bersifat vertikal (`flex-col`) atau horizontal (`flex-row`).
3. **Cantumkan Kode Warna Hex**: Jika Anda memiliki pedoman merek (brand guideline), berikan kode hex langsung (contoh: `#4F46E5` untuk indigo, `#0F172A` untuk slate).
4. **Hindari Perintah Terlalu Singkat**: Perintah seperti "buatkan tombol bagus" akan menghasilkan elemen default generik. Perintah seperti "buat tombol aksi utama lebar penuh, tinggi 44px, latar biru indigo, radius 8px, teks putih rata tengah" akan menghasilkan desain yang presisi.
