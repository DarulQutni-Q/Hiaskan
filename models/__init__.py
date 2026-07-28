"""Modul domain models untuk sistem Hiaskan."""

from .ikan import IkanHias, Cupang, Guppy, Koi
from .kolam import Kolam, KualitasAir
from .pemijahan import Pemijahan
from .pakan import Pakan
from .pelanggan import Pelanggan
from .penjualan import Penjualan, ItemPenjualan

__all__ = [
    "IkanHias", "Cupang", "Guppy", "Koi",
    "Kolam", "KualitasAir",
    "Pemijahan",
    "Pakan",
    "Pelanggan",
    "Penjualan", "ItemPenjualan",
]
