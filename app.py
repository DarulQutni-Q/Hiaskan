"""
Hiaskan — Sistem Pembibitan Ikan Hias & Penjualan.

Aplikasi web interaktif berbasis Streamlit. Data tersimpan di folder data/
(JSON/CSV) dan dibaca langsung oleh services setiap kali ada interaksi —
sehingga tampilan selalu sinkron dengan data terbaru.

Menjalankan:  streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

import ui.components as comp
from ui import (
    dashboard,
    ikan,
    kolam,
    laporan,
    pakan,
    pelanggan,
    pemijahan,
    penjualan,
)


def main() -> None:
    st.set_page_config(
        page_title="Hiaskan",
        page_icon=":material/water_drop:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    comp.inject_css()

    with st.sidebar:
        st.markdown('<p class="hs-brand">Hiaskan</p>', unsafe_allow_html=True)
        st.caption("Sistem Pembibitan Ikan Hias & Penjualan")
        st.divider()

    nav = st.navigation(
        {
            "Menu": [
                st.Page(dashboard.render, title="Dashboard", url_path="dashboard", icon=":material/space_dashboard:", default=True),
                st.Page(ikan.render, title="Ikan", url_path="ikan", icon=":material/phishing:"),
                st.Page(kolam.render, title="Kolam", url_path="kolam", icon=":material/water_drop:"),
                st.Page(pakan.render, title="Pakan", url_path="pakan", icon=":material/egg:"),
                st.Page(pemijahan.render, title="Pemijahan", url_path="pemijahan", icon=":material/egg_alt:"),
                st.Page(penjualan.render, title="Penjualan", url_path="penjualan", icon=":material/receipt_long:"),
                st.Page(pelanggan.render, title="Pelanggan", url_path="pelanggan", icon=":material/group:"),
                st.Page(laporan.render, title="Laporan", url_path="laporan", icon=":material/description:"),
            ]
        }
    )

    with st.sidebar:
        st.caption(f"Data: `{comp.DATA_DIR}`")

    nav.run()

    comp.flush_toast()


if __name__ == "__main__":
    if st.runtime.exists():
        main()
    else:
        print("Hiaskan tidak bisa dijalankan dengan `python app.py`.")
        print("Jalankan dengan perintah:  streamlit run app.py")
