"""
KolamService — manajemen kolam dan validasi kualitas air.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.kolam import Kolam
from exceptions import DataTidakValidError
from services.file_handler import FileHandler


class KolamService:
    """Service untuk operasi kolam pemeliharaan."""

    def __init__(self, data_dir: str | Path) -> None:
        self.filepath = Path(data_dir) / "kolam.json"

    def load_semua_kolam(self) -> list[Kolam]:
        data = FileHandler.load_json(self.filepath)
        return [Kolam.from_dict(d) for d in data]

    def simpan_semua_kolam(self, kolam_list: list[Kolam]) -> None:
        data = [k.to_dict() for k in kolam_list]
        FileHandler.save_json(self.filepath, data)

    def tambah_kolam(self, kolam: Kolam) -> None:
        FileHandler.tambah_json(self.filepath, kolam.to_dict())

    def update_kolam(self, kolam: Kolam) -> bool:
        return FileHandler.update_json(
            self.filepath, kolam.id_kolam, kolam.to_dict()
        )

    def hapus_kolam(self, id_kolam: str) -> bool:
        return FileHandler.hapus_json(self.filepath, id_kolam)

    def cari_kolam(self, id_kolam: str) -> Kolam | None:
        data = FileHandler.cari_json(self.filepath, id_kolam)
        if data:
            return Kolam.from_dict(data)
        return None

    def sync_jumlah_ikan(self) -> None:
        """Sinkronisasi jumlah_ikan di setiap kolam berdasarkan total stok ikan.json."""
        kolam_list = self.load_semua_kolam()
        if not kolam_list:
            return
            
        # Ambil semua data ikan secara langsung dari JSON
        ikan_data = FileHandler.load_json(self.filepath.parent / "ikan.json")
        
        # Hitung populasi per kolam
        populasi_map: dict[str, int] = {}
        for ikan in ikan_data:
            kid = ikan.get("kolam_id", "")
            if kid:
                populasi_map[kid] = populasi_map.get(kid, 0) + int(ikan.get("jumlah_stok", 0))
                
        # Update semua kolam
        diperbarui = False
        for kolam in kolam_list:
            real_stok = populasi_map.get(kolam.id_kolam, 0)
            if kolam.jumlah_ikan != real_stok:
                kolam.jumlah_ikan = real_stok
                diperbarui = True
                
        if diperbarui:
            self.simpan_semua_kolam(kolam_list)

    def cek_kualitas_air_semua(self) -> dict[str, bool]:
        """Cek kualitas air semua kolam, return dict {id: is_aman}."""
        kolam_list = self.load_semua_kolam()
        return {k.id_kolam: k.kualitas_air.is_aman() for k in kolam_list}

    def generate_id(self) -> str:
        """Generate ID kolam baru."""
        semua = self.load_semua_kolam()
        if not semua:
            return "K001"
        nums = []
        for k in semua:
            try:
                nums.append(int(k.id_kolam[1:]))
            except (ValueError, IndexError):
                continue
        next_num = max(nums, default=0) + 1
        return f"K{next_num:03d}"
