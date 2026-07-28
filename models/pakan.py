"""
Model Pakan — pencatatan jenis pakan dan penggunaannya.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Pakan:
    """Data pakan ikan hias dan pencatatan penggunaannya."""

    id_pakan: str = ""
    nama: str = ""
    jenis: str = ""               # pelet / cacing / artemia / spirulina
    merek: str = ""
    stok_gram: float = 0.0
    harga_per_kg: int = 0
    tanggal_beli: str = ""        # YYYY-MM-DD
    tanggal_kadaluarsa: str = ""  # YYYY-MM-DD
    catatan: str = ""

    def gunakan(self, gram: float) -> None:
        """Kurangi stok pakan setelah digunakan."""
        if gram <= 0:
            from exceptions import DataTidakValidError
            raise DataTidakValidError("gram", "Jumlah pakan harus > 0")
        if gram > self.stok_gram:
            from exceptions import DataTidakValidError
            raise DataTidakValidError(
                "gram",
                f"Stok pakan tidak cukup: tersedia {self.stok_gram}g, "
                f"diminta {gram}g",
            )
        self.stok_gram = round(self.stok_gram - gram, 2)

    def tambah_stok(self, gram: float) -> None:
        """Tambah stok pakan."""
        if gram <= 0:
            from exceptions import DataTidakValidError
            raise DataTidakValidError("gram", "Tambahan harus > 0")
        self.stok_gram = round(self.stok_gram + gram, 2)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["id"] = d.pop("id_pakan")
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pakan":
        return cls(
            id_pakan=data.get("id", data.get("id_pakan", "")),
            nama=data.get("nama", ""),
            jenis=data.get("jenis", ""),
            merek=data.get("merek", ""),
            stok_gram=float(data.get("stok_gram", 0)),
            harga_per_kg=int(data.get("harga_per_kg", 0)),
            tanggal_beli=data.get("tanggal_beli", ""),
            tanggal_kadaluarsa=data.get("tanggal_kadaluarsa", ""),
            catatan=data.get("catatan", ""),
        )
