# Hiaskan — Sistem Pembibitan Ikan Hias & Penjualan

Hiaskan adalah aplikasi web untuk mengelola pembibitan, pemeliharaan, dan penjualan ikan hias. Dibangun dengan **Python** dan **Streamlit**, aplikasi ini dibuat untuk menjadi teman sehari-hari peternak ikan: mencatat stok, memantau kualitas air, mencatat pemijahan, sampai memproses penjualan, semuanya dari satu tempat, tanpa ribet.

Salah satu pilihan desain utamanya: **tanpa database**. Semua data disimpan sebagai file JSON/CSV di folder `data/`, jadi aplikasinya ringan, mudah dibawa-bawa, dan transparan, kamu bisa membuka datanya langsung dengan notepad atau Excel kapan saja.

---

## Kebutuhan

Aplikasi ini cukup ringan, hampir semua komputer bisa menjalankannya:

- **Python 3.11 atau lebih baru**

## Instalasi

1. Ambil kode aplikasinya clone dari repository (`git clone https://github.com/DarulQutni-Q/Hiaskan.git`) atau ekstrak file zip.
2. Buat virtual environment biar bersih dari environment global: # OPTIONAL
   ```bash
   cd Hiaskan
   python -m venv .venv
   ```
   Aktifkan sesuai sistemmu:
   - Windows (PowerShell): `.venv\Scripts\activate.ps1` atau `.bat` kalau pakai CMD
   - Linux/macOS: `source .venv/bin/activate`
   - fish shell: `source .venv/bin/activate.fish`

   Catatan kecil: di Windows mengaktifkan environment tidak wajib, tapi di Linux sebaiknya dilakukan (keamanan kernel mengunci instalasi paket global, kecuali kamu menggunakan pipx).
3. Pasang semua dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Cara Menjalankan

```bash
# Jalankan aplikasi (browser akan terbuka otomatis di http://localhost:8501)
streamlit run app.py

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
Proyek akademik — dibuat untuk memenuhi tugas mata kuliah Pemograman Beriontasi Objek.
