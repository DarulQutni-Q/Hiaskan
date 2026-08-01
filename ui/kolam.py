"""
Halaman Kolam — CRUD kolam, indikator kualitas air, dan kepadatan populasi.
"""

from __future__ import annotations

import streamlit as st

import ui.components as comp
from exceptions import HiaskanBaseError
from models.kolam import Kolam

_P = "kolam_"


def _seed(fields: dict, marker: str, nilai: str) -> None:
    """Isi session_state hanya jika marker belum cocok — tidak menimpa
    nilai widget yang sedang diedit/di-stepper oleh user."""
    if st.session_state.get(marker) == nilai:
        return
    for k, v in fields.items():
        st.session_state[_P + k] = v
    st.session_state[marker] = nilai


def _baca_field() -> dict:
    return {
        "nama": st.session_state[_P + "nama"],
        "kapasitas": int(st.session_state[_P + "kapasitas"]),
        "jenis_ikan": st.session_state[_P + "jenis_ikan"],
        "suhu_air": float(st.session_state[_P + "suhu_air"]),
    }


def _form_kolam() -> None:
    st.text_input("Nama Kolam", key=_P + "nama")
    c1, c2 = st.columns(2)
    c1.number_input("Kapasitas (ekor)", 1, 100000, key=_P + "kapasitas")
    c2.number_input("Suhu Air (°C)", 0.0, 45.0, step=0.5, key=_P + "suhu_air")
    st.text_input("Jenis Ikan", placeholder="contoh: Cupang / Campuran", key=_P + "jenis_ikan")
    st.caption("Jumlah ikan ter-sync otomatis dari stok di data ikan.")


@st.dialog("Tambah Kolam")
def dlg_tambah() -> None:
    _seed(
        {"nama": "", "kapasitas": 50, "jenis_ikan": "", "suhu_air": 27.0},
        _P + "_seed_tambah", "open",
    )
    _form_kolam()
    if st.button("Simpan", type="primary", use_container_width=True):
        try:
            new_id = comp.kolam_svc().generate_id()
            comp.kolam_svc().tambah_kolam(Kolam.from_dict({"id": new_id, **_baca_field()}))
            comp.sukses_rerun(f"Kolam {new_id} ditambahkan")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Edit Kolam")
def dlg_edit(data) -> None:
    pilihan = {f"{k.id_kolam} — {k.nama}": k.id_kolam for k in data}
    picked = st.selectbox("Pilih kolam", list(pilihan), filter_mode=None)
    kolam = next(k for k in data if k.id_kolam == pilihan[picked])
    _seed({
        "nama": kolam.nama,
        "kapasitas": kolam.kapasitas,
        "jenis_ikan": kolam.jenis_ikan,
        "suhu_air": kolam.suhu_air,
    }, _P + "_seed_edit", kolam.id_kolam)
    _form_kolam()
    if st.button("Simpan Perubahan", type="primary", use_container_width=True):
        try:
            comp.kolam_svc().update_kolam(
                Kolam.from_dict({"id": kolam.id_kolam, **_baca_field()})
            )
            comp.sukses_rerun(f"Kolam {kolam.id_kolam} diperbarui")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Hapus Kolam")
def dlg_hapus(data) -> None:
    pilihan = {f"{k.id_kolam} — {k.nama}": k.id_kolam for k in data}
    picked = st.selectbox("Pilih kolam", list(pilihan), filter_mode=None)
    kolam = next(k for k in data if k.id_kolam == pilihan[picked])
    st.caption(f"Kapasitas {kolam.kapasitas} • terisi {kolam.jumlah_ikan} ikan")
    c1, c2 = st.columns(2)
    if c1.button("Ya, Hapus", type="primary", use_container_width=True):
        comp.kolam_svc().hapus_kolam(kolam.id_kolam)
        comp.sukses_rerun(f"Kolam {kolam.id_kolam} dihapus")
    if c2.button("Batal", use_container_width=True):
        st.rerun()


def render() -> None:
    comp.page_header(
        "Kolam",
        "Pantau kualitas air dan kepadatan populasi tiap kolam.",
    )

    svc = comp.kolam_svc()
    kolam_list = svc.load_semua_kolam()

    bermasalah = [k for k in kolam_list if not comp.status_kolam(k)[0]]
    if bermasalah:
        st.warning(
            f"**{len(bermasalah)} kolam** membutuhkan perhatian: "
            + ", ".join(k.id_kolam for k in bermasalah)
            + " — detail pada kolom Status Air di tabel."
        )

    df = comp.kolam_df(kolam_list)
    if not df.empty:
        st.dataframe(comp.kolam_styler(df), hide_index=True, width="stretch", height=320)

    if kolam_list:
        comp.section("Kepadatan per Kolam")
        cols = st.columns(len(kolam_list))
        for idx, k in enumerate(kolam_list):
            with cols[idx]:
                ratio = k.jumlah_ikan / k.kapasitas if k.kapasitas else 0
                st.markdown(f"**{k.id_kolam}**")
                st.caption(k.nama)
                st.progress(min(ratio, 1.0))
                st.caption(f"{k.jumlah_ikan}/{k.kapasitas} ({comp.pct(k.jumlah_ikan, k.kapasitas)})")

    a1, a2, a3 = st.columns(3)
    if a1.button("+ Tambah Kolam", type="primary", use_container_width=True):
        st.session_state.pop(_P + "_seed_tambah", None)
        dlg_tambah()
    if a2.button("Edit Kolam", use_container_width=True, disabled=not kolam_list):
        st.session_state.pop(_P + "_seed_edit", None)
        dlg_edit(kolam_list)
    if a3.button("Hapus Kolam", use_container_width=True, disabled=not kolam_list):
        dlg_hapus(kolam_list)
