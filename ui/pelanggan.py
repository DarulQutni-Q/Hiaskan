"""
Halaman Pelanggan — CRUD pelanggan dan ringkasan nilai pembelian.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import ui.components as comp
from exceptions import HiaskanBaseError
from models.pelanggan import Pelanggan
from services.file_handler import FileHandler

_P = "pel_"

FILE = comp.DATA_DIR / "pelanggan.json"


def _seed(fields: dict, marker: str, nilai: str) -> None:
    """Isi session_state hanya jika marker belum cocok — tidak menimpa
    nilai widget yang sedang diedit oleh user."""
    if st.session_state.get(marker) == nilai:
        return
    for k, v in fields.items():
        st.session_state[_P + k] = v
    st.session_state[marker] = nilai


def _form_pelanggan() -> None:
    st.text_input("Nama", key=_P + "nama")
    c1, c2 = st.columns(2)
    c1.text_input("Telepon", key=_P + "telepon")
    c2.text_input("Alamat", key=_P + "alamat")


@st.dialog("Tambah Pelanggan")
def dlg_tambah() -> None:
    _seed({"nama": "", "telepon": "", "alamat": ""}, _P + "_seed_tambah", "open")
    _form_pelanggan()
    if st.button("Simpan", type="primary", use_container_width=True):
        try:
            new_id = comp.jual_svc().generate_id_pelanggan()
            comp.jual_svc().tambah_pelanggan(Pelanggan(id_pelanggan=new_id, **_baca()))
            comp.sukses_rerun(f"Pelanggan {new_id} ditambahkan")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Edit Pelanggan")
def dlg_edit(data) -> None:
    pilihan = {f"{p.id_pelanggan} — {p.nama}": p.id_pelanggan for p in data}
    picked = st.selectbox("Pilih pelanggan", list(pilihan), filter_mode=None)
    pel = next(p for p in data if p.id_pelanggan == pilihan[picked])
    _seed({"nama": pel.nama, "telepon": pel.telepon, "alamat": pel.alamat},
          _P + "_seed_edit", pel.id_pelanggan)
    _form_pelanggan()
    if st.button("Simpan Perubahan", type="primary", use_container_width=True):
        try:
            updated = Pelanggan(
                id_pelanggan=pel.id_pelanggan,
                total_transaksi=pel.total_transaksi,
                total_pembelian=pel.total_pembelian,
                **_baca(),
            )
            semua = comp.jual_svc().load_pelanggan()
            comp.jual_svc().simpan_pelanggan([
                updated if p.id_pelanggan == pel.id_pelanggan else p for p in semua
            ])
            comp.sukses_rerun(f"Pelanggan {pel.id_pelanggan} diperbarui")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Hapus Pelanggan")
def dlg_hapus(data) -> None:
    pilihan = {f"{p.id_pelanggan} — {p.nama}": p.id_pelanggan for p in data}
    picked = st.selectbox("Pilih pelanggan", list(pilihan), filter_mode=None)
    pel = next(p for p in data if p.id_pelanggan == pilihan[picked])
    st.caption(f"{pel.total_transaksi} transaksi • {comp.rupiah(pel.total_pembelian)}")
    c1, c2 = st.columns(2)
    if c1.button("Ya, Hapus", type="primary", use_container_width=True):
        FileHandler.hapus_json(FILE, pel.id_pelanggan)
        comp.sukses_rerun(f"Pelanggan {pel.id_pelanggan} dihapus")
    if c2.button("Batal", use_container_width=True):
        st.rerun()


def _baca() -> dict:
    return {
        "nama": st.session_state[_P + "nama"],
        "telepon": st.session_state[_P + "telepon"],
        "alamat": st.session_state[_P + "alamat"],
    }


def render() -> None:
    comp.page_header(
        "Pelanggan",
        "Kelola data pembeli dan pantau loyalitas transaksi.",
    )

    svc = comp.jual_svc()
    data = svc.load_pelanggan()

    c = st.columns(3)
    with c[0]:
        comp.kpi("Total Pelanggan", str(len(data)))
    with c[1]:
        aktif = sum(1 for p in data if p.total_transaksi > 0)
        comp.kpi("Pelanggan Aktif", str(aktif))
    with c[2]:
        comp.kpi("Total Pembelian", comp.rupiah(sum(p.total_pembelian for p in data)))

    if data:
        rows = [
            {
                "ID": p.id_pelanggan,
                "Nama": p.nama,
                "Telepon": p.telepon or "—",
                "Alamat": p.alamat or "—",
                "Transaksi": p.total_transaksi,
                "Total Beli": p.total_pembelian,
            }
            for p in data
        ]
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            width="stretch",
            height=300,
            column_config={
                "Total Beli": st.column_config.NumberColumn("Total Beli", format="Rp %d"),
            },
        )
    else:
        st.caption("Belum ada pelanggan tercatat.")

    a1, a2, a3 = st.columns(3)
    if a1.button("+ Tambah Pelanggan", type="primary", use_container_width=True):
        st.session_state.pop(_P + "_seed_tambah", None)
        dlg_tambah()
    if a2.button("Edit Pelanggan", use_container_width=True, disabled=not data):
        st.session_state.pop(_P + "_seed_edit", None)
        dlg_edit(data)
    if a3.button("Hapus Pelanggan", use_container_width=True, disabled=not data):
        dlg_hapus(data)
