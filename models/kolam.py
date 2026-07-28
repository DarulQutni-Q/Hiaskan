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
    kualitas_air: KualitasAir = field(default_factory=KualitasAir)

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
            "kualitas_air": self.kualitas_air.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Kolam":
        air_data = data.get("kualitas_air", {})
        return cls(
            id_kolam=data.get("id", ""),
            nama=data.get("nama", ""),
            kapasitas=int(data.get("kapasitas", 0)),
            jenis_ikan=data.get("jenis_ikan", ""),
            jumlah_ikan=int(data.get("jumlah_ikan", 0)),
            kualitas_air=KualitasAir.from_dict(air_data),
        )
