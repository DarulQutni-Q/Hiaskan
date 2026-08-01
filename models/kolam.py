"""
Model Kolam dan KualitasAir.

Kolam menyimpan data fisik kolam dan parameter kualitas air.
Validasi kualitas air memicu KualitasAirBurukError bila di luar batas aman.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from exceptions import KualitasAirBurukError, DataTidakValidError


# Batas aman parameter air untuk ikan hias air tawar
BATAS_AMAN: dict[str, tuple[float, float]] = {
    "ph": (6.5, 8.0),
    "suhu": (24.0, 30.0),        # Celcius
    "oksigen": (5.0, 12.0),      # mg/L
    "amonia": (0.0, 0.02),       # mg/L — semakin rendah semakin baik
}


@dataclass
class KualitasAir:
    """Parameter kualitas air dalam satu kolam."""

    ph: float = 7.0
    suhu: float = 27.0
    oksigen: float = 6.5
    amonia: float = 0.01

    def validasi(self) -> list[str]:
        """Validasi semua parameter, kembalikan daftar pelanggaran.

        Raises:
            KualitasAirBurukError: jika ada parameter di luar batas aman.
        """
        masalah: list[str] = []
        for param, (bmin, bmax) in BATAS_AMAN.items():
            nilai = getattr(self, param)
            if nilai < bmin or nilai > bmax:
                masalah.append(
                    f"{param}={nilai} (batas {bmin}-{bmax})"
                )
        if masalah:
            # Lempar exception untuk parameter pertama yang bermasalah
            param0 = list(BATAS_AMAN.keys())[0]
            for param, (bmin, bmax) in BATAS_AMAN.items():
                nilai = getattr(self, param)
                if nilai < bmin or nilai > bmax:
                    raise KualitasAirBurukError(param, nilai, bmin, bmax)
        return masalah

    def is_aman(self) -> bool:
        """Cek apakah semua parameter dalam batas aman (tanpa exception)."""
        for param, (bmin, bmax) in BATAS_AMAN.items():
            nilai = getattr(self, param)
            if nilai < bmin or nilai > bmax:
                return False
        return True

    def to_dict(self) -> dict[str, float]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KualitasAir":
        return cls(
            ph=float(data.get("ph", 7.0)),
            suhu=float(data.get("suhu", 27.0)),
            oksigen=float(data.get("oksigen", 6.5)),
            amonia=float(data.get("amonia", 0.01)),
        )


@dataclass
class Kolam:
    """Representasi satu kolam pemeliharaan/pemijahan ikan."""

    id_kolam: str = ""
    nama: str = ""
    kapasitas: int = 0
    jenis_ikan: str = ""
    jumlah_ikan: int = 0
    suhu_air: float = 27.0  # Suhu tetap bisa diinput manual karena dipengaruhi cuaca

    @property
    def kualitas_air(self) -> KualitasAir:
        """Kalkulasi parameter air secara dinamis berdasarkan kepadatan populasi."""
        if self.kapasitas <= 0:
            rasio = 0.0
        else:
            rasio = self.jumlah_ikan / self.kapasitas

        kualitas = KualitasAir(suhu=self.suhu_air)

        if rasio > 1.0:
            lebihan = rasio - 1.0
            # Degradasi kualitas air akibat overcrowding
            kualitas.amonia = round(0.01 + (lebihan * 0.05), 3)
            kualitas.oksigen = round(max(0.0, 7.0 - (lebihan * 2.0)), 2)
            kualitas.ph = round(max(0.0, 7.0 - (lebihan * 1.5)), 2)
        else:
            # Kondisi ideal jika tidak overcrowded
            kualitas.amonia = 0.01
            kualitas.oksigen = 7.0
            kualitas.ph = 7.0

        return kualitas

    def cek_kualitas_air(self) -> None:
        """Validasi kualitas air — raise KualitasAirBurukError jika buruk."""
        self.kualitas_air.validasi()

    def is_penuh(self) -> bool:
        return self.jumlah_ikan >= self.kapasitas

    def sisa_kapasitas(self) -> int:
        return max(0, self.kapasitas - self.jumlah_ikan)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id_kolam,
            "nama": self.nama,
            "kapasitas": self.kapasitas,
            "jenis_ikan": self.jenis_ikan,
            "jumlah_ikan": self.jumlah_ikan,
            "suhu_air": self.suhu_air,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Kolam":
        # Kompatibilitas dengan data JSON lama yang memiliki 'kualitas_air'
        suhu = float(data.get("suhu_air", 27.0))
        if "kualitas_air" in data and "suhu" in data["kualitas_air"]:
            suhu = float(data["kualitas_air"]["suhu"])

        return cls(
            id_kolam=data.get("id", ""),
            nama=data.get("nama", ""),
            kapasitas=int(data.get("kapasitas", 0)),
            jenis_ikan=data.get("jenis_ikan", ""),
            jumlah_ikan=int(data.get("jumlah_ikan", 0)),
            suhu_air=suhu,
        )
