"""
Halaman Pemijahan — CRUD sesi pemijahan dan statistik penetasan.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

import ui.components as comp
from exceptions import HiaskanBaseError
from models.pemijahan import Pemijahan
from services.file_handler import FileHandler

STATUS_PIJAH = ["berlangsung", "selesai", "gagal"]
_P = "pijah_"

FILE = comp.DATA_DIR / "pemijahan.json"


def _semua() -> list[dict]:
    return FileHandler.load_json(FILE)


def _generate_id() -> str:
    data = _semua()
    if not data:
        return "PIJ001"
    nums = []
    for d in data:
        try:
            nums.append(int(d["id"][3:]))
        except (ValueError, KeyError, IndexError):
            continue
    return f"PIJ{max(nums, default=0) + 1:03d}"


def _seed(fields: dict, marker: str, nilai: str) -> None:
    """Isi session_state hanya jika marker belum cocok — tidak menimpa
    nilai widget yang sedang diedit/di-stepper oleh user."""
    if st.session_state.get(marker) == nilai:
        return
    for k, v in fields.items():
        st.session_state[_P + k] = v
    st.session_state[marker] = nilai


def _baca_field() -> dict:
    panen = st.session_state.get(_P + "tanggal_panen")
    return {
        "kolam_id": st.session_state[_P + "kolam_id"],
        "jenis_ikan": st.session_state[_P + "jenis_ikan"],
        "induk_jantan_id": st.session_state[_P + "induk_jantan_id"],
        "induk_betina_id": st.session_state[_P + "induk_betina_id"],
        "tanggal_pijah": comp.to_iso(st.session_state[_P + "tanggal_pijah"]),
        "jumlah_telur": int(st.session_state[_P + "jumlah_telur"]),
        "jumlah_menetas": int(st.session_state[_P + "jumlah_menetas"]),
        "jumlah_larva_hidup": int(st.session_state[_P + "jumlah_larva_hidup"]),
        "tanggal_panen": comp.to_iso(panen) if panen else "",
        "status": st.session_state[_P + "status"],
        "catatan": st.session_state[_P + "catatan"],
    }


def _form_pemijahan(ikan_ids: list[str], kolam_ids: list[str]) -> None:
    c1, c2 = st.columns(2)
    c1.selectbox("Kolam", ["(pilih)"] + kolam_ids, key=_P + "kolam_id", filter_mode=None)
    c2.text_input("Jenis Ikan", key=_P + "jenis_ikan")
    c1, c2 = st.columns(2)
    c1.selectbox("Induk Jantan", ["(pilih)"] + ikan_ids, key=_P + "induk_jantan_id", filter_mode=None)
    c2.selectbox("Induk Betina", ["(pilih)"] + ikan_ids, key=_P + "induk_betina_id", filter_mode=None)
    c1, c2, c3 = st.columns(3)
    c1.date_input("Tanggal Pijah", key=_P + "tanggal_pijah")
    c2.number_input("Jumlah Telur", 0, 100000, key=_P + "jumlah_telur")
    c3.number_input("Jumlah Menetas", 0, 100000, key=_P + "jumlah_menetas")
    c1, c2, c3 = st.columns(3)
    c1.number_input("Larva Hidup", 0, 100000, key=_P + "jumlah_larva_hidup")
    c2.date_input("Tanggal Panen (opsional)", value=None, key=_P + "tanggal_panen")
    c3.selectbox("Status", STATUS_PIJAH, key=_P + "status", filter_mode=None)
    st.text_area("Catatan", key=_P + "catatan")


def _pilihan_ikan() -> list[str]:
    return [i.to_dict()["id"] for i in comp.stok_svc().load_semua_ikan()]


def _pilihan_kolam() -> list[str]:
    return [k.id_kolam for k in comp.kolam_svc().load_semua_kolam()]


@st.dialog("Tambah Pemijahan", width="large")
def dlg_tambah() -> None:
    _seed({
        "kolam_id": "(pilih)", "jenis_ikan": "", "induk_jantan_id": "(pilih)",
        "induk_betina_id": "(pilih)", "tanggal_pijah": date.today(),
        "jumlah_telur": 0, "jumlah_menetas": 0, "jumlah_larva_hidup": 0,
        "tanggal_panen": None, "status": "berlangsung", "catatan": "",
    }, _P + "_seed_tambah", "open")
    _form_pemijahan(_pilihan_ikan(), _pilihan_kolam())
    if st.button("Simpan", type="primary", use_container_width=True):
        try:
            new_id = _generate_id()
            FileHandler.tambah_json(FILE, {"id": new_id, **_baca_field()})
            comp.sukses_rerun(f"Pemijahan {new_id} dicatat")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Edit Pemijahan", width="large")
def dlg_edit(data) -> None:
    pilihan = {
        f"{d.get('id', '')} — {d.get('jenis_ikan', '')}": d.get("id", "") for d in data
    }
    picked = st.selectbox("Pilih pemijahan", list(pilihan), filter_mode=None)
    rec = next(d for d in data if d.get("id") == pilihan[picked])
    _seed({
        "kolam_id": rec.get("kolam_id") or "(pilih)",
        "jenis_ikan": rec.get("jenis_ikan", ""),
        "induk_jantan_id": rec.get("induk_jantan_id") or "(pilih)",
        "induk_betina_id": rec.get("induk_betina_id") or "(pilih)",
        "tanggal_pijah": date.fromisoformat(rec["tanggal_pijah"]),
        "jumlah_telur": int(rec.get("jumlah_telur", 0)),
        "jumlah_menetas": int(rec.get("jumlah_menetas", 0)),
        "jumlah_larva_hidup": int(rec.get("jumlah_larva_hidup", 0)),
        "tanggal_panen": date.fromisoformat(rec["tanggal_panen"]) if rec.get("tanggal_panen") else None,
        "status": rec.get("status", "berlangsung"),
        "catatan": rec.get("catatan", ""),
    }, _P + "_seed_edit", str(rec.get("id", "")))
    _form_pemijahan(_pilihan_ikan(), _pilihan_kolam())
    if st.button("Simpan Perubahan", type="primary", use_container_width=True):
        try:
            FileHandler.update_json(FILE, rec["id"], {"id": rec["id"], **_baca_field()})
            comp.sukses_rerun(f"Pemijahan {rec['id']} diperbarui")
        except HiaskanBaseError as e:
            st.error(str(e))


@st.dialog("Hapus Pemijahan")
def dlg_hapus(data) -> None:
    pilihan = {
        f"{d.get('id', '')} — {d.get('jenis_ikan', '')}": d.get("id", "") for d in data
    }
    picked = st.selectbox("Pilih pemijahan", list(pilihan), filter_mode=None)
    rec = next(d for d in data if d.get("id") == pilihan[picked])
    c1, c2 = st.columns(2)
    if c1.button("Ya, Hapus", type="primary", use_container_width=True):
        FileHandler.hapus_json(FILE, rec["id"])
        comp.sukses_rerun(f"Pemijahan {rec['id']} dihapus")
    if c2.button("Batal", use_container_width=True):
        st.rerun()


def render() -> None:
    comp.page_header(
        "Pemijahan",
        "Catat proses pemijahan dan pantau tingkat penetasan.",
    )

    data = _semua()
    pemijahan = [Pemijahan.from_dict(d) for d in data]

    aktif = sum(1 for p in pemijahan if p.status == "berlangsung")
    penetasan = [p.tingkat_penetasan for p in pemijahan if p.jumlah_telur > 0]
    kelangsungan = [p.tingkat_kelangsungan_hidup for p in pemijahan if p.jumlah_menetas > 0]
    avg_penetasan = sum(penetasan) / len(penetasan) if penetasan else 0.0
    avg_kelangsungan = sum(kelangsungan) / len(kelangsungan) if kelangsungan else 0.0

    c = st.columns(4)
    with c[0]:
        comp.kpi("Total Sesi", str(len(pemijahan)))
    with c[1]:
        comp.kpi("Berlangsung", str(aktif))
    with c[2]:
        comp.kpi("Rata-rata Penetasan", f"{avg_penetasan:.1f}%")
    with c[3]:
        comp.kpi("Rata-rata Kelangsungan", f"{avg_kelangsungan:.1f}%")

    df = comp.pemijahan_df(data)
    if not df.empty:
        styler = comp.pemijahan_styler(df)
        st.dataframe(styler, hide_index=True, width="stretch", height=300)
    else:
        st.caption("Belum ada data pemijahan.")

    a1, a2, a3 = st.columns(3)
    if a1.button("+ Tambah Pemijahan", type="primary", use_container_width=True):
        st.session_state.pop(_P + "_seed_tambah", None)
        dlg_tambah()
    if a2.button("Edit Pemijahan", use_container_width=True, disabled=not data):
        st.session_state.pop(_P + "_seed_edit", None)
        dlg_edit(data)
    if a3.button("Hapus Pemijahan", use_container_width=True, disabled=not data):
        dlg_hapus(data)
