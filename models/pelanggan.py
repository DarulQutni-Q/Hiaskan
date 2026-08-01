"""
Model Pelanggan — data pembeli ikan hias.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Pelanggan:
    """Data pelanggan pembeli ikan hias."""

    id_pelanggan: str = ""
    nama: str = ""
    telepon: str = ""
    alamat: str = ""
    total_transaksi: int = 0
    total_pembelian: int = 0  # Rupiah

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["id"] = d.pop("id_pelanggan")
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pelanggan":
        return cls(
            id_pelanggan=data.get("id", data.get("id_pelanggan", "")),
            nama=data.get("nama", ""),
            telepon=data.get("telepon", ""),
            alamat=data.get("alamat", ""),
            total_transaksi=int(data.get("total_transaksi", 0)),
            total_pembelian=int(data.get("total_pembelian", 0)),
        )
