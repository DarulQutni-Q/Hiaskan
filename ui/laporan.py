"""
Halaman Laporan — generate, pratinjau, dan unduh laporan.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import ui.components as comp
from exceptions import HiaskanBaseError

LAPORAN = [
    ("Laporan Stok", "Data stok ikan saat ini", "laporan_stok"),
    ("Laporan Pendapatan", "Ringkasan pendapatan dan stok", "laporan_pendapatan"),
    ("Laporan Mortalitas", "Ikan sakit / karantina / mati", "laporan_mortalitas"),
    ("Laporan Pakan", "Stok pakan saat ini", "laporan_pakan"),
    ("Laporan Pertumbuhan", "Data pemijahan dan penetasan", "laporan_pertumbuhan"),
]


def _gen(svc, key: str) -> str:
    return {
        "laporan_stok": svc.laporan_stok,
        "laporan_pendapatan": svc.laporan_pendapatan,
        "laporan_mortalitas": svc.laporan_mortalitas,
        "laporan_pakan": svc.laporan_pakan,
        "laporan_pertumbuhan": svc.laporan_pertumbuhan,
    }[key]()


def _mime(p: Path) -> str:
    return "text/csv" if p.suffix == ".csv" else "text/plain"


def _preview(path: str, nama: str, key: str) -> None:
    p = Path(path)
    with st.expander(f"Pratinjau {nama}", expanded=True):
        try:
            if p.suffix == ".csv":
                st.dataframe(pd.read_csv(p), hide_index=True, width="stretch")
            else:
                st.code(p.read_text(encoding="utf-8"), language=None)
        except Exception as e:  # noqa: BLE001
            st.error(f"Gagal membaca pratinjau: {e}")
    st.download_button(
        "Unduh File", data=p.read_bytes(), file_name=p.name,
        mime=_mime(p), key=f"dl_{key}", use_container_width=True,
    )


def _arsip() -> None:
    if not comp.LAPORAN_DIR.exists():
        return
    files = sorted(
        (p for p in comp.LAPORAN_DIR.iterdir() if p.is_file() and p.suffix),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    if not files:
        return
    comp.section("Arsip Laporan")
    pilihan = {p.name: p for p in files}
    picked = st.selectbox("File tersimpan di folder laporan/", list(pilihan), filter_mode=None)
    p = pilihan[picked]
    st.caption(f"{p.stat().st_size:,} bytes • terakhir diubah {datetime.fromtimestamp(p.stat().st_mtime):%d/%m/%Y %H:%M}")
    st.download_button(
        "Unduh File", data=p.read_bytes(), file_name=p.name,
        mime=_mime(p), key="dl_arsip", use_container_width=True,
    )


def render() -> None:
    comp.page_header(
        "Laporan",
        "Generate laporan dari data terkini — file juga tersimpan di folder laporan/.",
    )

    svc = comp.laporan_svc()

    for nama, desc, key in LAPORAN:
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        c1.markdown(f"**{nama}**")
        c1.caption(desc)
        if c2.button("Generate", key=f"gen_{key}", use_container_width=True):
            try:
                path = _gen(svc, key)
                st.session_state[f"lap_path_{key}"] = path
                comp.toast(f"Laporan {nama} berhasil dibuat")
                st.rerun()
            except HiaskanBaseError as e:
                st.error(str(e))
        path = st.session_state.get(f"lap_path_{key}")
        if path and Path(path).exists():
            _preview(path, nama, key)
        st.divider()

    _arsip()
