"""
Strategy Pattern — Algoritma penghitungan harga jual ikan hias.

Pola desain Strategy memungkinkan algoritma harga diganti secara runtime
tanpa mengubah kelas IkanHias.  Setiap jenis ikan memiliki formula harga
yang berbeda berdasarkan ukuran, kualitas warna, umur, dan grade.

Prinsip SOLID yang diterapkan — Open/Closed Principle (OCP):
    Menambah jenis ikan baru cukup membuat subclass HargaStrategy baru
    tanpa memodifikasi kelas yang sudah ada.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.ikan import IkanHias


# ---------- Multiplier lookup tables ----------

GRADE_MULTIPLIER: dict[str, float] = {
    "A+": 2.0,
    "A": 1.5,
    "B": 1.0,
    "C": 0.7,
}

KUALITAS_WARNA_MULTIPLIER: dict[str, float] = {
    "premium": 1.8,
    "bagus": 1.3,
    "standar": 1.0,
    "pudar": 0.6,
}


def _grade_mult(grade: str) -> float:
    return GRADE_MULTIPLIER.get(grade, 1.0)


def _warna_mult(kualitas_warna: str) -> float:
    return KUALITAS_WARNA_MULTIPLIER.get(kualitas_warna.lower(), 1.0)


# ---------- Abstract Strategy ----------


class HargaStrategy(ABC):
    """Interface strategi penghitungan harga jual ikan hias."""

    @abstractmethod
    def hitung_harga(self, ikan: IkanHias) -> int:
        """Hitung harga jual dalam Rupiah (dibulatkan ke int)."""

    def nama_strategi(self) -> str:
        return self.__class__.__name__


# ---------- Concrete Strategies ----------


class CupangHargaStrategy(HargaStrategy):
    """Strategi harga untuk ikan Cupang.

    Formula:
        harga_dasar = 25_000
        harga = harga_dasar
                × pengali_ukuran(cm)
                × pengali_warna
                × pengali_grade
                × pengali_umur
    """

    HARGA_DASAR = 25_000

    def hitung_harga(self, ikan: IkanHias) -> int:
        ukuran = ikan.ukuran_cm
        # Cupang: ukuran ideal 5-7 cm
        if ukuran >= 7:
            mult_ukuran = 1.8
        elif ukuran >= 5:
            mult_ukuran = 1.4
        elif ukuran >= 3:
            mult_ukuran = 1.0
        else:
            mult_ukuran = 0.7

        # Umur optimal 3-8 bulan
        umur = ikan.umur_bulan
        if 3 <= umur <= 8:
            mult_umur = 1.3
        elif umur < 3:
            mult_umur = 0.8
        else:
            mult_umur = 0.9

        harga = (
            self.HARGA_DASAR
            * mult_ukuran
            * _warna_mult(ikan.kualitas_warna)
            * _grade_mult(ikan.grade)
            * mult_umur
        )
        return round(harga)


class GuppyHargaStrategy(HargaStrategy):
    """Strategi harga untuk ikan Guppy.

    Formula:
        harga_dasar = 8_000
        harga = harga_dasar
                × pengali_ukuran(cm)
                × pengali_warna
                × pengali_grade
                × pengali_umur
    Guppy dijual per-ekor, harga lebih rendah tapi volume tinggi.
    """

    HARGA_DASAR = 8_000

    def hitung_harga(self, ikan: IkanHias) -> int:
        ukuran = ikan.ukuran_cm
        # Guppy: ukuran ideal 3-5 cm
        if ukuran >= 5:
            mult_ukuran = 1.6
        elif ukuran >= 3:
            mult_ukuran = 1.2
        else:
            mult_ukuran = 0.8

        # Umur optimal 2-6 bulan
        umur = ikan.umur_bulan
        if 2 <= umur <= 6:
            mult_umur = 1.2
        elif umur < 2:
            mult_umur = 0.7
        else:
            mult_umur = 0.85

        harga = (
            self.HARGA_DASAR
            * mult_ukuran
            * _warna_mult(ikan.kualitas_warna)
            * _grade_mult(ikan.grade)
            * mult_umur
        )
        return round(harga)


class KoiHargaStrategy(HargaStrategy):
    """Strategi harga untuk ikan Koi.

    Formula:
        harga_dasar = 150_000
        harga = harga_dasar
                × pengali_ukuran(cm)
                × pengali_warna
                × pengali_grade
                × pengali_umur
    Koi adalah ikan premium — harga dasar tinggi, multiplier ukuran dominan.
    """

    HARGA_DASAR = 150_000

    def hitung_harga(self, ikan: IkanHias) -> int:
        ukuran = ikan.ukuran_cm
        # Koi: ukuran ideal > 25 cm, bisa sampai 60+ cm
        if ukuran >= 40:
            mult_ukuran = 3.0
        elif ukuran >= 25:
            mult_ukuran = 2.0
        elif ukuran >= 15:
            mult_ukuran = 1.3
        else:
            mult_ukuran = 0.8

        # Umur optimal > 12 bulan
        umur = ikan.umur_bulan
        if umur >= 24:
            mult_umur = 1.8
        elif umur >= 12:
            mult_umur = 1.4
        elif umur >= 6:
            mult_umur = 1.0
        else:
            mult_umur = 0.6

        harga = (
            self.HARGA_DASAR
            * mult_ukuran
            * _warna_mult(ikan.kualitas_warna)
            * _grade_mult(ikan.grade)
            * mult_umur
        )
        return round(harga)
