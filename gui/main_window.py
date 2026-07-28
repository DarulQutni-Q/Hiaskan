"""
MainWindow — Jendela utama GUI Hiaskan dengan tab navigasi.

Layout minimalis: header tipis, tab bar bersih, status bar informatif.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QStatusBar,
    QGroupBox,
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QSpinBox,
    QFileDialog,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, QTimer

from gui.styles import STYLESHEET, COLORS
from gui.dialogs import (
    IkanDialog,
    KolamDialog,
    PakanDialog,
    PelangganDialog,
    PemijahanDialog,
    PenjualanItemDialog,
)

from models.ikan import IkanHias
from models.kolam import Kolam
from models.pakan import Pakan
from models.pelanggan import Pelanggan
from models.pemijahan import Pemijahan
from models.penjualan import Penjualan, ItemPenjualan

from services.file_handler import FileHandler
from services.stok_service import StokService
from services.kolam_service import KolamService
from services.penjualan_service import PenjualanService
from services.laporan_service import LaporanService

from exceptions import (
    HiaskanBaseError,
    KualitasAirBurukError,
    StokIkanTidakCukupError,
    DataTidakValidError,
    FileOperasiError,
)


class MainWindow(QMainWindow):
    """Jendela utama aplikasi Hiaskan."""

    def __init__(self, data_dir: str | Path) -> None:
        super().__init__()
        self.data_dir = Path(data_dir)

        # Services
        self.stok_svc = StokService(self.data_dir)
        self.kolam_svc = KolamService(self.data_dir)
        self.jual_svc = PenjualanService(self.data_dir)
        self.laporan_svc = LaporanService(self.data_dir)

        self._setup_window()
        self._build_ui()

    def _setup_window(self) -> None:
        self.setWindowTitle("Hiaskan — Sistem Pembibitan Ikan Hias & Penjualan")
        self.setMinimumSize(1000, 650)
        self.resize(1120, 720)
        self.setStyleSheet(STYLESHEET)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 8)
        root.setSpacing(8)

        # Header
        header = QLabel("Hiaskan")
        header.setProperty("class", "heading")
        sub = QLabel("Sistem Pembibitan Ikan Hias & Penjualan")
        sub.setProperty("class", "subheading")
        root.addWidget(header)
        root.addWidget(sub)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._tab_dashboard(), "Dashboard")
        self.tabs.addTab(self._tab_ikan(), "Ikan")
        self.tabs.addTab(self._tab_kolam(), "Kolam")
        self.tabs.addTab(self._tab_pakan(), "Pakan")
        self.tabs.addTab(self._tab_pemijahan(), "Pemijahan")
        self.tabs.addTab(self._tab_penjualan(), "Penjualan")
        self.tabs.addTab(self._tab_pelanggan(), "Pelanggan")
        self.tabs.addTab(self._tab_laporan(), "Laporan")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Siap")

    # ══════════════════ Tab: Dashboard ══════════════════

    def _tab_dashboard(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        # Stat cards
        cards = QHBoxLayout()
        cards.setSpacing(12)

        self.stat_total_ikan = self._stat_card("Total Ikan", "0")
        self.stat_stok_sehat = self._stat_card("Stok Sehat", "0")
        self.stat_total_kolam = self._stat_card("Total Kolam", "0")
        self.stat_pendapatan = self._stat_card("Pendapatan", "Rp 0")

        cards.addWidget(self.stat_total_ikan)
        cards.addWidget(self.stat_stok_sehat)
        cards.addWidget(self.stat_total_kolam)
        cards.addWidget(self.stat_pendapatan)
        layout.addLayout(cards)

        # Ringkasan stok per jenis
        grp = QGroupBox("Ringkasan Stok per Jenis")
        grp_layout = QVBoxLayout(grp)
        self.tbl_ringkasan = QTableWidget(0, 4)
        self.tbl_ringkasan.setHorizontalHeaderLabels(
            ["Jenis", "Total Stok", "Stok Sehat", "Rata-rata Harga"]
        )
        self.tbl_ringkasan.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_ringkasan.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_ringkasan.setAlternatingRowColors(True)
        grp_layout.addWidget(self.tbl_ringkasan)
        layout.addWidget(grp)

        layout.addStretch()
        return w

    def _stat_card(self, label: str, value: str) -> QGroupBox:
        card = QGroupBox()
        card.setFixedHeight(100)
        vl = QVBoxLayout(card)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl = QLabel(value)
        val_lbl.setProperty("class", "stat-value")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl = QLabel(label)
        name_lbl.setProperty("class", "stat-label")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(val_lbl)
        vl.addWidget(name_lbl)
        card._val_label = val_lbl  # type: ignore[attr-defined]
        return card

    def _refresh_dashboard(self) -> None:
        try:
            semua = self.stok_svc.load_semua_ikan()
            total = sum(i.jumlah_stok for i in semua)
            sehat = sum(i.stok_sehat() for i in semua)
            kolam_list = self.kolam_svc.load_semua_kolam()
            pendapatan = self.jual_svc.total_pendapatan()

            self.stat_total_ikan._val_label.setText(str(total))  # type: ignore
            self.stat_stok_sehat._val_label.setText(str(sehat))  # type: ignore
            self.stat_total_kolam._val_label.setText(str(len(kolam_list)))  # type: ignore
            self.stat_pendapatan._val_label.setText(  # type: ignore
                f"Rp {pendapatan:,}".replace(",", ".")
            )

            # Ringkasan per jenis
            stok_jenis = self.stok_svc.total_stok_per_jenis()
            stok_sehat_jenis = self.stok_svc.total_stok_sehat_per_jenis()
            jenis_set = sorted(set(list(stok_jenis.keys()) + list(stok_sehat_jenis.keys())))

            self.tbl_ringkasan.setRowCount(len(jenis_set))
            for row, jenis in enumerate(jenis_set):
                ts = stok_jenis.get(jenis, 0)
                ss = stok_sehat_jenis.get(jenis, 0)
                # Hitung rata-rata harga
                ikan_jenis = [i for i in semua if i.jenis() == jenis]
                avg_harga = (
                    sum(i.hitung_harga_jual() for i in ikan_jenis) // len(ikan_jenis)
                    if ikan_jenis else 0
                )
                self.tbl_ringkasan.setItem(row, 0, QTableWidgetItem(jenis))
                self.tbl_ringkasan.setItem(row, 1, QTableWidgetItem(str(ts)))
                self.tbl_ringkasan.setItem(row, 2, QTableWidgetItem(str(ss)))
                self.tbl_ringkasan.setItem(
                    row, 3,
                    QTableWidgetItem(f"Rp {avg_harga:,}".replace(",", ".")),
                )
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error dashboard: {e}")

    # ══════════════════ Tab: Ikan ══════════════════

    def _tab_ikan(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # Toolbar
        tb = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Ikan")
        btn_tambah.clicked.connect(self._tambah_ikan)
        btn_edit = QPushButton("Edit")
        btn_edit.setProperty("class", "secondary")
        btn_edit.clicked.connect(self._edit_ikan)
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setProperty("class", "danger")
        btn_hapus.clicked.connect(self._hapus_ikan)
        tb.addWidget(btn_tambah)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_hapus)
        tb.addStretch()
        layout.addLayout(tb)

        # Table
        self.tbl_ikan = QTableWidget(0, 10)
        self.tbl_ikan.setHorizontalHeaderLabels([
            "ID", "Jenis", "Varietas", "Warna", "Ukuran",
            "Grade", "Stok", "Kesehatan", "Kolam", "Harga",
        ])
        self.tbl_ikan.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_ikan.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_ikan.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_ikan.setAlternatingRowColors(True)
        layout.addWidget(self.tbl_ikan)
        return w

    def _refresh_ikan(self) -> None:
        try:
            semua = self.stok_svc.load_semua_ikan()
            self.tbl_ikan.setRowCount(len(semua))
            for row, ikan in enumerate(semua):
                harga = ikan.hitung_harga_jual()
                vals = [
                    ikan.id_ikan, ikan.jenis(), ikan.varietas, ikan.warna,
                    f"{ikan.ukuran_cm} cm", ikan.grade,
                    str(ikan.jumlah_stok), ikan.status_kesehatan,
                    ikan.kolam_id, f"Rp {harga:,}".replace(",", "."),
                ]
                for col, v in enumerate(vals):
                    self.tbl_ikan.setItem(row, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _selected_ikan_id(self) -> str | None:
        row = self.tbl_ikan.currentRow()
        if row < 0:
            return None
        item = self.tbl_ikan.item(row, 0)
        return item.text() if item else None

    def _tambah_ikan(self) -> None:
        dlg = IkanDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            try:
                new_id = self.stok_svc.generate_id(data["jenis"])
                data["id"] = new_id
                ikan = IkanHias.from_dict(data)
                self.stok_svc.tambah_ikan(ikan)
                self._refresh_ikan()
                self.statusBar().showMessage(f"Ikan {new_id} berhasil ditambahkan")
            except HiaskanBaseError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _edit_ikan(self) -> None:
        ikan_id = self._selected_ikan_id()
        if not ikan_id:
            QMessageBox.information(self, "Info", "Pilih ikan yang ingin diedit")
            return
        try:
            ikan = self.stok_svc.cari_ikan(ikan_id)
            if not ikan:
                return
            dlg = IkanDialog(self, data=ikan.to_dict())
            if dlg.exec():
                data = dlg.get_data()
                data["id"] = ikan_id
                updated = IkanHias.from_dict(data)
                self.stok_svc.update_ikan(updated)
                self._refresh_ikan()
                self.statusBar().showMessage(f"Ikan {ikan_id} berhasil diperbarui")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _hapus_ikan(self) -> None:
        ikan_id = self._selected_ikan_id()
        if not ikan_id:
            QMessageBox.information(self, "Info", "Pilih ikan yang ingin dihapus")
            return
        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Yakin ingin menghapus ikan {ikan_id}?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.stok_svc.hapus_ikan(ikan_id)
            self._refresh_ikan()
            self.statusBar().showMessage(f"Ikan {ikan_id} berhasil dihapus")

    # ══════════════════ Tab: Kolam ══════════════════

    def _tab_kolam(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        tb = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Kolam")
        btn_tambah.clicked.connect(self._tambah_kolam)
        btn_edit = QPushButton("Edit")
        btn_edit.setProperty("class", "secondary")
        btn_edit.clicked.connect(self._edit_kolam)
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setProperty("class", "danger")
        btn_hapus.clicked.connect(self._hapus_kolam)
        btn_cek = QPushButton("Cek Kualitas Air")
        btn_cek.clicked.connect(self._cek_kualitas_air)
        tb.addWidget(btn_tambah)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_hapus)
        tb.addWidget(btn_cek)
        tb.addStretch()
        layout.addLayout(tb)

        self.tbl_kolam = QTableWidget(0, 9)
        self.tbl_kolam.setHorizontalHeaderLabels([
            "ID", "Nama", "Kapasitas", "Jenis", "Jumlah",
            "pH", "Suhu", "Oksigen", "Amonia",
        ])
        self.tbl_kolam.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_kolam.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_kolam.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_kolam.setAlternatingRowColors(True)
        layout.addWidget(self.tbl_kolam)
        return w

    def _refresh_kolam(self) -> None:
        try:
            semua = self.kolam_svc.load_semua_kolam()
            self.tbl_kolam.setRowCount(len(semua))
            for row, k in enumerate(semua):
                air = k.kualitas_air
                vals = [
                    k.id_kolam, k.nama, str(k.kapasitas), k.jenis_ikan,
                    str(k.jumlah_ikan), str(air.ph), f"{air.suhu}\u00b0C",
                    str(air.oksigen), str(air.amonia),
                ]
                for col, v in enumerate(vals):
                    self.tbl_kolam.setItem(row, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _selected_kolam_id(self) -> str | None:
        row = self.tbl_kolam.currentRow()
        if row < 0:
            return None
        item = self.tbl_kolam.item(row, 0)
        return item.text() if item else None

    def _tambah_kolam(self) -> None:
        dlg = KolamDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            try:
                new_id = self.kolam_svc.generate_id()
                kolam = Kolam.from_dict({"id": new_id, **data})
                self.kolam_svc.tambah_kolam(kolam)
                self._refresh_kolam()
                self.statusBar().showMessage(f"Kolam {new_id} berhasil ditambahkan")
            except HiaskanBaseError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _edit_kolam(self) -> None:
        kolam_id = self._selected_kolam_id()
        if not kolam_id:
            QMessageBox.information(self, "Info", "Pilih kolam yang ingin diedit")
            return
        try:
            kolam = self.kolam_svc.cari_kolam(kolam_id)
            if not kolam:
                return
            dlg = KolamDialog(self, data=kolam.to_dict())
            if dlg.exec():
                data = dlg.get_data()
                updated = Kolam.from_dict({"id": kolam_id, **data})
                self.kolam_svc.update_kolam(updated)
                self._refresh_kolam()
                self.statusBar().showMessage(f"Kolam {kolam_id} berhasil diperbarui")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _hapus_kolam(self) -> None:
        kolam_id = self._selected_kolam_id()
        if not kolam_id:
            QMessageBox.information(self, "Info", "Pilih kolam yang ingin dihapus")
            return
        reply = QMessageBox.question(
            self, "Konfirmasi", f"Yakin ingin menghapus kolam {kolam_id}?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.kolam_svc.hapus_kolam(kolam_id)
            self._refresh_kolam()
            self.statusBar().showMessage(f"Kolam {kolam_id} berhasil dihapus")

    def _cek_kualitas_air(self) -> None:
        kolam_id = self._selected_kolam_id()
        if not kolam_id:
            QMessageBox.information(self, "Info", "Pilih kolam untuk dicek")
            return
        try:
            kolam = self.kolam_svc.cari_kolam(kolam_id)
            if kolam:
                kolam.cek_kualitas_air()
                QMessageBox.information(
                    self, "Kualitas Air",
                    f"Kolam {kolam_id}: Semua parameter air AMAN",
                )
        except KualitasAirBurukError as e:
            QMessageBox.warning(
                self, "Kualitas Air Buruk!",
                f"PERINGATAN: {e}\n\n"
                f"Kolam {kolam_id} tidak aman untuk ikan!",
            )
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    # ══════════════════ Tab: Pakan ══════════════════

    def _tab_pakan(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        tb = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Pakan")
        btn_tambah.clicked.connect(self._tambah_pakan)
        btn_edit = QPushButton("Edit")
        btn_edit.setProperty("class", "secondary")
        btn_edit.clicked.connect(self._edit_pakan)
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setProperty("class", "danger")
        btn_hapus.clicked.connect(self._hapus_pakan)
        tb.addWidget(btn_tambah)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_hapus)
        tb.addStretch()
        layout.addLayout(tb)

        self.tbl_pakan = QTableWidget(0, 7)
        self.tbl_pakan.setHorizontalHeaderLabels([
            "ID", "Nama", "Jenis", "Merek", "Stok (g)",
            "Harga/kg", "Kadaluarsa",
        ])
        self.tbl_pakan.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_pakan.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_pakan.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_pakan.setAlternatingRowColors(True)
        layout.addWidget(self.tbl_pakan)
        return w

    def _refresh_pakan(self) -> None:
        try:
            path = self.data_dir / "pakan.json"
            data = FileHandler.load_json(path)
            self.tbl_pakan.setRowCount(len(data))
            for row, d in enumerate(data):
                vals = [
                    d.get("id", ""), d.get("nama", ""), d.get("jenis", ""),
                    d.get("merek", ""), str(d.get("stok_gram", 0)),
                    f"Rp {d.get('harga_per_kg', 0):,}".replace(",", "."),
                    d.get("tanggal_kadaluarsa", ""),
                ]
                for col, v in enumerate(vals):
                    self.tbl_pakan.setItem(row, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _pakan_generate_id(self) -> str:
        path = self.data_dir / "pakan.json"
        data = FileHandler.load_json(path)
        if not data:
            return "PKN001"
        nums = []
        for d in data:
            try:
                nums.append(int(d["id"][3:]))
            except (ValueError, KeyError, IndexError):
                continue
        return f"PKN{max(nums, default=0) + 1:03d}"

    def _tambah_pakan(self) -> None:
        dlg = PakanDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            new_id = self._pakan_generate_id()
            data["id"] = new_id
            try:
                path = self.data_dir / "pakan.json"
                FileHandler.tambah_json(path, data)
                self._refresh_pakan()
                self.statusBar().showMessage(f"Pakan {new_id} berhasil ditambahkan")
            except HiaskanBaseError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _edit_pakan(self) -> None:
        row = self.tbl_pakan.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih pakan yang ingin diedit")
            return
        pakan_id = self.tbl_pakan.item(row, 0).text()
        try:
            path = self.data_dir / "pakan.json"
            rec = FileHandler.cari_json(path, pakan_id)
            if not rec:
                return
            dlg = PakanDialog(self, data=rec)
            if dlg.exec():
                updated = dlg.get_data()
                updated["id"] = pakan_id
                FileHandler.update_json(path, pakan_id, updated)
                self._refresh_pakan()
                self.statusBar().showMessage(f"Pakan {pakan_id} berhasil diperbarui")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _hapus_pakan(self) -> None:
        row = self.tbl_pakan.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih pakan yang ingin dihapus")
            return
        pakan_id = self.tbl_pakan.item(row, 0).text()
        reply = QMessageBox.question(
            self, "Konfirmasi", f"Yakin ingin menghapus pakan {pakan_id}?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            path = self.data_dir / "pakan.json"
            FileHandler.hapus_json(path, pakan_id)
            self._refresh_pakan()
            self.statusBar().showMessage(f"Pakan {pakan_id} berhasil dihapus")

    # ══════════════════ Tab: Pemijahan ══════════════════

    def _tab_pemijahan(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        tb = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Pemijahan")
        btn_tambah.clicked.connect(self._tambah_pemijahan)
        btn_edit = QPushButton("Edit")
        btn_edit.setProperty("class", "secondary")
        btn_edit.clicked.connect(self._edit_pemijahan)
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setProperty("class", "danger")
        btn_hapus.clicked.connect(self._hapus_pemijahan)
        tb.addWidget(btn_tambah)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_hapus)
        tb.addStretch()
        layout.addLayout(tb)

        self.tbl_pijah = QTableWidget(0, 9)
        self.tbl_pijah.setHorizontalHeaderLabels([
            "ID", "Kolam", "Jenis", "Tgl Pijah", "Telur",
            "Menetas", "Larva Hidup", "% Penetasan", "Status",
        ])
        self.tbl_pijah.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_pijah.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_pijah.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_pijah.setAlternatingRowColors(True)
        layout.addWidget(self.tbl_pijah)
        return w

    def _refresh_pemijahan(self) -> None:
        try:
            path = self.data_dir / "pemijahan.json"
            data = FileHandler.load_json(path)
            self.tbl_pijah.setRowCount(len(data))
            for row, d in enumerate(data):
                p = Pemijahan.from_dict(d)
                vals = [
                    p.id_pemijahan, p.kolam_id, p.jenis_ikan,
                    p.tanggal_pijah, str(p.jumlah_telur),
                    str(p.jumlah_menetas), str(p.jumlah_larva_hidup),
                    f"{p.tingkat_penetasan}%", p.status,
                ]
                for col, v in enumerate(vals):
                    self.tbl_pijah.setItem(row, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _pijah_generate_id(self) -> str:
        path = self.data_dir / "pemijahan.json"
        data = FileHandler.load_json(path)
        if not data:
            return "PIJ001"
        nums = []
        for d in data:
            try:
                nums.append(int(d["id"][3:]))
            except (ValueError, KeyError, IndexError):
                continue
        return f"PIJ{max(nums, default=0) + 1:03d}"

    def _tambah_pemijahan(self) -> None:
        dlg = PemijahanDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            new_id = self._pijah_generate_id()
            data["id"] = new_id
            try:
                path = self.data_dir / "pemijahan.json"
                FileHandler.tambah_json(path, data)
                self._refresh_pemijahan()
                self.statusBar().showMessage(f"Pemijahan {new_id} berhasil dicatat")
            except HiaskanBaseError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _edit_pemijahan(self) -> None:
        row = self.tbl_pijah.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih data pemijahan")
            return
        pijah_id = self.tbl_pijah.item(row, 0).text()
        try:
            path = self.data_dir / "pemijahan.json"
            rec = FileHandler.cari_json(path, pijah_id)
            if not rec:
                return
            dlg = PemijahanDialog(self, data=rec)
            if dlg.exec():
                updated = dlg.get_data()
                updated["id"] = pijah_id
                FileHandler.update_json(path, pijah_id, updated)
                self._refresh_pemijahan()
                self.statusBar().showMessage(f"Pemijahan {pijah_id} diperbarui")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _hapus_pemijahan(self) -> None:
        row = self.tbl_pijah.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih data pemijahan")
            return
        pijah_id = self.tbl_pijah.item(row, 0).text()
        reply = QMessageBox.question(
            self, "Konfirmasi", f"Hapus pemijahan {pijah_id}?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            path = self.data_dir / "pemijahan.json"
            FileHandler.hapus_json(path, pijah_id)
            self._refresh_pemijahan()
            self.statusBar().showMessage(f"Pemijahan {pijah_id} dihapus")

    # ══════════════════ Tab: Penjualan ══════════════════

    def _tab_penjualan(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # Form penjualan baru
        grp = QGroupBox("Penjualan Baru")
        grp_layout = QVBoxLayout(grp)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Pelanggan:"))
        self.jual_pelanggan = QComboBox()
        self.jual_pelanggan.setMinimumWidth(200)
        row1.addWidget(self.jual_pelanggan)
        row1.addStretch()
        grp_layout.addLayout(row1)

        # Item list
        self.tbl_jual_items = QTableWidget(0, 5)
        self.tbl_jual_items.setHorizontalHeaderLabels([
            "ID Ikan", "Jenis", "Varietas", "Jumlah", "Harga Satuan",
        ])
        self.tbl_jual_items.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_jual_items.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_jual_items.setMaximumHeight(150)
        grp_layout.addWidget(self.tbl_jual_items)

        row2 = QHBoxLayout()
        btn_add_item = QPushButton("+ Tambah Item")
        btn_add_item.clicked.connect(self._tambah_item_jual)
        btn_clear = QPushButton("Bersihkan")
        btn_clear.setProperty("class", "secondary")
        btn_clear.clicked.connect(self._clear_jual)
        btn_proses = QPushButton("Proses Penjualan")
        btn_proses.clicked.connect(self._proses_penjualan)
        row2.addWidget(btn_add_item)
        row2.addWidget(btn_clear)
        row2.addStretch()
        row2.addWidget(btn_proses)
        grp_layout.addLayout(row2)

        layout.addWidget(grp)

        # Riwayat
        lbl = QLabel("Riwayat Penjualan")
        lbl.setProperty("class", "subheading")
        layout.addWidget(lbl)

        self.tbl_riwayat = QTableWidget(0, 8)
        self.tbl_riwayat.setHorizontalHeaderLabels([
            "ID Transaksi", "Tanggal", "Pelanggan", "Ikan",
            "Varietas", "Jumlah", "Harga", "Subtotal",
        ])
        self.tbl_riwayat.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_riwayat.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_riwayat.setAlternatingRowColors(True)
        layout.addWidget(self.tbl_riwayat)
        return w

    def _refresh_penjualan(self) -> None:
        # Refresh pelanggan combo
        self.jual_pelanggan.clear()
        try:
            pelanggan = self.jual_svc.load_pelanggan()
            for p in pelanggan:
                self.jual_pelanggan.addItem(
                    f"{p.id_pelanggan} - {p.nama}", p.id_pelanggan,
                )
        except HiaskanBaseError:
            pass

        # Refresh riwayat
        try:
            rows = self.jual_svc.load_riwayat()
            self.tbl_riwayat.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                display = [
                    row_data[0] if len(row_data) > 0 else "",  # id
                    row_data[1] if len(row_data) > 1 else "",  # tanggal
                    row_data[3] if len(row_data) > 3 else "",  # pelanggan
                    row_data[5] if len(row_data) > 5 else "",  # jenis
                    row_data[6] if len(row_data) > 6 else "",  # varietas
                    row_data[7] if len(row_data) > 7 else "",  # jumlah
                    f"Rp {int(row_data[8]):,}".replace(",", ".") if len(row_data) > 8 and row_data[8].isdigit() else "",
                    f"Rp {int(row_data[9]):,}".replace(",", ".") if len(row_data) > 9 and row_data[9].isdigit() else "",
                ]
                for col, v in enumerate(display):
                    self.tbl_riwayat.setItem(row_idx, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error: {e}")

        self._jual_items: list[dict] = []
        self.tbl_jual_items.setRowCount(0)

    def _tambah_item_jual(self) -> None:
        try:
            semua = self.stok_svc.load_semua_ikan()
            ikan_data = [i.to_dict() for i in semua if i.status_kesehatan == "sehat"]
            if not ikan_data:
                QMessageBox.information(self, "Info", "Tidak ada ikan sehat tersedia")
                return
            dlg = PenjualanItemDialog(ikan_data, self)
            if dlg.exec():
                item = dlg.get_data()
                if not hasattr(self, "_jual_items"):
                    self._jual_items = []
                self._jual_items.append(item)
                # Update table
                row = self.tbl_jual_items.rowCount()
                self.tbl_jual_items.setRowCount(row + 1)
                for col, v in enumerate([
                    item["ikan_id"], item["jenis_ikan"],
                    item["varietas"], str(item["jumlah"]), "-",
                ]):
                    self.tbl_jual_items.setItem(row, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _clear_jual(self) -> None:
        self._jual_items = []
        self.tbl_jual_items.setRowCount(0)

    def _proses_penjualan(self) -> None:
        if not hasattr(self, "_jual_items") or not self._jual_items:
            QMessageBox.information(self, "Info", "Tambahkan item terlebih dahulu")
            return

        pel_id = self.jual_pelanggan.currentData()
        if not pel_id:
            QMessageBox.information(self, "Info", "Pilih pelanggan")
            return

        try:
            pel = self.jual_svc.cari_pelanggan(pel_id)
            items = [
                ItemPenjualan(
                    ikan_id=it["ikan_id"],
                    jenis_ikan=it["jenis_ikan"],
                    varietas=it["varietas"],
                    jumlah=it["jumlah"],
                )
                for it in self._jual_items
            ]
            trx_id = self.jual_svc.generate_id_penjualan()
            penjualan = Penjualan(
                id_penjualan=trx_id,
                pelanggan_id=pel_id,
                pelanggan_nama=pel.nama if pel else "",
                items=items,
            )
            result = self.jual_svc.proses_penjualan(penjualan)
            QMessageBox.information(
                self, "Sukses",
                f"Penjualan {trx_id} berhasil!\n"
                f"Total: Rp {result.total:,}".replace(",", "."),
            )
            self._refresh_penjualan()
            self._refresh_ikan()
        except StokIkanTidakCukupError as e:
            QMessageBox.warning(
                self, "Stok Tidak Cukup!",
                f"GAGAL: {e}\n\nKurangi jumlah atau pilih ikan lain.",
            )
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    # ══════════════════ Tab: Pelanggan ══════════════════

    def _tab_pelanggan(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        tb = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Pelanggan")
        btn_tambah.clicked.connect(self._tambah_pelanggan)
        btn_edit = QPushButton("Edit")
        btn_edit.setProperty("class", "secondary")
        btn_edit.clicked.connect(self._edit_pelanggan)
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setProperty("class", "danger")
        btn_hapus.clicked.connect(self._hapus_pelanggan)
        tb.addWidget(btn_tambah)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_hapus)
        tb.addStretch()
        layout.addLayout(tb)

        self.tbl_pelanggan = QTableWidget(0, 5)
        self.tbl_pelanggan.setHorizontalHeaderLabels([
            "ID", "Nama", "Telepon", "Transaksi", "Total Beli",
        ])
        self.tbl_pelanggan.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbl_pelanggan.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_pelanggan.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_pelanggan.setAlternatingRowColors(True)
        layout.addWidget(self.tbl_pelanggan)
        return w

    def _refresh_pelanggan(self) -> None:
        try:
            semua = self.jual_svc.load_pelanggan()
            self.tbl_pelanggan.setRowCount(len(semua))
            for row, p in enumerate(semua):
                vals = [
                    p.id_pelanggan, p.nama, p.telepon,
                    str(p.total_transaksi),
                    f"Rp {p.total_pembelian:,}".replace(",", "."),
                ]
                for col, v in enumerate(vals):
                    self.tbl_pelanggan.setItem(row, col, QTableWidgetItem(v))
        except HiaskanBaseError as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _tambah_pelanggan(self) -> None:
        dlg = PelangganDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            new_id = self.jual_svc.generate_id_pelanggan()
            pel = Pelanggan(id_pelanggan=new_id, **data)
            try:
                self.jual_svc.tambah_pelanggan(pel)
                self._refresh_pelanggan()
                self.statusBar().showMessage(f"Pelanggan {new_id} ditambahkan")
            except HiaskanBaseError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _edit_pelanggan(self) -> None:
        row = self.tbl_pelanggan.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih pelanggan")
            return
        pel_id = self.tbl_pelanggan.item(row, 0).text()
        try:
            pel = self.jual_svc.cari_pelanggan(pel_id)
            if not pel:
                return
            dlg = PelangganDialog(self, data=pel.to_dict())
            if dlg.exec():
                data = dlg.get_data()
                updated = Pelanggan(
                    id_pelanggan=pel_id,
                    total_transaksi=pel.total_transaksi,
                    total_pembelian=pel.total_pembelian,
                    **data,
                )
                semua = self.jual_svc.load_pelanggan()
                for i, p in enumerate(semua):
                    if p.id_pelanggan == pel_id:
                        semua[i] = updated
                        break
                self.jual_svc.simpan_pelanggan(semua)
                self._refresh_pelanggan()
                self.statusBar().showMessage(f"Pelanggan {pel_id} diperbarui")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _hapus_pelanggan(self) -> None:
        row = self.tbl_pelanggan.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih pelanggan")
            return
        pel_id = self.tbl_pelanggan.item(row, 0).text()
        reply = QMessageBox.question(
            self, "Konfirmasi", f"Hapus pelanggan {pel_id}?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            FileHandler.hapus_json(self.data_dir / "pelanggan.json", pel_id)
            self._refresh_pelanggan()
            self.statusBar().showMessage(f"Pelanggan {pel_id} dihapus")

    # ══════════════════ Tab: Laporan ══════════════════

    def _tab_laporan(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        lbl = QLabel("Generate Laporan")
        lbl.setProperty("class", "subheading")
        layout.addWidget(lbl)

        grid = QGridLayout()
        reports = [
            ("Laporan Stok", "Ekspor data stok ikan saat ini ke CSV", self._gen_lap_stok),
            ("Laporan Pendapatan", "Ringkasan pendapatan dan stok ke TXT", self._gen_lap_pendapatan),
            ("Laporan Mortalitas", "Data ikan sakit/mati/karantina ke CSV", self._gen_lap_mortalitas),
            ("Laporan Pakan", "Stok pakan saat ini ke CSV", self._gen_lap_pakan),
            ("Laporan Pertumbuhan", "Data pemijahan dan penetasan ke CSV", self._gen_lap_pertumbuhan),
        ]
        for i, (title, desc, handler) in enumerate(reports):
            grp = QGroupBox(title)
            gl = QVBoxLayout(grp)
            gl.addWidget(QLabel(desc))
            btn = QPushButton("Generate")
            btn.clicked.connect(handler)
            gl.addWidget(btn)
            grid.addWidget(grp, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()
        return w

    def _gen_lap_stok(self) -> None:
        try:
            path = self.laporan_svc.laporan_stok()
            QMessageBox.information(self, "Sukses", f"Laporan stok disimpan:\n{path}")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _gen_lap_pendapatan(self) -> None:
        try:
            path = self.laporan_svc.laporan_pendapatan()
            QMessageBox.information(self, "Sukses", f"Laporan pendapatan disimpan:\n{path}")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _gen_lap_mortalitas(self) -> None:
        try:
            path = self.laporan_svc.laporan_mortalitas()
            QMessageBox.information(self, "Sukses", f"Laporan mortalitas disimpan:\n{path}")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _gen_lap_pakan(self) -> None:
        try:
            path = self.laporan_svc.laporan_pakan()
            QMessageBox.information(self, "Sukses", f"Laporan pakan disimpan:\n{path}")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _gen_lap_pertumbuhan(self) -> None:
        try:
            path = self.laporan_svc.laporan_pertumbuhan()
            QMessageBox.information(self, "Sukses", f"Laporan pertumbuhan disimpan:\n{path}")
        except HiaskanBaseError as e:
            QMessageBox.warning(self, "Error", str(e))

    # ══════════════════ Tab change handler ══════════════════

    def _on_tab_changed(self, index: int) -> None:
        tab_name = self.tabs.tabText(index)
        refreshers = {
            "Dashboard": self._refresh_dashboard,
            "Ikan": self._refresh_ikan,
            "Kolam": self._refresh_kolam,
            "Pakan": self._refresh_pakan,
            "Pemijahan": self._refresh_pemijahan,
            "Penjualan": self._refresh_penjualan,
            "Pelanggan": self._refresh_pelanggan,
        }
        refresher = refreshers.get(tab_name)
        if refresher:
            refresher()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        QTimer.singleShot(100, self._refresh_dashboard)
