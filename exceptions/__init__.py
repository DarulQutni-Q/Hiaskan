"""Modul custom exceptions untuk sistem Hiaskan."""

from .custom_errors import (
    HiaskanBaseError,
    KualitasAirBurukError,
    StokIkanTidakCukupError,
    DataTidakValidError,
    FileOperasiError,
)

__all__ = [
    "HiaskanBaseError",
    "KualitasAirBurukError",
    "StokIkanTidakCukupError",
    "DataTidakValidError",
    "FileOperasiError",
]
