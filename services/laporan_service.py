"""
LaporanService — generate dan export laporan ke CSV/TXT.

Jenis laporan:
    1. Laporan Stok         → laporan/laporan_stok.csv
    2. Laporan Pendapatan   → laporan/laporan_pendapatan.txt
    3. Laporan Mortalitas   → laporan/laporan_mortalitas.csv
    4. Laporan Pakan        → laporan/laporan_pakan.csv
    5. Laporan Pertumbuhan  → laporan/laporan_pertumbuhan.csv
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from models.ikan import IkanHias
from models.kolam import Kolam
from models.pakan import Pakan
from models.pemijahan import Pemijahan
from services.file_handler import FileHandler
from services.stok_service import StokService
from services.kolam_service import KolamService
from services.penjualan_service import PenjualanService


class LaporanService:
    """Service untuk generate laporan-laporan sistem."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.laporan_dir = self.data_dir.parent / "laporan"
        self.laporan_dir.mkdir(exist_ok=True)

        self.stok_svc = StokService(data_dir)
        self.kolam_svc = KolamService(data_dir)
        self.jual_svc = PenjualanService(data_dir)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    # ---- 1. Laporan Stok ----

    def laporan_stok(self) -> str:
        """Generate laporan stok ke CSV. Return filepath."""
        semua_ikan = self.stok_svc.load_semua_ikan()
        header = [
            "ID", "Jenis", "Varietas", "Warna", "Ukuran(cm)",
            "Grade", "Stok", "Status", "Harga Jual (Rp)",
        ]
        rows = []
        for ikan in semua_ikan:
            rows.append([
                ikan.id_ikan,
                ikan.jenis(),
                ikan.varietas,
                ikan.warna,
                str(ikan.ukuran_cm),
                ikan.grade,
                str(ikan.jumlah_stok),
                ikan.status_kesehatan,
                str(ikan.hitung_harga_jual()),
            ])
        filepath = self.laporan_dir / f"laporan_stok_{self._timestamp()}.csv"
        FileHandler.save_csv(filepath, header, rows)
        return str(filepath)

    # ---- 2. Laporan Pendapatan ----

    def laporan_pendapatan(self) -> str:
        """Generate laporan pendapatan ke TXT. Return filepath."""
        total = self.jual_svc.total_pendapatan()
        per_jenis = self.jual_svc.pendapatan_per_jenis()
        stok = self.stok_svc.total_stok_per_jenis()
        stok_sehat = self.stok_svc.total_stok_sehat_per_jenis()

        lines = [
            "=" * 60,
            "  LAPORAN PENDAPATAN - HIASKAN",
            f"  Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "=" * 60,
            "",
            f"  Total Pendapatan: Rp {total:,}".replace(",", "."),
            "",
            "  Pendapatan per Jenis Ikan:",
            "  " + "-" * 40,
        ]
        for jenis, nominal in sorted(per_jenis.items()):
            lines.append(
                f"    {jenis:<15} Rp {nominal:>12,}".replace(",", ".")
            )
        lines += [
            "",
            "  Ringkasan Stok:",
            "  " + "-" * 40,
        ]
        for jenis in sorted(set(list(stok.keys()) + list(stok_sehat.keys()))):
            s = stok.get(jenis, 0)
            sh = stok_sehat.get(jenis, 0)
            lines.append(f"    {jenis:<15} Total: {s:>5}   Sehat: {sh:>5}")
        lines += ["", "=" * 60]

        content = "\n".join(lines)
        filepath = self.laporan_dir / f"laporan_pendapatan_{self._timestamp()}.txt"
        FileHandler.export_txt(filepath, content)
        return str(filepath)

    # ---- 3. Laporan Mortalitas ----

    def laporan_mortalitas(self) -> str:
        """Generate laporan mortalitas (ikan mati/sakit) ke CSV."""
        semua = self.stok_svc.load_semua_ikan()
        header = ["ID", "Jenis", "Varietas", "Status", "Stok"]
        rows = [
            [ikan.id_ikan, ikan.jenis(), ikan.varietas,
             ikan.status_kesehatan, str(ikan.jumlah_stok)]
            for ikan in semua
            if ikan.status_kesehatan in ("mati", "sakit", "karantina")
        ]
        filepath = self.laporan_dir / f"laporan_mortalitas_{self._timestamp()}.csv"
        FileHandler.save_csv(filepath, header, rows)
        return str(filepath)

    # ---- 4. Laporan Pakan ----

    def laporan_pakan(self) -> str:
        """Generate laporan stok pakan ke CSV."""
        pakan_path = self.data_dir / "pakan.json"
        data = FileHandler.load_json(pakan_path)
        header = [
            "ID", "Nama", "Jenis", "Merek", "Stok(g)",
            "Harga/kg", "Kadaluarsa",
        ]
        rows = []
        for d in data:
            rows.append([
                d.get("id", ""),
                d.get("nama", ""),
                d.get("jenis", ""),
                d.get("merek", ""),
                str(d.get("stok_gram", 0)),
                str(d.get("harga_per_kg", 0)),
                d.get("tanggal_kadaluarsa", ""),
            ])
        filepath = self.laporan_dir / f"laporan_pakan_{self._timestamp()}.csv"
        FileHandler.save_csv(filepath, header, rows)
        return str(filepath)

    # ---- 5. Laporan Pertumbuhan (dari pemijahan) ----

    def laporan_pertumbuhan(self) -> str:
        """Generate laporan pertumbuhan dari data pemijahan ke CSV."""
        pijah_path = self.data_dir / "pemijahan.json"
        data = FileHandler.load_json(pijah_path)
        header = [
            "ID", "Jenis", "Tgl Pijah", "Telur", "Menetas",
            "Larva Hidup", "% Penetasan", "% Kelangsungan",
        ]
        rows = []
        for d in data:
            p = Pemijahan.from_dict(d)
            rows.append([
                p.id_pemijahan,
                p.jenis_ikan,
                p.tanggal_pijah,
                str(p.jumlah_telur),
                str(p.jumlah_menetas),
                str(p.jumlah_larva_hidup),
                f"{p.tingkat_penetasan:.1f}%",
                f"{p.tingkat_kelangsungan_hidup:.1f}%",
            ])
        filepath = self.laporan_dir / f"laporan_pertumbuhan_{self._timestamp()}.csv"
        FileHandler.save_csv(filepath, header, rows)
        return str(filepath)
