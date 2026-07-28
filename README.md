# Hiaskan — Sistem Pembibitan Ikan Hias & Penjualan

Aplikasi desktop berbasis **Python 3.11+** dan **PyQt6** untuk mengelola pembibitan, pemeliharaan, dan penjualan ikan hias.

---

## Kebutuhan Sistem

| Kebutuhan | Versi |
|-----------|-------|
| Python | 3.11 atau lebih baru |
| OS | Windows / macOS / Linux |
| RAM | Minimal 512 MB |
| Disk | Minimal 100 MB |

## Instalasi

```bash
# 1. Clone repository
git clone https://github.com/DarulQutni-Q/Hiaskan.git
cd Hiaskan

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan virtual environment
# Linux / macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

## Cara Menjalankan

```bash
# Jalankan aplikasi GUI
python main.py

# Jalankan unit tests
python -m pytest tests/ -v
```

## Struktur Folder

```
Hiaskan/
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
│   └── test_hiaskan.py      # 14 test cases
└── docs/
    └── uml_class_diagram.md # UML Class Diagram (Mermaid)
```

## Data Contoh

Aplikasi menyertakan data contoh yang siap digunakan:

| Data | Isi |
|------|-----|
| **Ikan** | 9 record (3 Cupang, 3 Guppy, 3 Koi) dengan berbagai grade dan status |
| **Kolam** | 4 kolam (termasuk 1 kolam karantina dengan kualitas air buruk) |
| **Pakan** | 4 jenis pakan (pelet, artemia, cacing, spirulina) |
| **Pelanggan** | 3 pelanggan dengan riwayat transaksi |
| **Penjualan** | 3 transaksi contoh |
| **Pemijahan** | 3 catatan pemijahan (2 selesai, 1 berlangsung) |

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

| Konsep | Implementasi |
|--------|-------------|
| **Inheritance** | `IkanHias` → `Cupang`, `Guppy`, `Koi` |
| **Polymorphism** | `hitung_harga_jual()` di-override tiap subclass |
| **Encapsulation** | `__jumlah_stok`, `__status_kesehatan` dengan property |
| **Exception Handling** | `KualitasAirBurukError`, `StokIkanTidakCukupError` |
| **File Handling** | `ikan.json`, `kolam.json`, `penjualan.csv` |

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

## Lisensi

Proyek akademik — dibuat untuk memenuhi tugas mata kuliah.
