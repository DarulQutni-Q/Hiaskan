"""
Unit tests untuk sistem Hiaskan — Pembibitan Ikan Hias & Penjualan.

Mencakup 12 test case:
    1-2   : Inheritance & isinstance checks
    3-4   : Polymorphism — hitung_harga_jual() override
    5-6   : Encapsulation — __jumlah_stok, __status_kesehatan
    7-8   : Custom exceptions — KualitasAirBurukError, StokIkanTidakCukupError
    9-10  : Strategy pattern — swap strategy, harga berubah
    11-12 : File handling — JSON CRUD, CSV append, file error
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Pastikan root project ada di sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.ikan import IkanHias, Cupang, Guppy, Koi
from models.kolam import Kolam, KualitasAir
from models.pakan import Pakan
from models.penjualan import Penjualan, ItemPenjualan

from strategies.harga_strategy import (
    HargaStrategy,
    CupangHargaStrategy,
    GuppyHargaStrategy,
    KoiHargaStrategy,
)

from exceptions import (
    HiaskanBaseError,
    KualitasAirBurukError,
    StokIkanTidakCukupError,
    DataTidakValidError,
    FileOperasiError,
)

from services.file_handler import FileHandler
from services.stok_service import StokService


# ─────────────────── Fixtures ───────────────────


@pytest.fixture
def cupang() -> Cupang:
    return Cupang(
        id_ikan="CUP001",
        varietas="Halfmoon",
        warna="Merah",
        kualitas_warna="premium",
        ukuran_cm=5.5,
        umur_bulan=5,
        grade="A+",
        jumlah_stok=10,
        status_kesehatan="sehat",
    )


@pytest.fixture
def guppy() -> Guppy:
    return Guppy(
        id_ikan="GUP001",
        varietas="Cobra",
        warna="Kuning",
        kualitas_warna="bagus",
        ukuran_cm=3.5,
        umur_bulan=3,
        grade="A",
        jumlah_stok=60,
        status_kesehatan="sehat",
    )


@pytest.fixture
def koi() -> Koi:
    return Koi(
        id_ikan="KOI001",
        varietas="Kohaku",
        warna="Merah-Putih",
        kualitas_warna="premium",
        ukuran_cm=28.0,
        umur_bulan=14,
        grade="A+",
        jumlah_stok=5,
        status_kesehatan="sehat",
    )


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Buat direktori data sementara untuk testing file handling."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


# ═══════════════════ TEST 1-2: INHERITANCE ═══════════════════


class TestInheritance:
    """Buktikan Cupang, Guppy, Koi adalah subclass IkanHias."""

    def test_cupang_is_ikan_hias(self, cupang: Cupang) -> None:
        """Test 1: Cupang isinstance IkanHias."""
        assert isinstance(cupang, IkanHias)
        assert isinstance(cupang, Cupang)
        assert cupang.jenis() == "Cupang"

    def test_semua_subclass_is_ikan_hias(
        self, cupang: Cupang, guppy: Guppy, koi: Koi,
    ) -> None:
        """Test 2: Semua subclass adalah instance IkanHias."""
        ikan_list: list[IkanHias] = [cupang, guppy, koi]
        for ikan in ikan_list:
            assert isinstance(ikan, IkanHias)

        # Verifikasi jenis berbeda
        jenis_set = {ikan.jenis() for ikan in ikan_list}
        assert jenis_set == {"Cupang", "Guppy", "Koi"}


# ═══════════════════ TEST 3-4: POLYMORPHISM ═══════════════════


class TestPolymorphism:
    """Buktikan hitung_harga_jual() menghasilkan harga berbeda per subclass."""

    def test_harga_berbeda_per_jenis(
        self, cupang: Cupang, guppy: Guppy, koi: Koi,
    ) -> None:
        """Test 3: Polymorphism — harga jual berbeda meski dipanggil
        dengan referensi superclass."""
        # Panggil via referensi superclass
        ikan_list: list[IkanHias] = [cupang, guppy, koi]
        harga_list = [ikan.hitung_harga_jual() for ikan in ikan_list]

        # Harga harus positif
        for harga in harga_list:
            assert harga > 0

        # Harga Koi harus lebih mahal dari Guppy
        harga_koi = koi.hitung_harga_jual()
        harga_guppy = guppy.hitung_harga_jual()
        assert harga_koi > harga_guppy

    def test_override_cupang_bonus_grade_a_plus(self, cupang: Cupang) -> None:
        """Test 4: Cupang grade A+ mendapat bonus 10% (override spesifik)."""
        # Cupang A+ vs Cupang A — yang A+ harus lebih mahal
        cupang_a = Cupang(
            id_ikan="CUP_A",
            varietas="Halfmoon",
            warna="Merah",
            kualitas_warna="premium",
            ukuran_cm=5.5,
            umur_bulan=5,
            grade="A",
            jumlah_stok=10,
        )
        harga_a_plus = cupang.hitung_harga_jual()  # grade A+
        harga_a = cupang_a.hitung_harga_jual()      # grade A
        assert harga_a_plus > harga_a


# ═══════════════════ TEST 5-6: ENCAPSULATION ═══════════════════


class TestEncapsulation:
    """Buktikan __jumlah_stok dan __status_kesehatan terproteksi."""

    def test_stok_tidak_bisa_negatif(self, cupang: Cupang) -> None:
        """Test 5: Setting stok negatif memicu DataTidakValidError."""
        with pytest.raises(DataTidakValidError):
            cupang.jumlah_stok = -5

        # Akses langsung atribut privat tidak bisa
        with pytest.raises(AttributeError):
            _ = cupang.__jumlah_stok  # type: ignore[attr-defined]  # noqa

    def test_status_kesehatan_tervalidasi(self, cupang: Cupang) -> None:
        """Test 6: Setting status tidak valid memicu DataTidakValidError."""
        with pytest.raises(DataTidakValidError):
            cupang.status_kesehatan = "super_sehat"

        # Set ke status valid berhasil
        cupang.status_kesehatan = "sakit"
        assert cupang.status_kesehatan == "sakit"

        # Verifikasi property bekerja
        cupang.jumlah_stok = 100
        assert cupang.jumlah_stok == 100


# ═══════════════════ TEST 7-8: CUSTOM EXCEPTION ═══════════════════


class TestCustomException:
    """Buktikan KualitasAirBurukError dan StokIkanTidakCukupError."""

    def test_kualitas_air_buruk_error(self) -> None:
        """Test 7: pH di luar batas aman memicu KualitasAirBurukError."""
        air_buruk = KualitasAir(ph=4.5, suhu=27.0, oksigen=6.5, amonia=0.01)
        with pytest.raises(KualitasAirBurukError) as exc_info:
            air_buruk.validasi()
        assert exc_info.value.parameter == "ph"
        assert exc_info.value.nilai == 4.5

        # Air baik tidak boleh raise
        air_baik = KualitasAir(ph=7.0, suhu=27.0, oksigen=6.5, amonia=0.01)
        assert air_baik.is_aman() is True

    def test_stok_tidak_cukup_error(self, cupang: Cupang) -> None:
        """Test 8: Jual melebihi stok memicu StokIkanTidakCukupError."""
        assert cupang.jumlah_stok == 10

        with pytest.raises(StokIkanTidakCukupError) as exc_info:
            cupang.kurangi_stok(100)
        assert exc_info.value.stok_tersedia == 10
        assert exc_info.value.jumlah_diminta == 100

        # Kurangi stok yang valid berhasil
        cupang.kurangi_stok(3)
        assert cupang.jumlah_stok == 7


# ═══════════════════ TEST 9-10: STRATEGY PATTERN ═══════════════════


class TestStrategyPattern:
    """Buktikan Strategy Pattern — swap strategy runtime, harga berubah."""

    def test_swap_strategy_changes_price(self, cupang: Cupang) -> None:
        """Test 9: Ganti strategy pada Cupang ke KoiHargaStrategy → harga berubah."""
        harga_awal = cupang.hitung_harga_jual()

        # Swap ke strategy Koi (harga dasar jauh lebih tinggi)
        cupang.set_harga_strategy(KoiHargaStrategy())
        harga_baru = cupang.hitung_harga_jual()

        # Harga harus berubah drastis
        assert harga_baru != harga_awal
        assert harga_baru > harga_awal  # Koi jauh lebih mahal

    def test_setiap_jenis_punya_strategy_default(
        self, cupang: Cupang, guppy: Guppy, koi: Koi,
    ) -> None:
        """Test 10: Setiap subclass punya default strategy yang benar."""
        assert isinstance(cupang._harga_strategy, CupangHargaStrategy)
        assert isinstance(guppy._harga_strategy, GuppyHargaStrategy)
        assert isinstance(koi._harga_strategy, KoiHargaStrategy)


# ═══════════════════ TEST 11-12: FILE HANDLING ═══════════════════


class TestFileHandling:
    """Buktikan CRUD JSON dan CSV baca-tulis benar."""

    def test_json_crud(self, tmp_data_dir: Path) -> None:
        """Test 11: Buat, baca, update, hapus record di JSON."""
        filepath = tmp_data_dir / "test_ikan.json"

        # 1. Buat file awal (auto-create)
        data = FileHandler.load_json(filepath)
        assert data == []

        # 2. Tambah record
        rec = {"id": "T001", "nama": "Test Ikan", "stok": 10}
        FileHandler.tambah_json(filepath, rec)
        data = FileHandler.load_json(filepath)
        assert len(data) == 1
        assert data[0]["id"] == "T001"

        # 3. Update record
        rec_updated = {"id": "T001", "nama": "Updated", "stok": 20}
        result = FileHandler.update_json(filepath, "T001", rec_updated)
        assert result is True
        data = FileHandler.load_json(filepath)
        assert data[0]["nama"] == "Updated"
        assert data[0]["stok"] == 20

        # 4. Hapus record
        result = FileHandler.hapus_json(filepath, "T001")
        assert result is True
        data = FileHandler.load_json(filepath)
        assert len(data) == 0

    def test_csv_append_dan_baca(self, tmp_data_dir: Path) -> None:
        """Test 12: Append baris ke CSV dan baca kembali."""
        filepath = tmp_data_dir / "test_penjualan.csv"
        header = ["id", "tanggal", "jumlah"]
        rows = [["TRX001", "2026-07-28", "5"]]

        # Append (buat file + header)
        FileHandler.append_csv(filepath, header, rows)
        assert filepath.exists()

        # Baca kembali
        result = FileHandler.load_csv(filepath)
        assert len(result) == 1
        assert result[0][0] == "TRX001"

        # Append lagi
        FileHandler.append_csv(filepath, header, [["TRX002", "2026-07-29", "3"]])
        result = FileHandler.load_csv(filepath)
        assert len(result) == 2

    def test_json_corrupt_raises_error(self, tmp_data_dir: Path) -> None:
        """Test tambahan: File JSON rusak memicu FileOperasiError."""
        filepath = tmp_data_dir / "corrupt.json"
        filepath.write_text("{invalid json content!!!", encoding="utf-8")

        with pytest.raises(FileOperasiError) as exc_info:
            FileHandler.load_json(filepath)
        assert "baca" in str(exc_info.value)

    def test_from_dict_factory_method(self) -> None:
        """Test tambahan: IkanHias.from_dict() membuat instance yang benar."""
        data = {
            "id": "CUP_TEST",
            "jenis": "Cupang",
            "varietas": "Halfmoon",
            "warna": "Merah",
            "kualitas_warna": "standar",
            "ukuran_cm": 4.0,
            "umur_bulan": 3,
            "grade": "B",
            "jumlah_stok": 5,
        }
        ikan = IkanHias.from_dict(data)
        assert isinstance(ikan, Cupang)
        assert ikan.jenis() == "Cupang"
        assert ikan.jumlah_stok == 5

        # Jenis tidak dikenal harus error
        with pytest.raises(DataTidakValidError):
            IkanHias.from_dict({"id": "X", "jenis": "Arwana"})
