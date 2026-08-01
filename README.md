# Hiaskan — Sistem Pembibitan Ikan Hias & Penjualan

Hiaskan adalah aplikasi web untuk mengelola pembibitan, pemeliharaan, dan penjualan ikan hias. Dibangun dengan **Python** dan **Streamlit**, aplikasi ini dibuat untuk menjadi teman sehari-hari peternak ikan: mencatat stok, memantau kualitas air, mencatat pemijahan, sampai memproses penjualan — semuanya dari satu tempat, tanpa ribet.

Salah satu pilihan desain utamanya: **tanpa database**. Semua data disimpan sebagai file JSON/CSV di folder `data/`, jadi aplikasinya ringan, mudah dibawa-bawa, dan transparan — kamu bisa membuka datanya langsung dengan notepad atau Excel kapan saja.

---

## Kebutuhan

Aplikasi ini cukup ringan — hampir semua komputer bisa menjalankannya:

- **Python 3.11 atau lebih baru**
- Windows, macOS, atau Linux
- RAM minimal 512 MB dan disk kosong sekitar 100 MB

## Instalasi

1. Ambil kode aplikasinya — clone dari repository atau ekstrak file zip yang diberikan.
2. Buat virtual environment biar bersih dari environment global:
   ```bash
   cd Hiaskan
   python -m venv .venv
   ```
   Aktifkan sesuai sistemmu:
   - Windows (PowerShell): `.venv\Scripts\activate.ps1` — atau `.bat` kalau pakai CMD
   - Linux/macOS: `source .venv/bin/activate`
   - fish shell: `source .venv/bin/activate.fish`

   Catatan kecil: di Windows mengaktifkan environment tidak wajib, tapi di Linux sebaiknya dilakukan (keamanan kernel mengunci instalasi paket global, kecuali kamu menggunakan pipx).
3. Pasang semua dependensi:
   ```bash
   pip install -r requirements.txt
   ```
Aplikasi desktop berbasis **Python 3.11+** dan **PyQt6** untuk mengelola pembibitan, pemeliharaan, dan penjualan ikan hias.

---

## Kebutuhan Sistem

| Kebutuhan |         Versi           |
|-----------|-------------------------|
| Python    | 3.11 atau lebih baru    |
| OS        | Windows / macOS / Linux |
| RAM       | Minimal 512 MB          |
| Disk      | Minimal 100 MB          |

## Instalasi

```bash
# 1. Clone repository
git clone https://github.com/DarulQutni-Q/Hiaskan.git #Atau extract file.zip nya
cd Hiaskan

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan virtual environment (optional)
# Linux / macOS:
zsh/bash = source .venv/bin/activate
fish shell = source .venv/bin/activate.fish
# Windows:
.venv\Scripts\activate.ps1 #kalo pakai powershell, kalo cmd activate.bat
# Biasanya di windows tidak wajib untuk mengaktifkan environment, di linux wajib karna keamanan kernel (kecuali install requirement pakai pipx)

# 4. Install dependencies
pip install -r requirements.txt
```

## Cara Menjalankan

```bash
# Jalankan aplikasi (browser akan terbuka otomatis di http://localhost:8501)
streamlit run app.py
# Jalankan aplikasi GUI
python main.py

# Jalankan unit tests
python -m pytest tests/ -v
```

Satu hal yang penting diingat: **jangan** jalankan dengan `python app.py`. Aplikasi ini memang dirancang hanya berjalan lewat perintah `streamlit run` — kalau dipanggil langsung, muncul pesan peringatan untuk memakai cara yang benar.

## Struktur Folder

```
Hiaskan/
├── app.py                  # Entry point aplikasi (dijalankan dengan streamlit run)
├── requirements.txt        # Daftar dependensi
├── .streamlit/config.toml  # Tema minimalis (aksen teal, light)
├── data/                   # Data persisten — semua tersimpan di sini
│   ├── ikan.json           # Data stok ikan hias
│   ├── kolam.json          # Data kolam + kualitas air
│   ├── pakan.json          # Data pakan
│   ├── pelanggan.json      # Data pelanggan
│   ├── pemijahan.json      # Data pemijahan
│   └── penjualan.csv       # Riwayat penjualan
├── laporan/                # Laporan hasil generate tersimpan di sini
├── ui/                     # Layer tampilan Streamlit
│   ├── components.py       # Helper bersama: palet warna, CSS, kartu KPI
│   ├── dashboard.py        # Ringkasan: KPI, grafik, peringatan otomatis
│   ├── ikan.py             # Kelola stok ikan + preview harga
│   ├── kolam.py            # Kelola kolam + kualitas air
│   ├── pakan.py            # Kelola pakan + pemakaian stok
│   ├── pemijahan.py        # Catat proses pemijahan
│   ├── penjualan.py        # Keranjang penjualan interaktif
│   ├── pelanggan.py        # Kelola data pelanggan
│   └── laporan.py          # Generate + unduh laporan
├── models/                 # Model domain (berpola OOP)
│   ├── ikan.py             # IkanHias, Cupang, Guppy, Koi
│   ├── kolam.py            # Kolam, KualitasAir
│   ├── pemijahan.py        # Pemijahan
│   ├── pakan.py            # Pakan
│   ├── pelanggan.py        # Pelanggan
│   └── penjualan.py        # Penjualan, ItemPenjualan
├── strategies/             # Strategy Pattern untuk harga
│   └── harga_strategy.py   # HargaStrategy + implementasi per jenis ikan
├── exceptions/             # Exception khusus aplikasi
│   └── custom_errors.py    # Misalnya StokIkanTidakCukupError
├── services/               # Lapisan logika bisnis
│   ├── file_handler.py     # CRUD JSON/CSV + export laporan
│   ├── stok_service.py     # Manajemen stok ikan
│   ├── kolam_service.py    # Validasi kualitas air
│   ├── penjualan_service.py# Proses transaksi penjualan
│   └── laporan_service.py  # Generate laporan
└── tests/                  # Unit tests
    └── test_hiaskan.py     # 14 test case
```

## Bagaimana Data Selalu Sinkron?

Kuncinya sederhana: setiap kali kamu berinteraksi dengan aplikasi, halaman membaca dan menulis file yang sama di folder `data/` lewat `services/file_handler.py`. Karena tidak ada penyimpanan perantara, tampilan tidak mungkin ketinggalan zaman. Contoh nyatanya:

- **Jual ikan** → stok langsung berkurang di data ikan, statistik pelanggan ikut ter-update
- **Tambah/mutasi stok ikan** → jumlah ikan di kolam ter-sync otomatis (`_sync_kolam`)
- **Buka dashboard** → semua angka dan grafik langsung mencerminkan data terbaru

## Fitur Utama

**Dashboard** — sepintas lihat kondisi seluruh operasional: total ikan, stok sehat, kolam aktif, pendapatan, dan jumlah transaksi. Ada grafik stok per jenis, pendapatan per jenis, tren penjualan, dan komposisi status kesehatan. Aplikasi juga proaktif mengingatkan: kualitas air yang buruk, stok menipis, pakan mendekati kadaluarsa, dan kepadatan kolam yang perlu perhatian.

**Manajemen Ikan** — catat ikan (Cupang, Guppy, Koi) lengkap dengan varietas, warna, ukuran, umur, grade, dan status kesehatan. Harga jual dihitung otomatis dari semua faktor itu, dan kamu bisa melihat preview harga saat masih mengisi form.

**Manajemen Kolam** — kelola kolam dan pantau kualitas air (pH, suhu, oksigen, amonia). Ada alert otomatis jika salah satu parameter keluar dari batas aman.

**Pemijahan** — catat setiap sesi pemijahan: indukan yang dipakai, jumlah telur, yang menetas, hingga larva yang bertahan. Aplikasi menghitung tingkat penetasan dan kelangsungan hidupnya.

**Penjualan** — buat transaksi lewat keranjang interaktif; ubah jumlah langsung di tabel. Stok divalidasi otomatis dan ikan yang berstatus sakit/karantina/mati tidak bisa dijual. Riwayat transaksi tersimpan di CSV.

**Pakan** — kelola persediaan pakan, kurangi stok saat dipakai, dan aplikasi mengingatkan kalau ada pakan yang mendekati atau sudah lewat tanggal kadaluarsa.

**Pelanggan** — simpan data pembeli lengkap dengan ringkasan total transaksi dan total pembeliannya.

**Laporan** — generate 5 jenis laporan (stok, pendapatan, mortalitas, pakan, pertumbuhan) dalam format CSV/TXT. Bisa dipratinjau di layar, diunduh, dan file-nya tersimpan otomatis di folder `laporan/`.

## Desain yang Dipakai

Tampilan dibuat minimalis: aksen teal untuk air, latar terang hangat, judul memakai font Plus Jakarta Sans, dan kartu-kartu KPI yang bersih. Grafiknya sengaja dibuat statis — tidak bisa di-zoom atau di-crop secara tak sengaja, jadi informasinya selalu terlihat utuh.

## Konsep OOP yang Diterapkan

| Konsep | Implementasi |
|---|---|
| **Inheritance** | `IkanHias` → `Cupang`, `Guppy`, `Koi` |
| **Polymorphism** | `hitung_harga_jual()` di-override tiap subclass |
| **Encapsulation** | `__jumlah_stok`, `__status_kesehatan` dengan property |
| **Exception Handling** | `KualitasAirBurukError`, `StokIkanTidakCukupError` |
| **File Handling** | `ikan.json`, `kolam.json`, `penjualan.csv` |

## Strategy Pattern untuk Harga

Harga ikan dihitung lewat Strategy Pattern: `HargaStrategy` sebagai kontrak umum, lalu `CupangHargaStrategy`, `GuppyHargaStrategy`, dan `KoiHargaStrategy` sebagai implementasinya. Strategi bisa diganti di runtime tanpa mengubah kode yang sudah ada — itulah yang namanya Open/Closed Principle.

## Menambah Jenis Ikan Baru (OCP)

Tidak perlu menyentuh service, file handler, atau UI yang sudah ada. Cukup tiga langkah:

1. Buat class baru, misalnya `Arwana(IkanHias)` di `models/ikan.py`
2. Buat `ArwanaHargaStrategy(HargaStrategy)` di `strategies/harga_strategy.py`
3. Selesai — sisanya mengikuti pola yang sudah ada.

## Skenario Demo

Ada beberapa skenario yang bisa dicoba untuk melihat cara aplikasi menangani situasi berbeda:

- **Normal**: jual 3 Cupang Halfmoon ke pelanggan Ahmad Fauzi — stok berkurang otomatis, transaksi tercatat, statistik pelanggan ter-update.
- **Error 1 — kualitas air buruk**: periksa Kolam Karantina (K004) yang pH-nya 4.5; aplikasi memicu `KualitasAirBurukError`.
- **Error 2 — stok tidak cukup**: coba jual 100 Cupang padahal stok hanya 15; `StokIkanTidakCukupError` muncul dengan pesan yang jelas.
- **Error 3 — file rusak**: jika file JSON tidak valid, `FileOperasiError` ditampilkan secara informatif tanpa membuat aplikasi crash.

## Unit Tests

Ada 14 test yang mencakup 6 kategori:

```
TestInheritance      — 2 test (isinstance, jenis())
TestPolymorphism     — 2 test (harga berbeda, override bonus)
TestEncapsulation    — 2 test (stok negatif, status invalid)
TestCustomException  — 2 test (air buruk, stok kurang)
TestStrategyPattern  — 2 test (swap strategy, default strategy)
TestFileHandling     — 4 test (JSON CRUD, CSV, corrupt, factory)
```

Jalankan dengan `python -m pytest tests/ -v`.

---
├── main.py                  # Entry point utama
├── requirements.txt         # Dependencies
├── data/                    # Data persisten (JSON/CSV)
│   ├── ikan.json            # Data stok ikan hias
│   ├── kolam.json           # Data kolam + kualitas air
│   ├── pakan.json           # Data pakan
│   ├── pelanggan.json       # Data pelanggan
│   ├── pemijahan.json       # Data pemijahan
│   └── penjualan.csv        # Riwayat penjualan
├── laporan/                 # Laporan yang di-generate
├── models/                  # Domain models (OOP)
│   ├── ikan.py              # IkanHias, Cupang, Guppy, Koi
│   ├── kolam.py             # Kolam, KualitasAir
│   ├── pemijahan.py         # Pemijahan
│   ├── pakan.py             # Pakan
│   ├── pelanggan.py         # Pelanggan
│   └── penjualan.py         # Penjualan, ItemPenjualan
├── strategies/              # Strategy Pattern
│   └── harga_strategy.py    # HargaStrategy + 3 concrete
├── exceptions/              # Custom Exceptions
│   └── custom_errors.py     # 4 custom exception classes
├── services/                # Business Logic Layer
│   ├── file_handler.py      # CRUD JSON/CSV, export laporan
│   ├── stok_service.py      # Manajemen stok
│   ├── kolam_service.py     # Validasi kualitas air
│   ├── penjualan_service.py # Proses penjualan
│   └── laporan_service.py   # Generate laporan
├── gui/                     # GUI PyQt6
│   ├── main_window.py       # Main window + 8 tab
│   ├── dialogs.py           # Dialog forms
│   └── styles.py            # Stylesheet minimalis
├── tests/                   # Unit Tests
    └── test_hiaskan.py      # 14 test cases

```

## Data Contoh

Aplikasi menyertakan data contoh yang siap digunakan:

| Data          |                                Isi                                   |
|---------------|----------------------------------------------------------------------|
| **Ikan**      | 9 record (3 Cupang, 3 Guppy, 3 Koi) dengan berbagai grade dan status |
| **Kolam**     | 4 kolam (termasuk 1 kolam karantina dengan kualitas air buruk)       |
| **Pakan**     | 4 jenis pakan (pelet, artemia, cacing, spirulina)                    |
| **Pelanggan** | 3 pelanggan dengan riwayat transaksi                                 |
| **Penjualan** | 3 transaksi contoh                                                   |
| **Pemijahan** | 3 catatan pemijahan (2 selesai, 1 berlangsung)                       |

## Fitur Utama

### 1. Manajemen Ikan Hias
- CRUD data ikan (Cupang, Guppy, Koi)
- Penghitungan harga otomatis berdasarkan jenis, ukuran, warna, umur, dan grade
- Tracking status kesehatan (sehat/sakit/karantina/mati)

### 2. Manajemen Kolam
- CRUD data kolam pemeliharaan
- Validasi kualitas air (pH, suhu, oksigen, amonia)
- Alert otomatis jika parameter air di luar batas aman

### 3. Pemijahan
- Pencatatan proses pemijahan (indukan, telur, penetasan)
- Tracking tingkat penetasan dan kelangsungan hidup larva

### 4. Penjualan
- Proses penjualan dengan validasi stok otomatis
- Pencegahan penjualan ikan berstatus sakit/karantina/mati
- Riwayat transaksi tersimpan di CSV

### 5. Laporan
- Laporan Stok (CSV)
- Laporan Pendapatan (TXT)
- Laporan Mortalitas (CSV)
- Laporan Pakan (CSV)
- Laporan Pertumbuhan/Pemijahan (CSV)

## Konsep OOP yang Diterapkan

|         Konsep         |                     Implementasi                      |
|------------------------|-------------------------------------------------------|
| **Inheritance**        | `IkanHias` → `Cupang`, `Guppy`, `Koi`                 |
| **Polymorphism**       | `hitung_harga_jual()` di-override tiap subclass       |
| **Encapsulation**      | `__jumlah_stok`, `__status_kesehatan` dengan property |
| **Exception Handling** | `KualitasAirBurukError`, `StokIkanTidakCukupError`    |
| **File Handling**      | `ikan.json`, `kolam.json`, `penjualan.csv`            |

## Pola Desain: Strategy Pattern

Penghitungan harga menggunakan Strategy Pattern:
- `HargaStrategy` (ABC) — interface strategi
- `CupangHargaStrategy` — formula harga Cupang
- `GuppyHargaStrategy` — formula harga Guppy  
- `KoiHargaStrategy` — formula harga Koi

Strategy bisa diganti runtime tanpa mengubah kode existing (Open/Closed Principle).

## Prinsip SOLID: Open/Closed Principle (OCP)

Menambah jenis ikan baru (misalnya Arwana) cukup:
1. Buat class `Arwana(IkanHias)`
2. Buat class `ArwanaHargaStrategy(HargaStrategy)`
3. Tidak perlu mengubah service, file handler, atau GUI yang sudah ada.

## Skenario Demo

### Skenario Normal
Penjualan 3 Cupang Halfmoon ke pelanggan Ahmad Fauzi — stok berkurang otomatis, transaksi tercatat di CSV.

### Skenario Error 1: Kualitas Air Buruk
Cek kualitas air Kolam Karantina (K004) — pH=4.5 memicu `KualitasAirBurukError`.

### Skenario Error 2: Stok Tidak Cukup
Coba jual 100 Cupang saat stok hanya 15 — memicu `StokIkanTidakCukupError`.

### Skenario Error 3: File Corrupt
File JSON rusak (format tidak valid) — memicu `FileOperasiError` dengan pesan informatif.

## Unit Tests

```
14 tests, 6 kategori:
  TestInheritance          — 2 test (isinstance, jenis())
  TestPolymorphism         — 2 test (harga berbeda, override bonus)
  TestEncapsulation        — 2 test (stok negatif, status invalid)
  TestCustomException      — 2 test (air buruk, stok kurang)
  TestStrategyPattern      — 2 test (swap strategy, default strategy)
  TestFileHandling         — 4 test (JSON CRUD, CSV, corrupt, factory)
```


Proyek akademik — dibuat untuk memenuhi tugas mata kuliah.
