"""
Dialog forms untuk menambah/mengedit data pada GUI Hiaskan.

Setiap dialog menggunakan QFormLayout agar tampilan bersih dan konsisten.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QGroupBox,
    QLabel,
)
from PyQt6.QtCore import Qt


# ──────────────────────── helpers ────────────────────────

def _make_buttons() -> QDialogButtonBox:
    bb = QDialogButtonBox()
    bb.addButton("Simpan", QDialogButtonBox.ButtonRole.AcceptRole)
    bb.addButton("Batal", QDialogButtonBox.ButtonRole.RejectRole)
    return bb


def _combo(items: list[str], current: str = "") -> QComboBox:
    cb = QComboBox()
    cb.addItems(items)
    if current:
        idx = cb.findText(current, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            cb.setCurrentIndex(idx)
    return cb


def _double_spin(
    mn: float = 0, mx: float = 100, step: float = 0.1,
    decimals: int = 1, val: float = 0,
) -> QDoubleSpinBox:
    sb = QDoubleSpinBox()
    sb.setRange(mn, mx)
    sb.setSingleStep(step)
    sb.setDecimals(decimals)
    sb.setValue(val)
    return sb


def _spin(mn: int = 0, mx: int = 100_000, val: int = 0) -> QSpinBox:
    sb = QSpinBox()
    sb.setRange(mn, mx)
    sb.setValue(val)
    return sb


# ──────────────────────── IkanDialog ────────────────────────


class IkanDialog(QDialog):
    """Dialog untuk menambah atau mengedit data ikan hias."""

    def __init__(self, kolam_list: list[dict], parent=None, data: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self._edit_mode = data is not None
        self.setWindowTitle("Edit Ikan" if self._edit_mode else "Tambah Ikan")
        self.setMinimumWidth(420)

        form = QFormLayout()

        self.jenis = _combo(["Cupang", "Guppy", "Koi"], data.get("jenis", "") if data else "")
        self.varietas = QLineEdit(data.get("varietas", "") if data else "")
        self.warna = QLineEdit(data.get("warna", "") if data else "")
        self.kualitas_warna = _combo(
            ["premium", "bagus", "standar", "pudar"],
            data.get("kualitas_warna", "standar") if data else "standar",
        )
        self.ukuran_cm = _double_spin(0.1, 100.0, 0.5, 1, data.get("ukuran_cm", 3.0) if data else 3.0)
        self.umur_bulan = _spin(0, 120, data.get("umur_bulan", 1) if data else 1)
        self.grade = _combo(["A+", "A", "B", "C"], data.get("grade", "B") if data else "B")
        self.jumlah_stok = _spin(0, 10_000, data.get("jumlah_stok", 0) if data else 0)
        self.status_kesehatan = _combo(
            ["sehat", "sakit", "karantina", "mati"],
            data.get("status_kesehatan", "sehat") if data else "sehat",
        )
        
        # Kolam Dropdown
        self.kolam_id = QComboBox()
        self.kolam_id.addItem("-- Tidak ada kolam --", "")
        for k in kolam_list:
            self.kolam_id.addItem(f"{k.get('id', '')} - {k.get('nama', '')}", k.get('id', ''))
            
        if data and data.get("kolam_id"):
            idx = self.kolam_id.findData(data.get("kolam_id"))
            if idx >= 0:
                self.kolam_id.setCurrentIndex(idx)

        form.addRow("Jenis:", self.jenis)
        form.addRow("Varietas:", self.varietas)
        form.addRow("Warna:", self.warna)
        form.addRow("Kualitas Warna:", self.kualitas_warna)
        form.addRow("Ukuran (cm):", self.ukuran_cm)
        form.addRow("Umur (bulan):", self.umur_bulan)
        form.addRow("Grade:", self.grade)
        form.addRow("Jumlah Stok:", self.jumlah_stok)
        form.addRow("Status Kesehatan:", self.status_kesehatan)
        form.addRow("Kolam:", self.kolam_id)

        buttons = _make_buttons()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "jenis": self.jenis.currentText(),
            "varietas": self.varietas.text().strip(),
            "warna": self.warna.text().strip(),
            "kualitas_warna": self.kualitas_warna.currentText(),
            "ukuran_cm": self.ukuran_cm.value(),
            "umur_bulan": self.umur_bulan.value(),
            "grade": self.grade.currentText(),
            "jumlah_stok": self.jumlah_stok.value(),
            "status_kesehatan": self.status_kesehatan.currentText(),
            "kolam_id": self.kolam_id.currentData(),
        }


# ──────────────────────── KolamDialog ────────────────────────


class KolamDialog(QDialog):
    """Dialog untuk menambah atau mengedit data kolam."""

    def __init__(self, parent=None, data: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self._edit_mode = data is not None
        self.setWindowTitle("Edit Kolam" if self._edit_mode else "Tambah Kolam")
        self.setMinimumWidth(420)

        form = QFormLayout()

        self.nama = QLineEdit(data.get("nama", "") if data else "")
        self.kapasitas = _spin(1, 5000, data.get("kapasitas", 50) if data else 50)
        self.jenis_ikan = _combo(
            ["Cupang", "Guppy", "Koi", "Campuran"],
            data.get("jenis_ikan", "") if data else "",
        )
        self.jumlah_ikan = _spin(0, 5000, data.get("jumlah_ikan", 0) if data else 0)

        form.addRow("Nama Kolam:", self.nama)
        form.addRow("Kapasitas:", self.kapasitas)
        form.addRow("Jenis Ikan:", self.jenis_ikan)
        form.addRow("Jumlah Ikan:", self.jumlah_ikan)

        # Kualitas Air group
        air = data.get("kualitas_air", {}) if data else {}
        air_group = QGroupBox("Kualitas Air")
        air_form = QFormLayout()
        self.ph = _double_spin(0, 14, 0.1, 1, air.get("ph", 7.0))
        self.suhu = _double_spin(0, 50, 0.5, 1, air.get("suhu", 27.0))
        self.oksigen = _double_spin(0, 20, 0.1, 1, air.get("oksigen", 6.5))
        self.amonia = _double_spin(0, 1, 0.001, 3, air.get("amonia", 0.01))
        air_form.addRow("pH:", self.ph)
        air_form.addRow("Suhu (\u00b0C):", self.suhu)
        air_form.addRow("Oksigen (mg/L):", self.oksigen)
        air_form.addRow("Amonia (mg/L):", self.amonia)
        air_group.setLayout(air_form)

        buttons = _make_buttons()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(air_group)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "nama": self.nama.text().strip(),
            "kapasitas": self.kapasitas.value(),
            "jenis_ikan": self.jenis_ikan.currentText(),
            "jumlah_ikan": self.jumlah_ikan.value(),
            "kualitas_air": {
                "ph": self.ph.value(),
                "suhu": self.suhu.value(),
                "oksigen": self.oksigen.value(),
                "amonia": self.amonia.value(),
            },
        }


# ──────────────────────── PakanDialog ────────────────────────


class PakanDialog(QDialog):
    """Dialog untuk menambah atau mengedit data pakan."""

    def __init__(self, parent=None, data: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self._edit_mode = data is not None
        self.setWindowTitle("Edit Pakan" if self._edit_mode else "Tambah Pakan")
        self.setMinimumWidth(420)

        form = QFormLayout()

        self.nama = QLineEdit(data.get("nama", "") if data else "")
        self.jenis = _combo(
            ["pelet", "cacing", "artemia", "spirulina"],
            data.get("jenis", "pelet") if data else "pelet",
        )
        self.merek = QLineEdit(data.get("merek", "") if data else "")
        self.stok_gram = _double_spin(0, 100_000, 10, 1, data.get("stok_gram", 0) if data else 0)
        self.harga_per_kg = _spin(0, 10_000_000, data.get("harga_per_kg", 0) if data else 0)
        self.tanggal_beli = QLineEdit(data.get("tanggal_beli", "") if data else "")
        self.tanggal_beli.setPlaceholderText("YYYY-MM-DD")
        self.tanggal_kadaluarsa = QLineEdit(data.get("tanggal_kadaluarsa", "") if data else "")
        self.tanggal_kadaluarsa.setPlaceholderText("YYYY-MM-DD")

        form.addRow("Nama:", self.nama)
        form.addRow("Jenis:", self.jenis)
        form.addRow("Merek:", self.merek)
        form.addRow("Stok (gram):", self.stok_gram)
        form.addRow("Harga / kg (Rp):", self.harga_per_kg)
        form.addRow("Tanggal Beli:", self.tanggal_beli)
        form.addRow("Kadaluarsa:", self.tanggal_kadaluarsa)

        buttons = _make_buttons()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "nama": self.nama.text().strip(),
            "jenis": self.jenis.currentText(),
            "merek": self.merek.text().strip(),
            "stok_gram": self.stok_gram.value(),
            "harga_per_kg": self.harga_per_kg.value(),
            "tanggal_beli": self.tanggal_beli.text().strip(),
            "tanggal_kadaluarsa": self.tanggal_kadaluarsa.text().strip(),
        }


# ──────────────────────── PelangganDialog ────────────────────────


class PelangganDialog(QDialog):
    """Dialog untuk menambah atau mengedit data pelanggan."""

    def __init__(self, parent=None, data: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self._edit_mode = data is not None
        self.setWindowTitle("Edit Pelanggan" if self._edit_mode else "Tambah Pelanggan")
        self.setMinimumWidth(420)

        form = QFormLayout()

        self.nama = QLineEdit(data.get("nama", "") if data else "")
        self.telepon = QLineEdit(data.get("telepon", "") if data else "")
        self.alamat = QTextEdit()
        self.alamat.setPlainText(data.get("alamat", "") if data else "")
        self.alamat.setMaximumHeight(80)

        form.addRow("Nama:", self.nama)
        form.addRow("Telepon:", self.telepon)
        form.addRow("Alamat:", self.alamat)

        buttons = _make_buttons()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "nama": self.nama.text().strip(),
            "telepon": self.telepon.text().strip(),
            "alamat": self.alamat.toPlainText().strip(),
        }


# ──────────────────────── PemijahanDialog ────────────────────────


class PemijahanDialog(QDialog):
    """Dialog untuk menambah atau mengedit data pemijahan."""

    def __init__(self, kolam_list: list[dict], ikan_list: list[dict], parent=None, data: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self._edit_mode = data is not None
        self.setWindowTitle("Edit Pemijahan" if self._edit_mode else "Tambah Pemijahan")
        self.setMinimumWidth(420)

        form = QFormLayout()

        # Kolam Dropdown
        self.kolam_id = QComboBox()
        self.kolam_id.addItem("-- Pilih Kolam --", "")
        for k in kolam_list:
            self.kolam_id.addItem(f"{k.get('id', '')} - {k.get('nama', '')}", k.get('id', ''))
        if data and data.get("kolam_id"):
            idx = self.kolam_id.findData(data.get("kolam_id"))
            if idx >= 0:
                self.kolam_id.setCurrentIndex(idx)

        self.jenis_ikan = _combo(
            ["Cupang", "Guppy", "Koi"],
            data.get("jenis_ikan", "") if data else "",
        )

        # Induk Jantan Dropdown
        self.induk_jantan = QComboBox()
        self.induk_jantan.addItem("-- Pilih Induk Jantan --", "")
        for i in ikan_list:
            label = f"{i.get('id', '')} - {i.get('jenis', '')} {i.get('varietas', '')}"
            self.induk_jantan.addItem(label, i.get('id', ''))
        if data and data.get("induk_jantan_id"):
            idx = self.induk_jantan.findData(data.get("induk_jantan_id"))
            if idx >= 0:
                self.induk_jantan.setCurrentIndex(idx)

        # Induk Betina Dropdown
        self.induk_betina = QComboBox()
        self.induk_betina.addItem("-- Pilih Induk Betina --", "")
        for i in ikan_list:
            label = f"{i.get('id', '')} - {i.get('jenis', '')} {i.get('varietas', '')}"
            self.induk_betina.addItem(label, i.get('id', ''))
        if data and data.get("induk_betina_id"):
            idx = self.induk_betina.findData(data.get("induk_betina_id"))
            if idx >= 0:
                self.induk_betina.setCurrentIndex(idx)

        self.tgl_pijah = QLineEdit(data.get("tanggal_pijah", "") if data else "")
        self.tgl_pijah.setPlaceholderText("YYYY-MM-DD")
        self.jumlah_telur = _spin(0, 100_000, data.get("jumlah_telur", 0) if data else 0)
        self.jumlah_menetas = _spin(0, 100_000, data.get("jumlah_menetas", 0) if data else 0)
        self.jumlah_larva = _spin(0, 100_000, data.get("jumlah_larva_hidup", 0) if data else 0)
        self.tgl_panen = QLineEdit(data.get("tanggal_panen", "") if data else "")
        self.tgl_panen.setPlaceholderText("YYYY-MM-DD")
        self.status = _combo(
            ["berlangsung", "selesai", "gagal"],
            data.get("status", "berlangsung") if data else "berlangsung",
        )
        self.catatan = QTextEdit()
        self.catatan.setPlainText(data.get("catatan", "") if data else "")
        self.catatan.setMaximumHeight(80)

        form.addRow("Kolam:", self.kolam_id)
        form.addRow("Jenis Ikan:", self.jenis_ikan)
        form.addRow("Induk Jantan:", self.induk_jantan)
        form.addRow("Induk Betina:", self.induk_betina)
        form.addRow("Tanggal Pijah:", self.tgl_pijah)
        form.addRow("Jumlah Telur:", self.jumlah_telur)
        form.addRow("Jumlah Menetas:", self.jumlah_menetas)
        form.addRow("Larva Hidup:", self.jumlah_larva)
        form.addRow("Tanggal Panen:", self.tgl_panen)
        form.addRow("Status:", self.status)
        form.addRow("Catatan:", self.catatan)

        buttons = _make_buttons()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "kolam_id": self.kolam_id.currentData(),
            "jenis_ikan": self.jenis_ikan.currentText(),
            "induk_jantan_id": self.induk_jantan.currentData(),
            "induk_betina_id": self.induk_betina.currentData(),
            "tanggal_pijah": self.tgl_pijah.text().strip(),
            "jumlah_telur": self.jumlah_telur.value(),
            "jumlah_menetas": self.jumlah_menetas.value(),
            "jumlah_larva_hidup": self.jumlah_larva.value(),
            "tanggal_panen": self.tgl_panen.text().strip(),
            "status": self.status.currentText(),
            "catatan": self.catatan.toPlainText().strip(),
        }


# ──────────────────────── PenjualanDialog ────────────────────────


class PenjualanItemDialog(QDialog):
    """Dialog untuk menambah item penjualan (pilih ikan + jumlah)."""

    def __init__(self, ikan_list: list[dict], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tambah Item Penjualan")
        self.setMinimumWidth(420)

        form = QFormLayout()

        # Buat combo dari daftar ikan yang tersedia
        self.ikan_combo = QComboBox()
        self._ikan_data = ikan_list
        for ikan in ikan_list:
            label = (
                f"{ikan.get('id', '')} - {ikan.get('jenis', '')} "
                f"{ikan.get('varietas', '')} "
                f"(stok: {ikan.get('jumlah_stok', 0)}, "
                f"{ikan.get('status_kesehatan', '')})"
            )
            self.ikan_combo.addItem(label)

        self.jumlah = _spin(1, 10_000, 1)

        form.addRow("Pilih Ikan:", self.ikan_combo)
        form.addRow("Jumlah:", self.jumlah)

        buttons = _make_buttons()
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        idx = self.ikan_combo.currentIndex()
        ikan = self._ikan_data[idx] if 0 <= idx < len(self._ikan_data) else {}
        return {
            "ikan_id": ikan.get("id", ""),
            "jenis_ikan": ikan.get("jenis", ""),
            "varietas": ikan.get("varietas", ""),
            "jumlah": self.jumlah.value(),
        }
