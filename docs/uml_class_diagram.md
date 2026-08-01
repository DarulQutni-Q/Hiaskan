# UML Class Diagram — Hiaskan

```mermaid
classDiagram
    direction TB

    %% ═══════════ EXCEPTIONS ═══════════
    class HiaskanBaseError {
        <<exception>>
    }
    class KualitasAirBurukError {
        <<exception>>
        +parameter: str
        +nilai: float
        +batas_min: float
        +batas_max: float
    }
    class StokIkanTidakCukupError {
        <<exception>>
        +jenis_ikan: str
        +stok_tersedia: int
        +jumlah_diminta: int
    }
    class DataTidakValidError {
        <<exception>>
        +field: str
        +pesan: str
    }
    class FileOperasiError {
        <<exception>>
        +filepath: str
        +operasi: str
        +penyebab: Exception
    }
    HiaskanBaseError <|-- KualitasAirBurukError
    HiaskanBaseError <|-- StokIkanTidakCukupError
    HiaskanBaseError <|-- DataTidakValidError
    HiaskanBaseError <|-- FileOperasiError

    %% ═══════════ STRATEGY PATTERN ═══════════
    class HargaStrategy {
        <<abstract>>
        +hitung_harga(ikan: IkanHias)* int
        +nama_strategi() str
    }
    class CupangHargaStrategy {
        +HARGA_DASAR = 25000
        +hitung_harga(ikan) int
    }
    class GuppyHargaStrategy {
        +HARGA_DASAR = 8000
        +hitung_harga(ikan) int
    }
    class KoiHargaStrategy {
        +HARGA_DASAR = 150000
        +hitung_harga(ikan) int
    }
    HargaStrategy <|-- CupangHargaStrategy
    HargaStrategy <|-- GuppyHargaStrategy
    HargaStrategy <|-- KoiHargaStrategy

    %% ═══════════ DOMAIN MODELS ═══════════
    class IkanHias {
        <<abstract>>
        +id_ikan: str
        +varietas: str
        +warna: str
        +ukuran_cm: float
        +umur_bulan: int
        +kolam_id: str
        -__jumlah_stok: int
        -__status_kesehatan: str
        #_kualitas_warna: str
        #_grade: str
        #_harga_strategy: HargaStrategy
        +jenis()* str
        +hitung_harga_jual() int
        +tambah_stok(jumlah) void
        +kurangi_stok(jumlah) void
        +stok_sehat() int
        +set_harga_strategy(strategy) void
        +to_dict() dict
        +from_dict(data)$ IkanHias
    }
    class Cupang {
        +jenis() str
        +hitung_harga_jual() int
    }
    class Guppy {
        +jenis() str
        +hitung_harga_jual() int
    }
    class Koi {
        +jenis() str
        +hitung_harga_jual() int
    }
    IkanHias <|-- Cupang
    IkanHias <|-- Guppy
    IkanHias <|-- Koi
    IkanHias --> HargaStrategy : uses

    class KualitasAir {
        +ph: float
        +suhu: float
        +oksigen: float
        +amonia: float
        +validasi() list
        +is_aman() bool
    }
    class Kolam {
        +id_kolam: str
        +nama: str
        +kapasitas: int
        +jenis_ikan: str
        +jumlah_ikan: int
        +kualitas_air: KualitasAir
        +cek_kualitas_air() void
        +is_penuh() bool
        +sisa_kapasitas() int
    }
    Kolam *-- KualitasAir

    class Pemijahan {
        +id_pemijahan: str
        +kolam_id: str
        +jenis_ikan: str
        +induk_jantan_id: str
        +induk_betina_id: str
        +tanggal_pijah: str
        +jumlah_telur: int
        +jumlah_menetas: int
        +jumlah_larva_hidup: int
        +tingkat_penetasan: float
        +tingkat_kelangsungan_hidup: float
    }

    class Pakan {
        +id_pakan: str
        +nama: str
        +jenis: str
        +stok_gram: float
        +harga_per_kg: int
        +gunakan(gram) void
        +tambah_stok(gram) void
    }

    class Pelanggan {
        +id_pelanggan: str
        +nama: str
        +telepon: str
        +alamat: str
        +total_transaksi: int
        +total_pembelian: int
    }

    class ItemPenjualan {
        +ikan_id: str
        +jenis_ikan: str
        +varietas: str
        +jumlah: int
        +harga_satuan: int
        +subtotal: int
    }
    class Penjualan {
        +id_penjualan: str
        +tanggal: str
        +pelanggan_id: str
        +pelanggan_nama: str
        +items: list~ItemPenjualan~
        +total: int
        +total_ikan: int
        +to_csv_rows() list
    }
    Penjualan *-- ItemPenjualan

    %% ═══════════ SERVICES ═══════════
    class FileHandler {
        +load_json(filepath)$ list
        +save_json(filepath, data)$ void
        +tambah_json(filepath, record)$ void
        +update_json(filepath, id, updated)$ bool
        +hapus_json(filepath, id)$ bool
        +load_csv(filepath)$ list
        +save_csv(filepath, header, rows)$ void
        +append_csv(filepath, header, rows)$ void
        +export_txt(filepath, content)$ void
    }
    class StokService {
        +load_semua_ikan() list
        +tambah_ikan(ikan) void
        +update_ikan(ikan) bool
        +hapus_ikan(id) bool
        +validasi_stok_jual(id, jumlah) IkanHias
        +total_stok_per_jenis() dict
    }
    class KolamService {
        +load_semua_kolam() list
        +tambah_kolam(kolam) void
        +cek_kualitas_air_semua() dict
    }
    class PenjualanService {
        +proses_penjualan(penjualan) Penjualan
        +load_riwayat() list
        +total_pendapatan() int
        +pendapatan_per_jenis() dict
    }
    class LaporanService {
        +laporan_stok() str
        +laporan_pendapatan() str
        +laporan_mortalitas() str
        +laporan_pakan() str
        +laporan_pertumbuhan() str
    }

    StokService --> FileHandler : uses
    StokService --> IkanHias : manages
    KolamService --> FileHandler : uses
    KolamService --> Kolam : manages
    PenjualanService --> StokService : validates
    PenjualanService --> FileHandler : uses
    LaporanService --> StokService : reads
    LaporanService --> KolamService : reads
    LaporanService --> PenjualanService : reads
```

## Keterangan Notasi
- `<<abstract>>` — kelas abstrak, tidak bisa diinstansiasi langsung
- `<<exception>>` — kelas exception custom
- `-` private, `#` protected, `+` public
- `*` abstract method
- `$` static/class method
- `<|--` inheritance (is-a)
- `-->` dependency/uses
- `*--` composition (has-a, lifecycle terikat)
