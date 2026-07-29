"""
StokService — manajemen stok ikan hias.

Mengelola pembacaan, pembaruan, dan validasi stok dari file ikan.json.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.ikan import IkanHias
from exceptions import StokIkanTidakCukupError, DataTidakValidError
from services.file_handler import FileHandler


class StokService:
    """Service untuk operasi stok ikan hias."""

    def __init__(self, data_dir: str | Path) -> None:
        self.filepath = Path(data_dir) / "ikan.json"

    def load_semua_ikan(self) -> list[IkanHias]:
        """Muat semua data ikan dari file."""
        data = FileHandler.load_json(self.filepath)
        hasil: list[IkanHias] = []
        for d in data:
            try:
                hasil.append(IkanHias.from_dict(d))
            except (DataTidakValidError, KeyError):
                continue  # skip data rusak
        return hasil

    def simpan_semua_ikan(self, ikan_list: list[IkanHias]) -> None:
        """Simpan semua data ikan ke file."""
        data = [ikan.to_dict() for ikan in ikan_list]
        FileHandler.save_json(self.filepath, data)
        self._sync_kolam()

    def tambah_ikan(self, ikan: IkanHias) -> None:
        """Tambah ikan baru ke file."""
        FileHandler.tambah_json(self.filepath, ikan.to_dict())
        self._sync_kolam()

    def update_ikan(self, ikan: IkanHias) -> bool:
        """Update data ikan berdasarkan ID."""
        sukses = FileHandler.update_json(self.filepath, ikan.id_ikan, ikan.to_dict())
        if sukses:
            self._sync_kolam()
        return sukses

    def hapus_ikan(self, id_ikan: str) -> bool:
        """Hapus ikan berdasarkan ID."""
        sukses = FileHandler.hapus_json(self.filepath, id_ikan)
        if sukses:
            self._sync_kolam()
        return sukses
        
    def _sync_kolam(self) -> None:
        """Sinkronisasi data kolam setiap kali ada mutasi stok."""
        from services.kolam_service import KolamService
        kolam_svc = KolamService(self.filepath.parent)
        kolam_svc.sync_jumlah_ikan()

    def cari_ikan(self, id_ikan: str) -> IkanHias | None:
        """Cari ikan berdasarkan ID."""
        data = FileHandler.cari_json(self.filepath, id_ikan)
        if data:
            return IkanHias.from_dict(data)
        return None

    def total_stok_per_jenis(self) -> dict[str, int]:
        """Hitung total stok per jenis ikan."""
        semua = self.load_semua_ikan()
        hasil: dict[str, int] = {}
        for ikan in semua:
            jenis = ikan.jenis()
            hasil[jenis] = hasil.get(jenis, 0) + ikan.jumlah_stok
        return hasil

    def total_stok_sehat_per_jenis(self) -> dict[str, int]:
        """Hitung total stok sehat (bisa dijual) per jenis."""
        semua = self.load_semua_ikan()
        hasil: dict[str, int] = {}
        for ikan in semua:
            jenis = ikan.jenis()
            hasil[jenis] = hasil.get(jenis, 0) + ikan.stok_sehat()
        return hasil

    def validasi_stok_jual(self, id_ikan: str, jumlah: int) -> IkanHias:
        """Validasi apakah stok cukup untuk penjualan.

        Returns:
            IkanHias yang valid untuk dijual.

        Raises:
            StokIkanTidakCukupError jika stok tidak cukup.
            DataTidakValidError jika ikan tidak ditemukan atau sakit.
        """
        ikan = self.cari_ikan(id_ikan)
        if ikan is None:
            raise DataTidakValidError("id_ikan", f"Ikan '{id_ikan}' tidak ditemukan")
        if ikan.status_kesehatan != "sehat":
            raise DataTidakValidError(
                "status_kesehatan",
                f"Ikan '{id_ikan}' berstatus '{ikan.status_kesehatan}', "
                f"tidak bisa dijual",
            )
        if jumlah > ikan.stok_sehat():
            raise StokIkanTidakCukupError(
                ikan.jenis(), ikan.stok_sehat(), jumlah,
            )
        return ikan

    def generate_id(self, jenis: str) -> str:
        """Generate ID baru untuk ikan berdasarkan jenis."""
        prefix_map = {"cupang": "CUP", "guppy": "GUP", "koi": "KOI"}
        prefix = prefix_map.get(jenis.lower(), "IKN")
        semua = self.load_semua_ikan()
        existing = [
            ikan.id_ikan for ikan in semua
            if ikan.id_ikan.startswith(prefix)
        ]
        if not existing:
            return f"{prefix}001"
        nums = []
        for eid in existing:
            try:
                nums.append(int(eid[len(prefix):]))
            except ValueError:
                continue
        next_num = max(nums, default=0) + 1
        return f"{prefix}{next_num:03d}"
