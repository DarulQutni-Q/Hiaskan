"""
Helper bersama untuk halaman-halaman Streamlit Hiaskan.

Layer ini hanya memanggil services — tanpa logika bisnis (lihat AGENTS.md).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from models.kolam import BATAS_AMAN, Kolam
from services.kolam_service import KolamService
from services.laporan_service import LaporanService
from services.penjualan_service import PenjualanService
from services.stok_service import StokService

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LAPORAN_DIR = PROJECT_ROOT / "laporan"

# Palet warna minimalis — aksen teal (air), netral hangat (batu)
TEAL = "#0F766E"
INK = "#1C1917"
MUTED = "#78716C"
BORDER = "#E7E5E4"
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"
CHART_COLORS = [
    "#0F766E", "#F59E0B", "#0EA5E9", "#84CC16",
    "#8B5CF6", "#F43F5E", "#64748B",
]
STATUS_COLOR = {
    "sehat": SUCCESS,
    "sakit": WARNING,
    "karantina": "#EA580C",
    "mati": DANGER,
}


# ---------- Services (stateless — aman untuk di-cache) ----------


@st.cache_resource
def stok_svc() -> StokService:
    return StokService(DATA_DIR)


@st.cache_resource
def kolam_svc() -> KolamService:
    return KolamService(DATA_DIR)


@st.cache_resource
def jual_svc() -> PenjualanService:
    return PenjualanService(DATA_DIR)


@st.cache_resource
def laporan_svc() -> LaporanService:
    return LaporanService(DATA_DIR)


# ---------- Format ----------


def rupiah(nilai: float | int) -> str:
    return f"Rp {int(round(nilai)):,}".replace(",", ".")


def pct(sebagian: float, total: float) -> str:
    if not total:
        return "0%"
    return f"{sebagian / total * 100:.0f}%"


def to_iso(v) -> str:
    return v.isoformat() if v else ""


# ---------- Tampilan ----------

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1.6rem; padding-bottom: 2.5rem;}
.stApp {background: #FAFAF8;}
[data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #E7E5E4;}
.stButton > button, .stDownloadButton > button {border-radius: 8px;}
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
    border: 1px solid #E7E5E4; border-radius: 12px; overflow: hidden;
}
h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    letter-spacing: -0.02em; color: #1C1917;
}
[data-testid="stDialog"] h2 {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    font-weight: 700;
}
.hs-title {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    font-size: 30px; font-weight: 800; letter-spacing: -0.03em;
    color: #1C1917; margin: 0 0 4px; line-height: 1.2;
}
.hs-brand {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    font-size: 22px; font-weight: 800; letter-spacing: -0.02em;
    color: #0F766E; margin: 0; line-height: 1.2;
}
.hs-card {
    background: #FFFFFF; border: 1px solid #E7E5E4; border-radius: 14px;
    padding: 18px 22px; box-shadow: 0 1px 2px rgba(28, 25, 23, 0.05);
}
.hs-label {
    margin: 0; font-size: 12px; letter-spacing: .6px;
    text-transform: uppercase; color: #78716C;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}
.hs-value {
    margin: 6px 0 2px; font-size: 30px; font-weight: 700; color: #1C1917;
    line-height: 1.15; font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}
.hs-sub {margin: 0; font-size: 12.5px; color: #A8A29E;}
.hs-section {
    font-size: 17px; font-weight: 600; color: #1C1917; margin: 0;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def kpi(label: str, value: str, sub: str = "") -> None:
    sub_html = f'<p class="hs-sub">{sub}</p>' if sub else ""
    st.markdown(
        f'<div class="hs-card"><p class="hs-label">{label}</p>'
        f'<p class="hs-value">{value}</p>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def section(titel: str) -> None:
    st.markdown(f'<p class="hs-section">{titel}</p>', unsafe_allow_html=True)


def page_header(titel: str, sub: str = "") -> None:
    st.markdown(f'<h1 class="hs-title">{titel}</h1>', unsafe_allow_html=True)
    if sub:
        st.caption(sub)


def toast(msg: str) -> None:
    st.session_state["_hs_toast"] = msg


def flush_toast() -> None:
    pesan = st.session_state.pop("_hs_toast", None)
    if pesan:
        st.toast(pesan)


def sukses_rerun(msg: str) -> None:
    toast(msg)
    st.rerun()


# ---------- Konversi data -> DataFrame ----------


def ikan_df(ikan_list) -> pd.DataFrame:
    rows = []
    for i in ikan_list:
        rows.append({
            "ID": i.id_ikan,
            "Jenis": i.jenis(),
            "Varietas": i.varietas,
            "Warna": i.warna,
            "Ukuran (cm)": i.ukuran_cm,
            "Umur (bln)": i.umur_bulan,
            "Grade": i.grade,
            "Stok": i.jumlah_stok,
            "Status": i.status_kesehatan,
            "Kolam": i.kolam_id or "—",
            "Harga Jual": i.hitung_harga_jual(),
        })
    return pd.DataFrame(rows)


def harga_styler(df: pd.DataFrame):
    return (
        df.style
        .format({"Harga Jual": lambda v: rupiah(v)})
        .map(
            lambda v: f"color: {STATUS_COLOR.get(str(v).lower(), INK)}; font-weight: 600",
            subset=["Status"],
        )
    )


def status_kolam(k: Kolam) -> tuple[bool, str]:
    """Return (aman, detail_pelanggaran) untuk satu kolam."""
    air = k.kualitas_air
    masalah: list[str] = []
    for param, (bmin, bmax) in BATAS_AMAN.items():
        nilai = getattr(air, param)
        if nilai < bmin or nilai > bmax:
            masalah.append(f"{param} = {nilai} (batas {bmin}–{bmax})")
    if k.kapasitas and k.jumlah_ikan > k.kapasitas:
        masalah.append(f"kepadatan {k.jumlah_ikan}/{k.kapasitas}")
    return (not masalah), ", ".join(masalah)


def kolam_df(kolam_list) -> pd.DataFrame:
    rows = []
    for k in kolam_list:
        air = k.kualitas_air
        aman, _ = status_kolam(k)
        kepadatan = round(k.jumlah_ikan / k.kapasitas * 100, 0) if k.kapasitas else 0
        rows.append({
            "ID": k.id_kolam,
            "Nama": k.nama,
            "Kapasitas": k.kapasitas,
            "Jenis Ikan": k.jenis_ikan or "—",
            "Jumlah Ikan": k.jumlah_ikan,
            "Kepadatan (%)": kepadatan,
            "pH": air.ph,
            "Suhu (°C)": k.suhu_air,
            "Oksigen (mg/L)": air.oksigen,
            "Amonia (mg/L)": air.amonia,
            "Status Air": "Aman" if aman else "Tidak Aman",
        })
    return pd.DataFrame(rows)


def kolam_styler(df: pd.DataFrame):
    return (
        df.style
        .map(
            lambda v: f"color: {SUCCESS}; font-weight: 600"
            if v == "Aman"
            else f"color: {DANGER}; font-weight: 600",
            subset=["Status Air"],
        )
        .map(
            lambda v: f"color: {DANGER}; font-weight: 600"
            if isinstance(v, (int, float)) and v > 100
            else "",
            subset=["Kepadatan (%)"],
        )
    )


def riwayat_df() -> pd.DataFrame:
    """Riwayat penjualan dari CSV dalam bentuk DataFrame."""
    rows = jual_svc().load_riwayat()
    data = []
    for r in rows:
        data.append({
            "ID": r[0] if len(r) > 0 else "",
            "Tanggal": r[1] if len(r) > 1 else "",
            "Pelanggan": r[3] if len(r) > 3 else "",
            "Total Ikan": r[4] if len(r) > 4 else "",
            "Total Harga": r[5] if len(r) > 5 else "",
            "Detail": _detail_items(r[6]) if len(r) > 6 else "",
        })
    df = pd.DataFrame(data)
    if not df.empty:
        df["Total Harga"] = pd.to_numeric(df["Total Harga"], errors="coerce").fillna(0).astype(int)
        df["Total Ikan"] = pd.to_numeric(df["Total Ikan"], errors="coerce").fillna(0).astype(int)
    return df


def _detail_items(raw: str) -> str:
    try:
        items = json.loads(raw)
        return ", ".join(
            f"{it.get('jenis_ikan', '')} {it.get('varietas', '')} ({it.get('jumlah', 0)}x)"
            for it in items
        )
    except (ValueError, json.JSONDecodeError):
        return raw


def pakan_df(data) -> pd.DataFrame:
    rows = []
    for d in data:
        rows.append({
            "ID": d.get("id", ""),
            "Nama": d.get("nama", ""),
            "Jenis": d.get("jenis", ""),
            "Merek": d.get("merek", ""),
            "Stok (g)": d.get("stok_gram", 0),
            "Harga/kg": d.get("harga_per_kg", 0),
            "Tgl Beli": d.get("tanggal_beli", ""),
            "Kadaluarsa": d.get("tanggal_kadaluarsa", ""),
        })
    return pd.DataFrame(rows)


def pemijahan_df(data) -> pd.DataFrame:
    from models.pemijahan import Pemijahan

    rows = []
    for d in data:
        p = Pemijahan.from_dict(d)
        rows.append({
            "ID": p.id_pemijahan,
            "Kolam": p.kolam_id,
            "Jenis": p.jenis_ikan,
            "Tgl Pijah": p.tanggal_pijah,
            "Telur": p.jumlah_telur,
            "Menetas": p.jumlah_menetas,
            "Larva Hidup": p.jumlah_larva_hidup,
            "% Penetasan": p.tingkat_penetasan,
            "% Kelangsungan": p.tingkat_kelangsungan_hidup,
            "Status": p.status,
            "Tgl Panen": p.tanggal_panen or "—",
        })
    return pd.DataFrame(rows)


def pemijahan_styler(df: pd.DataFrame):
    warna = {"selesai": SUCCESS, "berlangsung": TEAL, "gagal": DANGER}
    return df.style.map(
        lambda v: f"color: {warna.get(str(v).lower(), MUTED)}; font-weight: 600",
        subset=["Status"],
    )


# ---------- Chart ----------


def plotly_config() -> dict:
    """Konfigurasi plotly: tanpa modebar & zoom/crop — grafik bersifat statis."""
    return {"displayModeBar": False, "scrollZoom": False}


def chart_layout(**kwargs) -> dict:
    layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "'Plus Jakarta Sans', 'Segoe UI', Inter, sans-serif", "color": MUTED, "size": 12},
        "margin": {"l": 10, "r": 10, "t": 34, "b": 10},
        "showlegend": False,
        "dragmode": False,
        "xaxis": {"gridcolor": BORDER, "zeroline": False, "linecolor": BORDER},
        "yaxis": {"gridcolor": BORDER, "zeroline": False, "linecolor": BORDER},
    }
    layout.update(kwargs)
    return layout
