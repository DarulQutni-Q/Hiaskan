"""
Model Penjualan dan ItemPenjualan.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any
from datetime import date


@dataclass
class ItemPenjualan:
    """Satu baris item dalam transaksi penjualan."""

    ikan_id: str = ""
    jenis_ikan: str = ""
    varietas: str = ""
    jumlah: int = 0
    harga_satuan: int = 0

    @property
    def subtotal(self) -> int:
        return self.jumlah * self.harga_satuan

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["subtotal"] = self.subtotal
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ItemPenjualan":
        return cls(
            ikan_id=data.get("ikan_id", ""),
            jenis_ikan=data.get("jenis_ikan", ""),
            varietas=data.get("varietas", ""),
            jumlah=int(data.get("jumlah", 0)),
            harga_satuan=int(data.get("harga_satuan", 0)),
        )


@dataclass
class Penjualan:
    """Satu transaksi penjualan ikan hias."""

    id_penjualan: str = ""
    tanggal: str = ""  # YYYY-MM-DD
    pelanggan_id: str = ""
    pelanggan_nama: str = ""
    items: list[ItemPenjualan] = field(default_factory=list)
    catatan: str = ""

    def __post_init__(self) -> None:
        if not self.tanggal:
            self.tanggal = date.today().isoformat()

    @property
    def total(self) -> int:
        return sum(item.subtotal for item in self.items)

    @property
    def total_ikan(self) -> int:
        return sum(item.jumlah for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id_penjualan,
            "tanggal": self.tanggal,
            "pelanggan_id": self.pelanggan_id,
            "pelanggan_nama": self.pelanggan_nama,
            "items": [it.to_dict() for it in self.items],
            "total": self.total,
            "catatan": self.catatan,
        }

    def to_csv_rows(self) -> list[list[str]]:
        """Konversi ke baris-baris CSV (satu baris per item)."""
        rows = []
        for item in self.items:
            rows.append([
                self.id_penjualan,
                self.tanggal,
                self.pelanggan_id,
                self.pelanggan_nama,
                item.ikan_id,
                item.jenis_ikan,
                item.varietas,
                str(item.jumlah),
                str(item.harga_satuan),
                str(item.subtotal),
                self.catatan,
            ])
        return rows

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Penjualan":
        items_data = data.get("items", [])
        items = [ItemPenjualan.from_dict(it) for it in items_data]
        return cls(
            id_penjualan=data.get("id", data.get("id_penjualan", "")),
            tanggal=data.get("tanggal", ""),
            pelanggan_id=data.get("pelanggan_id", ""),
            pelanggan_nama=data.get("pelanggan_nama", ""),
            items=items,
            catatan=data.get("catatan", ""),
        )

    # CSV header untuk export
    CSV_HEADER = [
        "id_penjualan", "tanggal", "pelanggan_id", "pelanggan_nama",
        "ikan_id", "jenis_ikan", "varietas", "jumlah",
        "harga_satuan", "subtotal", "catatan",
    ]
