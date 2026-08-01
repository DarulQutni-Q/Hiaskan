"""
Halaman Penjualan — keranjang interaktif, validasi stok, dan riwayat transaksi.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import ui.components as comp
from exceptions import HiaskanBaseError, StokIkanTidakCukupError
from models.penjualan import ItemPenjualan, Penjualan

KOLOM_KERANJANG = ["ikan_id", "jenis_ikan", "varietas", "jumlah"]


def _keranjang() -> pd.DataFrame:
    k = st.session_state.get("_cart")
    if k is None or isinstance(k, list):
        df = pd.DataFrame(k or [], columns=KOLOM_KERANJANG)
        st.session_state["_cart"] = df
        return df
    return k


def _simpan_cart() -> None:
    """Sinkronkan hasil edit data_editor ke state keranjang."""
    st.session_state["_cart"] = st.session_state.get("_cart_widget", _keranjang())


def _reset_cart() -> None:
    st.session_state["_cart"] = pd.DataFrame(columns=KOLOM_KERANJANG)
    st.session_state.pop("_cart_widget", None)


def _proses(jual_svc, pel_map: dict, catatan: str) -> None:
    pel_id = st.session_state.get("jual_pelanggan")
    if not pel_id:
        st.error("Pilih pelanggan terlebih dahulu.")
        return
    df = _keranjang()
    if df.empty:
        st.error("Keranjang kosong — tambahkan item terlebih dahulu.")
        return
    df = df.copy()
    df = df[df["ikan_id"].notna() & df["ikan_id"].astype(str).str.strip().ne("")]
    df = df[df["jumlah"].notna()]
    if df.empty:
        st.error("Keranjang kosong — tambahkan item terlebih dahulu.")
        return

    items = [
        ItemPenjualan(
            ikan_id=str(r.ikan_id).strip(),
            jenis_ikan=str(r.get("jenis_ikan") or ""),
            varietas=str(r.get("varietas") or ""),
            jumlah=max(int(r.jumlah), 1),
        )
        for _, r in df.iterrows()
    ]
    penjualan = Penjualan(
        id_penjualan=jual_svc.generate_id_penjualan(),
        pelanggan_id=pel_id,
        pelanggan_nama=pel_map.get(pel_id, ""),
        items=items,
        catatan=catatan,
    )
    try:
        result = jual_svc.proses_penjualan(penjualan)
        comp.toast(f"Penjualan {result.id_penjualan} berhasil — {comp.rupiah(result.total)}")
        _reset_cart()
        st.rerun()
    except StokIkanTidakCukupError as e:
        st.error(f"{e} — kurangi jumlah atau pilih ikan lain.")
    except HiaskanBaseError as e:
        st.error(str(e))


def render() -> None:
    comp.page_header(
        "Penjualan",
        "Buat transaksi dengan validasi stok otomatis — stok berkurang langsung di data.",
    )

    jual_svc, stok_svc = comp.jual_svc(), comp.stok_svc()
    pelanggan = jual_svc.load_pelanggan()
    ikan_sehat = [i for i in stok_svc.load_semua_ikan() if i.status_kesehatan == "sehat"]

    pel_map = {p.id_pelanggan: p.nama for p in pelanggan}
    ikan_opts = {f"{i.id_ikan} — {i.jenis()} {i.varietas}": i.id_ikan for i in ikan_sehat}

    kiri, kanan = st.columns([2, 3], gap="medium")

    with kiri:
        comp.section("Transaksi Baru")
        pel = st.selectbox(
            "Pelanggan",
            list(pel_map.keys()),
            format_func=lambda pid: f"{pid} — {pel_map[pid]}",
            key="jual_pelanggan",
            disabled=not pel_map,
            filter_mode=None,
        )
        ik = st.selectbox(
            "Ikan (stok sehat)", list(ikan_opts) or ["—"],
            disabled=not ikan_opts,
            filter_mode=None,
        )
        stok_tersedia = next(
            (i.stok_sehat() for i in ikan_sehat if i.id_ikan == ikan_opts.get(ik)), 1
        )
        jml = st.number_input("Jumlah", 1, max(int(stok_tersedia), 1), step=1)
        catatan = st.text_input("Catatan", placeholder="Opsional")

        if st.button("+ Tambah ke Keranjang", type="primary", use_container_width=True):
            if not pel_map:
                st.error("Belum ada pelanggan — tambahkan pelanggan terlebih dahulu.")
            elif not ikan_opts:
                st.error("Tidak ada ikan sehat tersedia untuk dijual.")
            else:
                ikan = next(i for i in ikan_sehat if i.id_ikan == ikan_opts[ik])
                if jml > ikan.stok_sehat():
                    st.error(f"Stok {ikan.id_ikan} tidak cukup — tersedia {ikan.stok_sehat()} ekor.")
                else:
                    df = _keranjang()
                    row = pd.DataFrame([{
                        "ikan_id": ikan.id_ikan,
                        "jenis_ikan": ikan.jenis(),
                        "varietas": ikan.varietas,
                        "jumlah": int(jml),
                    }])
                    st.session_state["_cart"] = pd.concat([df, row], ignore_index=True)
                    st.session_state.pop("_cart_widget", None)
                    st.rerun()

    with kanan:
        comp.section("Keranjang")
        df = _keranjang()
        st.data_editor(
            df,
            key="_cart_widget",
            on_change=_simpan_cart,
            num_rows="dynamic",
            disabled=["ikan_id", "jenis_ikan", "varietas"],
            hide_index=True,
            width="stretch",
            column_config={
                "ikan_id": st.column_config.TextColumn("ID Ikan"),
                "jenis_ikan": st.column_config.TextColumn("Jenis"),
                "varietas": st.column_config.TextColumn("Varietas"),
                "jumlah": st.column_config.NumberColumn("Jumlah", min_value=1, step=1),
            },
        )
        st.caption("Edit jumlah langsung di tabel. Baris kosong diabaikan saat diproses.")
        if st.button(
            "Proses Penjualan",
            type="primary",
            use_container_width=True,
            disabled=df.empty,
        ):
            _proses(jual_svc, pel_map, catatan)

    comp.section("Riwayat Penjualan")
    riwayat = comp.riwayat_df()
    if not riwayat.empty:
        st.dataframe(
            riwayat.iloc[::-1],
            hide_index=True,
            width="stretch",
            height=420,
            column_config={
                "Total Harga": st.column_config.NumberColumn("Total Harga", format="Rp %d"),
            },
        )
    else:
        st.caption("Belum ada transaksi tercatat.")
