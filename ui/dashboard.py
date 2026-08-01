"""
Halaman Dashboard — KPI, grafik interaktif, dan peringatan otomatis.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import ui.components as comp
from models.pakan import Pakan
from services.file_handler import FileHandler


def _int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def render() -> None:
    comp.page_header(
        "Dashboard",
        "Ringkasan operasional pembibitan — dibaca langsung dari data terbaru.",
    )

    stok_svc, kolam_svc, jual_svc = comp.stok_svc(), comp.kolam_svc(), comp.jual_svc()
    semua_ikan = stok_svc.load_semua_ikan()
    kolam_list = kolam_svc.load_semua_kolam()
    riwayat = jual_svc.load_riwayat()
    pakan_data = [Pakan.from_dict(d) for d in FileHandler.load_json(comp.DATA_DIR / "pakan.json")]

    total = sum(i.jumlah_stok for i in semua_ikan)
    sehat = sum(i.stok_sehat() for i in semua_ikan)
    pendapatan = jual_svc.total_pendapatan()
    n_transaksi = len([r for r in riwayat if r])

    c = st.columns(5)
    with c[0]:
        comp.kpi("Total Ikan", f"{total:,}")
    with c[1]:
        comp.kpi("Stok Sehat", f"{sehat:,}", f"{comp.pct(sehat, total)} dari total")
    with c[2]:
        comp.kpi("Kolam Aktif", str(len(kolam_list)))
    with c[3]:
        comp.kpi("Pendapatan", comp.rupiah(pendapatan))
    with c[4]:
        comp.kpi("Transaksi", str(n_transaksi))

    # ---- Peringatan otomatis ----

    for k in kolam_list:
        aman, detail = comp.status_kolam(k)
        if not aman:
            st.warning(f"**{k.id_kolam} — {k.nama}**: kualitas air butuh perhatian — {detail}")

    low_stock = [i for i in semua_ikan if i.jumlah_stok <= 5]
    if low_stock:
        daftar = ", ".join(f"{i.id_ikan} ({i.jumlah_stok})" for i in low_stock)
        st.info(f"Stok menipis (≤ 5 ekor): {daftar}")

    hari_ini = date.today()
    for p in pakan_data:
        if not p.tanggal_kadaluarsa:
            continue
        try:
            exp = date.fromisoformat(p.tanggal_kadaluarsa)
        except ValueError:
            continue
        sisa = (exp - hari_ini).days
        if sisa < 0:
            st.warning(f"**Pakan {p.id_pakan}** sudah kadaluarsa ({p.tanggal_kadaluarsa}).")
        elif sisa <= 30:
            st.info(f"**Pakan {p.id_pakan}** kadaluarsa dalam {sisa} hari ({p.tanggal_kadaluarsa}).")

    # ---- Grafik ----

    comp.section("Analitik")
    kiri, kanan = st.columns(2)

    with kiri:
        per_jenis = stok_svc.total_stok_per_jenis()
        sehat_jenis = stok_svc.total_stok_sehat_per_jenis()
        jenis_set = sorted(set(per_jenis) | set(sehat_jenis))
        dfm = pd.DataFrame({
            "Jenis": jenis_set,
            "Sehat": [sehat_jenis.get(j, 0) for j in jenis_set],
            "Tidak Sehat": [per_jenis.get(j, 0) - sehat_jenis.get(j, 0) for j in jenis_set],
        })
        fig = px.bar(
            dfm, x="Jenis", y=["Tidak Sehat", "Sehat"],
            barmode="stack", color_discrete_sequence=[comp.BORDER, comp.TEAL],
        )
        fig.update_layout(comp.chart_layout(title="Stok per Jenis"))
        st.plotly_chart(fig, width="stretch", config=comp.plotly_config())

    with kanan:
        pend_per_jenis = jual_svc.pendapatan_per_jenis()
        if pend_per_jenis:
            fig2 = px.pie(
                names=list(pend_per_jenis), values=list(pend_per_jenis.values()),
                hole=0.62, color_discrete_sequence=comp.CHART_COLORS,
            )
            fig2.update_layout(comp.chart_layout(title="Pendapatan per Jenis"))
            fig2.update_traces(textinfo="percent", textfont_size=11)
            st.plotly_chart(fig2, width="stretch", config=comp.plotly_config())
        else:
            st.caption("Belum ada data penjualan.")

    kiri2, kanan2 = st.columns(2)

    with kiri2:
        trend: dict[str, int] = {}
        for r in riwayat:
            if len(r) > 5:
                trend[r[1]] = trend.get(r[1], 0) + _int(r[5])
        if trend:
            dft = pd.DataFrame(sorted(trend.items()), columns=["Tanggal", "Pendapatan"])
            fig3 = px.line(
                dft, x="Tanggal", y="Pendapatan",
                markers=True, color_discrete_sequence=[comp.TEAL],
            )
            fig3.update_layout(comp.chart_layout(title="Tren Penjualan"))
            fig3.update_yaxes(tickformat=",")
            st.plotly_chart(fig3, width="stretch", config=comp.plotly_config())
        else:
            st.caption("Belum ada data penjualan.")

    with kanan2:
        status_counts: dict[str, int] = {}
        for i in semua_ikan:
            status_counts[i.status_kesehatan] = (
                status_counts.get(i.status_kesehatan, 0) + i.jumlah_stok
            )
        if status_counts:
            warna = [comp.STATUS_COLOR.get(s, comp.MUTED) for s in status_counts]
            fig4 = px.pie(
                names=list(status_counts), values=list(status_counts.values()),
                hole=0.62, color_discrete_sequence=warna,
            )
            fig4.update_layout(comp.chart_layout(title="Status Kesehatan Stok"))
            fig4.update_traces(textinfo="percent", textfont_size=11)
            st.plotly_chart(fig4, width="stretch", config=comp.plotly_config())

    # ---- Kepadatan kolam ----

    comp.section("Kepadatan Kolam")
    if kolam_list:
        kolam_cols = st.columns(len(kolam_list))
        for idx, k in enumerate(kolam_list):
            with kolam_cols[idx]:
                ratio = k.jumlah_ikan / k.kapasitas if k.kapasitas else 0
                st.markdown(f"**{k.id_kolam}** — {k.nama}")
                st.progress(min(ratio, 1.0))
                st.caption(f"{k.jumlah_ikan} / {k.kapasitas} ikan ({comp.pct(k.jumlah_ikan, k.kapasitas)})")
    else:
        st.caption("Belum ada kolam tercatat.")

    # ---- Riwayat terbaru ----

    comp.section("Penjualan Terakhir")
    df = comp.riwayat_df()
    if not df.empty:
        st.dataframe(
            df.iloc[::-1].head(8),
            hide_index=True,
            width="stretch",
            column_config={
                "Total Harga": st.column_config.NumberColumn("Total Harga", format="Rp %d"),
            },
        )
    else:
        st.caption("Belum ada transaksi.")
