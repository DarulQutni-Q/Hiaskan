"""
PenjualanService — proses penjualan dengan validasi stok dan kualitas air.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from models.penjualan import Penjualan, ItemPenjualan
from models.pelanggan import Pelanggan
from services.file_handler import FileHandler
from services.stok_service import StokService


class PenjualanService:
    """Service untuk proses transaksi penjualan ikan hias."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.csv_path = self.data_dir / "penjualan.csv"
        self.pelanggan_path = self.data_dir / "pelanggan.json"
        self.stok_service = StokService(data_dir)

    # ---------- Pelanggan ----------

    def load_pelanggan(self) -> list[Pelanggan]:
        data = FileHandler.load_json(self.pelanggan_path)
        return [Pelanggan.from_dict(d) for d in data]

    def simpan_pelanggan(self, pelanggan_list: list[Pelanggan]) -> None:
        data = [p.to_dict() for p in pelanggan_list]
        FileHandler.save_json(self.pelanggan_path, data)

    def tambah_pelanggan(self, pelanggan: Pelanggan) -> None:
        FileHandler.tambah_json(self.pelanggan_path, pelanggan.to_dict())

    def cari_pelanggan(self, id_pelanggan: str) -> Pelanggan | None:
        data = FileHandler.cari_json(self.pelanggan_path, id_pelanggan)
        if data:
            return Pelanggan.from_dict(data)
        return None

    def generate_id_pelanggan(self) -> str:
        semua = self.load_pelanggan()
        if not semua:
            return "PEL001"
        nums = []
        for p in semua:
            try:
                nums.append(int(p.id_pelanggan[3:]))
            except (ValueError, IndexError):
                continue
        return f"PEL{max(nums, default=0) + 1:03d}"

    # ---------- Penjualan ----------

    def proses_penjualan(self, penjualan: Penjualan) -> Penjualan:
        """Proses penjualan: validasi stok → kurangi stok → catat transaksi.

        Raises:
            StokIkanTidakCukupError: jika stok tidak mencukupi.
            DataTidakValidError: jika data tidak valid.
        """
        # 1. Validasi semua item dulu sebelum mengurangi stok
        semua_ikan = self.stok_service.load_semua_ikan()
        ikan_map = {ikan.id_ikan: ikan for ikan in semua_ikan}

        for item in penjualan.items:
            self.stok_service.validasi_stok_jual(item.ikan_id, item.jumlah)

        # 2. Kurangi stok
        for item in penjualan.items:
            ikan = ikan_map[item.ikan_id]
            ikan.kurangi_stok(item.jumlah)
            # Set harga satuan dari kalkulasi
            item.harga_satuan = ikan.hitung_harga_jual()

        # 3. Simpan stok yang telah diperbarui
        self.stok_service.simpan_semua_ikan(list(ikan_map.values()))

        # 4. Catat penjualan ke CSV
        FileHandler.append_csv(
            self.csv_path,
            Penjualan.CSV_HEADER,
            penjualan.to_csv_rows(),
        )

        # 5. Update total transaksi pelanggan
        self._update_pelanggan_transaksi(penjualan)

        return penjualan

    def _update_pelanggan_transaksi(self, penjualan: Penjualan) -> None:
        """Update statistik pelanggan setelah penjualan."""
        semua = self.load_pelanggan()
        for p in semua:
            if p.id_pelanggan == penjualan.pelanggan_id:
                p.total_transaksi += 1
                p.total_pembelian += penjualan.total
                break
        self.simpan_pelanggan(semua)

    def load_riwayat(self) -> list[list[str]]:
        """Muat riwayat penjualan dari CSV."""
        return FileHandler.load_csv(self.csv_path)

    def generate_id_penjualan(self) -> str:
        """Generate ID penjualan baru berdasarkan tanggal."""
        today = date.today().strftime("%Y%m%d")
        riwayat = self.load_riwayat()
        count = sum(1 for r in riwayat if r and r[0].startswith(f"TRX{today}"))
        return f"TRX{today}{count + 1:03d}"

    def total_pendapatan(self) -> int:
        """Hitung total pendapatan dari semua penjualan."""
        riwayat = self.load_riwayat()
        total = 0
        for row in riwayat:
            try:
                total += int(row[9])  # kolom subtotal
            except (IndexError, ValueError):
                continue
        return total

    def pendapatan_per_jenis(self) -> dict[str, int]:
        """Hitung pendapatan per jenis ikan."""
        riwayat = self.load_riwayat()
        hasil: dict[str, int] = {}
        for row in riwayat:
            try:
                jenis = row[5]
                subtotal = int(row[9])
                hasil[jenis] = hasil.get(jenis, 0) + subtotal
            except (IndexError, ValueError):
                continue
        return hasil
