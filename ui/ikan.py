"""
Halaman Ikan — CRUD stok ikan hias, filter, dan preview harga otomatis.
"""

from __future__ import annotations

import streamlit as st

import ui.components as comp
from exceptions import HiaskanBaseError
from models.ikan import GRADE_VALID, KUALITAS_WARNA_VALID, STATUS_VALID, IkanHias

JENIS_IKAN = ["Cupang", "Guppy", "Koi"]
_P = "ikan_"


# ---------- Form & dialog ----------


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
        "jenis": st.session_state[_P + "jenis"],
        "varietas": st.session_state[_P + "varietas"],
        "warna": st.session_state[_P + "warna"],
        "kualitas_warna": st.session_state[_P + "kualitas_warna"],
        "grade": st.session_state[_P + "grade"],
        "status_kesehatan": st.session_state[_P + "status_kesehatan"],
        "ukuran_cm": float(st.session_state[_P + "ukuran_cm"]),
        "umur_bulan": int(st.session_state[_P + "umur_bulan"]),
        "jumlah_stok": int(st.session_state[_P + "jumlah_stok"]),
        "kolam_id": st.session_state.get(_P + "kolam_id", ""),
    }


def _form_ikan(kolam_list, editing_id: str = "") -> None:
    kolam_opts = {f"{k.id_kolam} — {k.nama}": k.id_kolam for k in kolam_list}
    ops = ["(tanpa kolam)"] + list(kolam_opts)

    st.selectbox("Jenis", JENIS_IKAN, key=_P + "jenis", filter_mode=None)
    c1, c2 = st.columns(2)
    c1.text_input("Varietas", key=_P + "varietas")
    c2.text_input("Warna", key=_P + "warna")
    c1, c2, c3 = st.columns(3)
    c1.selectbox("Kualitas Warna", KUALITAS_WARNA_VALID, key=_P + "kualitas_warna", filter_mode=None)
    c2.selectbox("Grade", list(GRADE_VALID), key=_P + "grade", filter_mode=None)
    c3.selectbox("Status Kesehatan", STATUS_VALID, key=_P + "status_kesehatan", filter_mode=None)
    c1, c2, c3 = st.columns(3)
    c1.number_input("Ukuran (cm)", 0.0, 200.0, step=0.5, key=_P + "ukuran_cm")
    c2.number_input("Umur (bulan)", 0, 240, key=_P + "umur_bulan")
    c3.number_input("Jumlah Stok", 0, 100000, key=_P + "jumlah_stok")

    kolam_pick = st.selectbox("Kolam", ops, key=_P + "kolam_pick", filter_mode=None)
    st.session_state[_P + "kolam_id"] = (
        "" if kolam_pick == "(tanpa kolam)" else kolam_opts[kolam_pick]
    )

    try:
        preview = IkanHias.from_dict({
            "id": editing_id or "PREV",
            **{k: _baca_field()[k] for k in (
                "jenis", "varietas", "warna", "kualitas_warna", "grade",
                "status_kesehatan", "ukuran_cm", "umur_bulan", "jumlah_stok",
            )},
            "kolam_id": st.session_state.get(_P + "kolam_id", ""),
        })
        st.caption(f"Harga jual: **{comp.rupiah(preview.hitung_harga_jual())}** per ekor")
    except (HiaskanBaseError, KeyError, ValueError):
        st.caption("Lengkapi data untuk melihat preview harga.")


@st.dialog("Tambah Ikan", width="large")
def dlg_tambah(kolam_list) -> None:
    _seed({
        "jenis": "Cupang", "varietas": "", "warna": "",
        "kualitas_warna": "standar", "grade": "B",
        "status_kesehatan": "sehat", "ukuran_cm": 4.0,
        "umur_bulan": 3, "jumlah_stok": 0, "kolam_id": "", "kolam_pick": "(tanpa kolam)",
    }, _P + "_seed_tambah", "open")
    _form_ikan(kolam_list)
    if st.button("Simpan", type="primary", use_container_width=True):
        try:
            data = _baca_field()
            new_id = comp.stok_svc().generate_id(data["jenis"])
            comp.stok_svc().tambah_ikan(IkanHias.from_dict({"id": new_id, **data}))
            comp.sukses_rerun(f"Ikan {new_id} ditambahkan")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Edit Ikan", width="large")
def dlg_edit(kolam_list, data) -> None:
    kolam_opts = {f"{k.id_kolam} — {k.nama}": k.id_kolam for k in kolam_list}
    pilihan = {f"{i.id_ikan} — {i.jenis()} {i.varietas}": i.id_ikan for i in data}
    picked = st.selectbox("Pilih ikan", list(pilihan), filter_mode=None)
    ikan = next(i for i in data if i.id_ikan == pilihan[picked])
    label_pick = next(
        (lbl for lbl, kid in kolam_opts.items() if kid == ikan.kolam_id),
        "(tanpa kolam)",
    )
    _seed({
        "jenis": ikan.jenis(), "varietas": ikan.varietas, "warna": ikan.warna,
        "kualitas_warna": ikan.kualitas_warna, "grade": ikan.grade,
        "status_kesehatan": ikan.status_kesehatan, "ukuran_cm": ikan.ukuran_cm,
        "umur_bulan": ikan.umur_bulan, "jumlah_stok": ikan.jumlah_stok,
        "kolam_id": ikan.kolam_id, "kolam_pick": label_pick,
    }, _P + "_seed_edit", ikan.id_ikan)
    _form_ikan(kolam_list, editing_id=ikan.id_ikan)
    if st.button("Simpan Perubahan", type="primary", use_container_width=True):
        try:
            data2 = _baca_field()
            comp.stok_svc().update_ikan(IkanHias.from_dict({"id": ikan.id_ikan, **data2}))
            comp.sukses_rerun(f"Ikan {ikan.id_ikan} diperbarui")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Hapus Ikan")
def dlg_hapus(data) -> None:
    pilihan = {f"{i.id_ikan} — {i.jenis()} {i.varietas}": i.id_ikan for i in data}
    picked = st.selectbox("Pilih ikan", list(pilihan), filter_mode=None)
    ikan = next(i for i in data if i.id_ikan == pilihan[picked])
    st.caption(f"{ikan.jenis()} {ikan.varietas} • stok {ikan.jumlah_stok}")
    c1, c2 = st.columns(2)
    if c1.button("Ya, Hapus", type="primary", use_container_width=True):
        comp.stok_svc().hapus_ikan(ikan.id_ikan)
        comp.sukses_rerun(f"Ikan {ikan.id_ikan} dihapus")
    if c2.button("Batal", use_container_width=True):
        st.rerun()


# ---------- Halaman ----------


def render() -> None:
    comp.page_header(
        "Ikan",
        "Kelola stok ikan hias — harga dihitung otomatis oleh strategi harga.",
    )

    svc = comp.stok_svc()
    semua = svc.load_semua_ikan()
    kolam_list = comp.kolam_svc().load_semua_kolam()

    st.caption(f"Total {len(semua)} varietas ikan tercatat.")

    k1, k2, k3 = st.columns([2, 1, 1])
    cari = k1.text_input(
        "Cari", placeholder="ID, varietas, atau warna", label_visibility="collapsed",
    )
    jenis = k2.selectbox("Jenis", ["Semua"] + sorted({i.jenis() for i in semua}), filter_mode=None)
    status = k3.selectbox("Status", ["Semua"] + list(STATUS_VALID), filter_mode=None)

    data = semua
    if cari:
        q = cari.lower()
        data = [
            i for i in data
            if q in i.id_ikan.lower()
            or q in i.varietas.lower()
            or q in i.warna.lower()
        ]
    if jenis != "Semua":
        data = [i for i in data if i.jenis() == jenis]
    if status != "Semua":
        data = [i for i in data if i.status_kesehatan == status]

    df = comp.ikan_df(data)
    if not df.empty:
        st.dataframe(comp.harga_styler(df), hide_index=True, width="stretch", height=400)
    else:
        st.caption("Tidak ada data yang cocok dengan filter.")

    a1, a2, a3 = st.columns(3)
    if a1.button("+ Tambah Ikan", type="primary", use_container_width=True):
        st.session_state.pop(_P + "_seed_tambah", None)
        dlg_tambah(kolam_list)
    if a2.button("Edit Ikan", use_container_width=True, disabled=not data):
        st.session_state.pop(_P + "_seed_edit", None)
        dlg_edit(kolam_list, data)
    if a3.button("Hapus Ikan", use_container_width=True, disabled=not data):
        dlg_hapus(data)
