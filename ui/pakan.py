"""
Halaman Pakan — CRUD pakan, pemakaian stok, dan peringatan kadaluarsa.
"""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

import ui.components as comp
from exceptions import DataTidakValidError, HiaskanBaseError
from models.pakan import Pakan
from services.file_handler import FileHandler

JENIS_PAKAN = ["pelet", "artemia", "cacing", "spirulina", "lainnya"]
_P = "pakan_"

FILE = comp.DATA_DIR / "pakan.json"


def _semua() -> list[dict]:
    return FileHandler.load_json(FILE)


def _generate_id() -> str:
    data = _semua()
    if not data:
        return "PKN001"
    nums = []
    for d in data:
        try:
            nums.append(int(d["id"][3:]))
        except (ValueError, KeyError, IndexError):
            continue
    return f"PKN{max(nums, default=0) + 1:03d}"


def _status_pakan(d: dict) -> tuple[str, str]:
    """Return (label, warna) berdasarkan stok & tanggal kadaluarsa."""
    try:
        exp = date.fromisoformat(d.get("tanggal_kadaluarsa", ""))
    except ValueError:
        exp = None
    sisa = (exp - date.today()).days if exp else None
    if sisa is not None and sisa < 0:
        return "Kadaluarsa", comp.DANGER
    if sisa is not None and sisa <= 30:
        return "Segera Kadaluarsa", comp.WARNING
    if float(d.get("stok_gram", 0)) < 500:
        return "Stok Menipis", comp.WARNING
    return "Aman", comp.SUCCESS


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
        "jenis": st.session_state[_P + "jenis"],
        "merek": st.session_state[_P + "merek"],
        "stok_gram": float(st.session_state[_P + "stok_gram"]),
        "harga_per_kg": int(st.session_state[_P + "harga_per_kg"]),
        "tanggal_beli": comp.to_iso(st.session_state[_P + "tanggal_beli"]),
        "tanggal_kadaluarsa": comp.to_iso(st.session_state[_P + "tanggal_kadaluarsa"]),
        "catatan": st.session_state[_P + "catatan"],
    }


def _form_pakan() -> None:
    st.text_input("Nama Pakan", key=_P + "nama")
    c1, c2 = st.columns(2)
    c1.selectbox("Jenis", JENIS_PAKAN, key=_P + "jenis", filter_mode=None)
    c2.text_input("Merek", key=_P + "merek")
    c1, c2 = st.columns(2)
    c1.number_input("Stok (gram)", 0.0, 1_000_000.0, step=50.0, key=_P + "stok_gram")
    c2.number_input("Harga per kg (Rp)", 0, 10_000_000, step=1000, key=_P + "harga_per_kg")
    c1, c2 = st.columns(2)
    c1.date_input("Tanggal Beli", key=_P + "tanggal_beli")
    c2.date_input("Tanggal Kadaluarsa", key=_P + "tanggal_kadaluarsa")
    st.text_area("Catatan", key=_P + "catatan")


@st.dialog("Tambah Pakan")
def dlg_tambah() -> None:
    _seed({
        "nama": "", "jenis": "pelet", "merek": "", "stok_gram": 500.0,
        "harga_per_kg": 100000, "tanggal_beli": date.today(),
        "tanggal_kadaluarsa": date.today() + timedelta(days=365), "catatan": "",
    }, _P + "_seed_tambah", "open")
    _form_pakan()
    if st.button("Simpan", type="primary", use_container_width=True):
        try:
            new_id = _generate_id()
            FileHandler.tambah_json(FILE, {"id": new_id, **_baca_field()})
            comp.sukses_rerun(f"Pakan {new_id} ditambahkan")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Edit Pakan")
def dlg_edit(data) -> None:
    pilihan = {f"{d.get('id', '')} — {d.get('nama', '')}": d.get("id", "") for d in data}
    picked = st.selectbox("Pilih pakan", list(pilihan), filter_mode=None)
    rec = next(d for d in data if d.get("id") == pilihan[picked])
    _seed({
        "nama": rec.get("nama", ""), "jenis": rec.get("jenis", "pelet"),
        "merek": rec.get("merek", ""), "stok_gram": float(rec.get("stok_gram", 0)),
        "harga_per_kg": int(rec.get("harga_per_kg", 0)),
        "tanggal_beli": date.fromisoformat(rec["tanggal_beli"]),
        "tanggal_kadaluarsa": date.fromisoformat(rec["tanggal_kadaluarsa"]),
        "catatan": rec.get("catatan", ""),
    }, _P + "_seed_edit", str(rec.get("id", "")))
    _form_pakan()
    if st.button("Simpan Perubahan", type="primary", use_container_width=True):
        try:
            FileHandler.update_json(FILE, rec["id"], {"id": rec["id"], **_baca_field()})
            comp.sukses_rerun(f"Pakan {rec['id']} diperbarui")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Hapus Pakan")
def dlg_hapus(data) -> None:
    pilihan = {f"{d.get('id', '')} — {d.get('nama', '')}": d.get("id", "") for d in data}
    picked = st.selectbox("Pilih pakan", list(pilihan), filter_mode=None)
    rec = next(d for d in data if d.get("id") == pilihan[picked])
    st.caption(f"Stok {rec.get('stok_gram', 0)} g • kadaluarsa {rec.get('tanggal_kadaluarsa', '—')}")
    c1, c2 = st.columns(2)
    if c1.button("Ya, Hapus", type="primary", use_container_width=True):
        FileHandler.hapus_json(FILE, rec["id"])
        comp.sukses_rerun(f"Pakan {rec['id']} dihapus")
    if c2.button("Batal", use_container_width=True):
        st.rerun()


@st.dialog("Gunakan Pakan")
def dlg_pakai(data) -> None:
    pilihan = {f"{d.get('id', '')} — {d.get('nama', '')}": d.get("id", "") for d in data}
    picked = st.selectbox("Pilih pakan", list(pilihan), filter_mode=None)
    rec = next(d for d in data if d.get("id") == pilihan[picked])
    gram = st.number_input("Jumlah yang dipakai (gram)", 1.0, 1_000_000.0, step=10.0)
    if st.button("Kurangi Stok", type="primary", use_container_width=True):
        try:
            p = Pakan.from_dict(rec)
            p.gunakan(gram)
            FileHandler.update_json(FILE, rec["id"], p.to_dict())
            comp.sukses_rerun(f"Stok {rec['id']} berkurang {gram:g} g")
        except (DataTidakValidError, HiaskanBaseError) as e:
            st.error(str(e))


@st.dialog("Tambah Stok Pakan")
def dlg_isi(data) -> None:
    pilihan = {f"{d.get('id', '')} — {d.get('nama', '')}": d.get("id", "") for d in data}
    picked = st.selectbox("Pilih pakan", list(pilihan), filter_mode=None)
    rec = next(d for d in data if d.get("id") == pilihan[picked])
    gram = st.number_input("Jumlah tambahan (gram)", 1.0, 1_000_000.0, step=100.0)
    if st.button("Tambah Stok", type="primary", use_container_width=True):
        try:
            p = Pakan.from_dict(rec)
            p.tambah_stok(gram)
            FileHandler.update_json(FILE, rec["id"], p.to_dict())
            comp.sukses_rerun(f"Stok {rec['id']} bertambah {gram:g} g")
        except (DataTidakValidError, HiaskanBaseError) as e:
            st.error(str(e))


def render() -> None:
    comp.page_header(
        "Pakan",
        "Kelola persediaan pakan dan pantau kadaluarsa.",
    )

    data = _semua()

    df = comp.pakan_df(data)
    if not df.empty:
        df["Status"] = [_status_pakan(d)[0] for d in data]
        warna = dict(_status_pakan(d) for d in data)
        styler = df.style.format({
            "Stok (g)": lambda v: f"{v:g} g",
            "Harga/kg": lambda v: comp.rupiah(v),
        }).map(
            lambda v: f"color: {warna.get(v, comp.MUTED)}; font-weight: 600",
            subset=["Status"],
        )
        st.dataframe(styler, hide_index=True, width="stretch", height=300)
    else:
        st.caption("Belum ada pakan tercatat.")

    a1, a2, a3, a4, a5 = st.columns(5)
    if a1.button("+ Tambah", type="primary", use_container_width=True):
        st.session_state.pop(_P + "_seed_tambah", None)
        dlg_tambah()
    if a2.button("Edit", use_container_width=True, disabled=not data):
        st.session_state.pop(_P + "_seed_edit", None)
        dlg_edit(data)
    if a3.button("Hapus", use_container_width=True, disabled=not data):
        dlg_hapus(data)
    if a4.button("Gunakan Stok", use_container_width=True, disabled=not data):
        dlg_pakai(data)
    if a5.button("Tambah Stok", use_container_width=True, disabled=not data):
        dlg_isi(data)
