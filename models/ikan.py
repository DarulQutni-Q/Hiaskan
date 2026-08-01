"""
Model IkanHias — superclass abstrak dan tiga subclass konkret.

Konsep OOP yang diterapkan:
    - Inheritance  : Cupang, Guppy, Koi mewarisi IkanHias.
    - Polymorphism : hitung_harga_jual() di-override tiap subclass.
    - Encapsulation: __jumlah_stok dan __status_kesehatan bersifat privat,
                     diakses melalui property dengan validasi.
    - Strategy     : Setiap subclass memiliki default HargaStrategy yang
                     bisa diganti saat runtime.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from exceptions import DataTidakValidError
from strategies import (
    HargaStrategy,
    CupangHargaStrategy,
    GuppyHargaStrategy,
    KoiHargaStrategy,
)


STATUS_VALID = ("sehat", "sakit", "karantina", "mati")
GRADE_VALID = ("A+", "A", "B", "C")
KUALITAS_WARNA_VALID = ("premium", "bagus", "standar", "pudar")


class IkanHias(ABC):
    """Superclass abstrak untuk semua jenis ikan hias.

    Encapsulation:
        __jumlah_stok       — hanya bisa diubah via property jumlah_stok
        __status_kesehatan  — hanya bisa diubah via property status_kesehatan
    """

    def __init__(
        self,
        id_ikan: str,
        varietas: str,
        warna: str,
        kualitas_warna: str,
        ukuran_cm: float,
        umur_bulan: int,
        grade: str,
        jumlah_stok: int = 0,
        status_kesehatan: str = "sehat",
        kolam_id: str = "",
        harga_strategy: HargaStrategy | None = None,
    ) -> None:
        self.id_ikan = id_ikan
        self.varietas = varietas
        self.warna = warna
        self.ukuran_cm = ukuran_cm
        self.umur_bulan = umur_bulan
        self.kolam_id = kolam_id

        # Validasi dan set atribut terkontrol
        self.kualitas_warna = kualitas_warna  # via property
        self.grade = grade                    # via property

        # Encapsulation — atribut privat
        self.__jumlah_stok: int = 0
        self.__status_kesehatan: str = "sehat"
        # Set melalui property agar tervalidasi
        self.jumlah_stok = jumlah_stok
        self.status_kesehatan = status_kesehatan

        # Strategy pattern
        self._harga_strategy: HargaStrategy = (
            harga_strategy or self._default_strategy()
        )

    # ---------- Abstract ----------

    @abstractmethod
    def jenis(self) -> str:
        """Kembalikan nama jenis ikan."""

    @abstractmethod
    def _default_strategy(self) -> HargaStrategy:
        """Kembalikan strategi harga default untuk jenis ini."""

    # ---------- Polymorphism: bisa di-override oleh subclass ----------

    def hitung_harga_jual(self) -> int:
        """Hitung harga jual menggunakan strategy yang terpasang."""
        return self._harga_strategy.hitung_harga(self)

    # ---------- Encapsulation: property jumlah_stok ----------

    @property
    def jumlah_stok(self) -> int:
        return self.__jumlah_stok

    @jumlah_stok.setter
    def jumlah_stok(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise DataTidakValidError(
                "jumlah_stok",
                "Stok harus bilangan bulat >= 0",
            )
        self.__jumlah_stok = value

    # ---------- Encapsulation: property status_kesehatan ----------

    @property
    def status_kesehatan(self) -> str:
        return self.__status_kesehatan

    @status_kesehatan.setter
    def status_kesehatan(self, value: str) -> None:
        if value not in STATUS_VALID:
            raise DataTidakValidError(
                "status_kesehatan",
                f"Harus salah satu dari {STATUS_VALID}, bukan '{value}'",
            )
        self.__status_kesehatan = value

    # ---------- Property grade & kualitas warna (tervalidasi) ----------

    @property
    def grade(self) -> str:
        return self._grade

    @grade.setter
    def grade(self, value: str) -> None:
        if value not in GRADE_VALID:
            raise DataTidakValidError(
                "grade",
                f"Harus salah satu dari {GRADE_VALID}, bukan '{value}'",
            )
        self._grade = value

    @property
    def kualitas_warna(self) -> str:
        return self._kualitas_warna

    @kualitas_warna.setter
    def kualitas_warna(self, value: str) -> None:
        v = value.lower()
        if v not in KUALITAS_WARNA_VALID:
            raise DataTidakValidError(
                "kualitas_warna",
                f"Harus salah satu dari {KUALITAS_WARNA_VALID}, bukan '{value}'",
            )
        self._kualitas_warna = v

    # ---------- Strategy swap ----------

    def set_harga_strategy(self, strategy: HargaStrategy) -> None:
        """Ganti strategi penghitungan harga saat runtime."""
        self._harga_strategy = strategy

    # ---------- Stok helpers ----------

    def tambah_stok(self, jumlah: int) -> None:
        if jumlah <= 0:
            raise DataTidakValidError("jumlah", "Tambahan stok harus > 0")
        self.jumlah_stok = self.__jumlah_stok + jumlah

    def kurangi_stok(self, jumlah: int) -> None:
        if jumlah <= 0:
            raise DataTidakValidError("jumlah", "Pengurangan stok harus > 0")
        if jumlah > self.__jumlah_stok:
            from exceptions import StokIkanTidakCukupError
            raise StokIkanTidakCukupError(
                self.jenis(), self.__jumlah_stok, jumlah,
            )
        self.jumlah_stok = self.__jumlah_stok - jumlah

    def stok_sehat(self) -> int:
        """Jumlah stok yang berstatus sehat (bisa dijual)."""
        return self.__jumlah_stok if self.__status_kesehatan == "sehat" else 0

    # ---------- Serialization ----------

    def to_dict(self) -> dict[str, Any]:
        """Konversi ke dict untuk penyimpanan JSON."""
        return {
            "id": self.id_ikan,
            "jenis": self.jenis(),
            "varietas": self.varietas,
            "warna": self.warna,
            "kualitas_warna": self.kualitas_warna,
            "ukuran_cm": self.ukuran_cm,
            "umur_bulan": self.umur_bulan,
            "grade": self.grade,
            "jumlah_stok": self.jumlah_stok,
            "status_kesehatan": self.status_kesehatan,
            "kolam_id": self.kolam_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IkanHias":
        """Factory method — buat instance sesuai jenis."""
        jenis = data.get("jenis", "").lower()
        kelas_map: dict[str, type[IkanHias]] = {
            "cupang": Cupang,
            "guppy": Guppy,
            "koi": Koi,
        }
        kelas = kelas_map.get(jenis)
        if kelas is None:
            raise DataTidakValidError("jenis", f"Jenis ikan tidak dikenal: '{jenis}'")
        return kelas(
            id_ikan=data["id"],
            varietas=data.get("varietas", ""),
            warna=data.get("warna", ""),
            kualitas_warna=data.get("kualitas_warna", "standar"),
            ukuran_cm=float(data.get("ukuran_cm", 0)),
            umur_bulan=int(data.get("umur_bulan", 0)),
            grade=data.get("grade", "B"),
            jumlah_stok=int(data.get("jumlah_stok", 0)),
            status_kesehatan=data.get("status_kesehatan", "sehat"),
            kolam_id=data.get("kolam_id", ""),
        )

    def __repr__(self) -> str:
        return (
            f"{self.jenis()}(id={self.id_ikan!r}, varietas={self.varietas!r}, "
            f"stok={self.jumlah_stok}, kesehatan={self.status_kesehatan!r})"
        )


# ======================== Subclass ========================


class Cupang(IkanHias):
    """Ikan Cupang — ikan hias populer dengan beragam varietas ekor."""

    def jenis(self) -> str:
        return "Cupang"

    def _default_strategy(self) -> HargaStrategy:
        return CupangHargaStrategy()

    def hitung_harga_jual(self) -> int:
        """Override polymorphism: Cupang mendapat bonus 10% untuk grade A+."""
        harga = self._harga_strategy.hitung_harga(self)
        if self.grade == "A+":
            harga = round(harga * 1.10)
        return harga


class Guppy(IkanHias):
    """Ikan Guppy — ikan hias kecil dengan warna cerah dan ekor lebar."""

    def jenis(self) -> str:
        return "Guppy"

    def _default_strategy(self) -> HargaStrategy:
        return GuppyHargaStrategy()

    def hitung_harga_jual(self) -> int:
        """Override polymorphism: Guppy diskon 5% jika stok > 50 (bulk)."""
        harga = self._harga_strategy.hitung_harga(self)
        if self.jumlah_stok > 50:
            harga = round(harga * 0.95)
        return harga


class Koi(IkanHias):
    """Ikan Koi — ikan hias premium dengan pola warna unik."""

    def jenis(self) -> str:
        return "Koi"

    def _default_strategy(self) -> HargaStrategy:
        return KoiHargaStrategy()

    def hitung_harga_jual(self) -> int:
        """Override polymorphism: Koi > 30 cm mendapat premium 20%."""
        harga = self._harga_strategy.hitung_harga(self)
        if self.ukuran_cm > 30:
            harga = round(harga * 1.20)
        return harga
