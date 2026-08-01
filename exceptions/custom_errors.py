"""
Custom exceptions untuk sistem Hiaskan - Pembibitan Ikan Hias & Penjualan.

Hierarki:
    HiaskanBaseError
    ├── KualitasAirBurukError   — parameter air di luar batas aman
    ├── StokIkanTidakCukupError — penjualan melebihi stok sehat
    ├── DataTidakValidError     — data input tidak valid
    └── FileOperasiError        — kegagalan baca/tulis file
"""


class HiaskanBaseError(Exception):
    """Base exception untuk seluruh error pada sistem Hiaskan."""

    pass


class KualitasAirBurukError(HiaskanBaseError):
    """Dilempar saat parameter kualitas air berada di luar batas aman.

    Attributes:
        parameter: nama parameter air (ph, suhu, oksigen, amonia).
        nilai: nilai aktual yang terukur.
        batas_min: batas minimum yang diperbolehkan.
        batas_max: batas maksimum yang diperbolehkan.
    """

    def __init__(
        self,
        parameter: str,
        nilai: float,
        batas_min: float,
        batas_max: float,
    ) -> None:
        self.parameter = parameter
        self.nilai = nilai
        self.batas_min = batas_min
        self.batas_max = batas_max
        super().__init__(
            f"Kualitas air buruk: {parameter} = {nilai} "
            f"(batas aman: {batas_min} - {batas_max})"
        )


class StokIkanTidakCukupError(HiaskanBaseError):
    """Dilempar saat jumlah ikan yang diminta melebihi stok sehat.

    Attributes:
        jenis_ikan: jenis ikan yang diminta.
        stok_tersedia: jumlah stok sehat yang tersedia.
        jumlah_diminta: jumlah yang diminta pembeli.
    """

    def __init__(
        self,
        jenis_ikan: str,
        stok_tersedia: int,
        jumlah_diminta: int,
    ) -> None:
        self.jenis_ikan = jenis_ikan
        self.stok_tersedia = stok_tersedia
        self.jumlah_diminta = jumlah_diminta
        super().__init__(
            f"Stok {jenis_ikan} tidak cukup: "
            f"tersedia {stok_tersedia}, diminta {jumlah_diminta}"
        )


class DataTidakValidError(HiaskanBaseError):
    """Dilempar saat data input gagal validasi aturan bisnis.

    Attributes:
        field: nama field yang tidak valid.
        pesan: penjelasan kesalahan.
    """

    def __init__(self, field: str, pesan: str) -> None:
        self.field = field
        self.pesan = pesan
        super().__init__(f"Data tidak valid [{field}]: {pesan}")


class FileOperasiError(HiaskanBaseError):
    """Dilempar saat operasi file (baca/tulis/hapus) gagal.

    Attributes:
        filepath: path file yang bermasalah.
        operasi: jenis operasi (baca/tulis/hapus).
        penyebab: exception asli yang menyebabkan kegagalan.
    """

    def __init__(
        self,
        filepath: str,
        operasi: str,
        penyebab: Exception | None = None,
    ) -> None:
        self.filepath = filepath
        self.operasi = operasi
        self.penyebab = penyebab
        detail = f" — {penyebab}" if penyebab else ""
        super().__init__(
            f"Gagal {operasi} file '{filepath}'{detail}"
        )
