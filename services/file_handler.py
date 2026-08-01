"""
FileHandler — CRUD untuk file JSON dan CSV.

Operasi:
    - Membuat file awal jika belum ada
    - Membaca (load) data dari file
    - Menambah, mengubah, menghapus record
    - Menyimpan ulang tanpa kehilangan data (atomic write)
    - Mengekspor laporan ke CSV/TXT

Exception handling:
    - FileNotFoundError  → buat file baru dengan data kosong
    - json.JSONDecodeError → FileOperasiError (format rusak)
    - PermissionError     → FileOperasiError
    - OSError             → FileOperasiError
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from exceptions import FileOperasiError


class FileHandler:
    """Utility class untuk operasi baca/tulis file JSON dan CSV."""

    # ---------- JSON Operations ----------

    @staticmethod
    def load_json(filepath: str | Path) -> list[dict[str, Any]]:
        """Baca file JSON, kembalikan list of dict.

        Jika file tidak ditemukan, buat file kosong dan kembalikan [].
        Jika file rusak (format salah), lempar FileOperasiError.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            # Buat file awal kosong
            FileHandler.save_json(filepath, [])
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = [data]
            return data
        except json.JSONDecodeError as e:
            raise FileOperasiError(str(filepath), "baca", e)
        except PermissionError as e:
            raise FileOperasiError(str(filepath), "baca", e)
        except OSError as e:
            raise FileOperasiError(str(filepath), "baca", e)

    @staticmethod
    def save_json(filepath: str | Path, data: list[dict[str, Any]]) -> None:
        """Simpan data ke file JSON secara atomic.

        Menulis ke file temporary dulu, lalu rename — mencegah data hilang
        jika proses terganggu di tengah penulisan.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Atomic write: tulis ke temp file, lalu rename
            fd, tmp_path = tempfile.mkstemp(
                dir=filepath.parent, suffix=".tmp"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                shutil.move(tmp_path, filepath)
            except Exception:
                # Hapus temp file jika gagal
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise
        except PermissionError as e:
            raise FileOperasiError(str(filepath), "tulis", e)
        except OSError as e:
            raise FileOperasiError(str(filepath), "tulis", e)

    @staticmethod
    def tambah_json(filepath: str | Path, record: dict[str, Any]) -> None:
        """Tambah satu record ke file JSON."""
        data = FileHandler.load_json(filepath)
        data.append(record)
        FileHandler.save_json(filepath, data)

    @staticmethod
    def update_json(
        filepath: str | Path,
        record_id: str,
        updated: dict[str, Any],
        id_field: str = "id",
    ) -> bool:
        """Update satu record berdasarkan ID. Return True jika ditemukan."""
        data = FileHandler.load_json(filepath)
        for i, rec in enumerate(data):
            if rec.get(id_field) == record_id:
                data[i] = updated
                FileHandler.save_json(filepath, data)
                return True
        return False

    @staticmethod
    def hapus_json(
        filepath: str | Path,
        record_id: str,
        id_field: str = "id",
    ) -> bool:
        """Hapus satu record berdasarkan ID. Return True jika ditemukan."""
        data = FileHandler.load_json(filepath)
        new_data = [r for r in data if r.get(id_field) != record_id]
        if len(new_data) == len(data):
            return False
        FileHandler.save_json(filepath, new_data)
        return True

    @staticmethod
    def cari_json(
        filepath: str | Path,
        record_id: str,
        id_field: str = "id",
    ) -> dict[str, Any] | None:
        """Cari satu record berdasarkan ID."""
        data = FileHandler.load_json(filepath)
        for rec in data:
            if rec.get(id_field) == record_id:
                return rec
        return None

    # ---------- CSV Operations ----------

    @staticmethod
    def load_csv(filepath: str | Path) -> list[list[str]]:
        """Baca file CSV, kembalikan list of rows (tanpa header)."""
        filepath = Path(filepath)
        if not filepath.exists():
            return []
        try:
            with open(filepath, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            # Skip header jika ada
            if rows and rows[0] and not rows[0][0].startswith("20"):
                return rows[1:]
            return rows
        except PermissionError as e:
            raise FileOperasiError(str(filepath), "baca", e)
        except OSError as e:
            raise FileOperasiError(str(filepath), "baca", e)

    @staticmethod
    def save_csv(
        filepath: str | Path,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        """Tulis header + rows ke file CSV (overwrite)."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
        except PermissionError as e:
            raise FileOperasiError(str(filepath), "tulis", e)
        except OSError as e:
            raise FileOperasiError(str(filepath), "tulis", e)

    @staticmethod
    def append_csv(
        filepath: str | Path,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        """Tambah rows ke akhir file CSV. Buat file + header jika belum ada."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        file_exists = filepath.exists() and filepath.stat().st_size > 0
        try:
            with open(filepath, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(header)
                writer.writerows(rows)
        except PermissionError as e:
            raise FileOperasiError(str(filepath), "tulis", e)
        except OSError as e:
            raise FileOperasiError(str(filepath), "tulis", e)

    # ---------- TXT Export ----------

    @staticmethod
    def export_txt(filepath: str | Path, content: str) -> None:
        """Tulis laporan teks ke file TXT."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except (PermissionError, OSError) as e:
            raise FileOperasiError(str(filepath), "tulis", e)
