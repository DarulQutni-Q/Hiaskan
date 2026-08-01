"""
Model Pemijahan — pencatatan proses pemijahan dan data larva.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Pemijahan:
    """Catatan satu sesi pemijahan ikan hias."""

    id_pemijahan: str = ""
    kolam_id: str = ""
    jenis_ikan: str = ""
    induk_jantan_id: str = ""
    induk_betina_id: str = ""
    tanggal_pijah: str = ""          # YYYY-MM-DD
    jumlah_telur: int = 0
    jumlah_menetas: int = 0
    jumlah_larva_hidup: int = 0
    tanggal_panen: str = ""          # YYYY-MM-DD
    status: str = "berlangsung"      # berlangsung / selesai / gagal
    catatan: str = ""

    @property
    def tingkat_penetasan(self) -> float:
        """Persentase telur yang menetas."""
        if self.jumlah_telur == 0:
            return 0.0
        return round(self.jumlah_menetas / self.jumlah_telur * 100, 1)

    @property
    def tingkat_kelangsungan_hidup(self) -> float:
        """Persentase larva yang bertahan hidup dari yang menetas."""
        if self.jumlah_menetas == 0:
            return 0.0
        return round(self.jumlah_larva_hidup / self.jumlah_menetas * 100, 1)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["id"] = d.pop("id_pemijahan")
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pemijahan":
        return cls(
            id_pemijahan=data.get("id", data.get("id_pemijahan", "")),
            kolam_id=data.get("kolam_id", ""),
            jenis_ikan=data.get("jenis_ikan", ""),
            induk_jantan_id=data.get("induk_jantan_id", ""),
            induk_betina_id=data.get("induk_betina_id", ""),
            tanggal_pijah=data.get("tanggal_pijah", ""),
            jumlah_telur=int(data.get("jumlah_telur", 0)),
            jumlah_menetas=int(data.get("jumlah_menetas", 0)),
            jumlah_larva_hidup=int(data.get("jumlah_larva_hidup", 0)),
            tanggal_panen=data.get("tanggal_panen", ""),
            status=data.get("status", "berlangsung"),
            catatan=data.get("catatan", ""),
        )
