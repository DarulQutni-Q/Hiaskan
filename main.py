"""
Hiaskan — Sistem Pembibitan Ikan Hias & Penjualan
Entry point utama aplikasi.

Menjalankan GUI PyQt6 dengan data dari folder data/.
"""

import sys
from pathlib import Path

# Tambahkan root project ke sys.path agar import modul lokal bekerja
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main() -> None:
    """Entry point utama — jalankan aplikasi GUI Hiaskan."""
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)

    app = QApplication(sys.argv)
    app.setApplicationName("Hiaskan")
    app.setApplicationDisplayName("Hiaskan — Sistem Pembibitan Ikan Hias")

    window = MainWindow(data_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
