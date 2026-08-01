# OpenCode Agents Instructions

This repository is a web application for managing ornamental fish breeding and sales. It uses **Python 3.11+**, **Streamlit**, and a localized JSON/CSV data store instead of a traditional SQL database.

## Essential Commands
- **Run the app:** `streamlit run app.py`
- **Run tests:** `python -m pytest tests/ -v`

## Architecture & Boundaries
- **UI (Streamlit):** Handled entirely in the `ui/` directory. `components.py` holds shared helpers (colors, CSS, DataFrame converters, KPI cards). Each page (`dashboard.py`, `ikan.py`, `kolam.py`, `pakan.py`, `pemijahan.py`, `penjualan.py`, `pelanggan.py`, `laporan.py`) contains a `render()` function registered via `st.navigation` in `app.py`. Do not mix business logic into page render functions — call services only.
- **Data Persistence:** Managed *exclusively* via `services/file_handler.py`. It handles JSON (for fish, ponds, customers) and CSV (for sales records) operations. Data files live in `data/`. Because pages read/write the same files on every rerun, the UI is always in sync with the data on disk.
- **Strategy Pattern (Pricing):** Fish pricing is determined dynamically using the Strategy pattern (`strategies/harga_strategy.py`). 
- **Open/Closed Principle (OCP):** To add a new fish type (e.g., Arwana), create a new subclass in `models/ikan.py` and a new pricing strategy in `strategies/harga_strategy.py`. Do not modify existing service logic to accommodate new types.

## Development Quirks
- Virtual environment is created at `.venv`. Be aware that activation commands differ slightly depending on the user's shell (e.g., fish shell).
- Custom domain exceptions are defined in `exceptions/custom_errors.py` (e.g., `StokIkanTidakCukupError`). Catch `HiaskanBaseError` in UI code to show error messages via `st.error`.
- Keep `requirements.txt` strictly to external dependencies (`streamlit`, `plotly`, `pandas`, `pytest`). Built-in libraries do not belong there.
- `@st.dialog` is used for add/edit forms; seed widget values via `st.session_state` with a per-page prefix (e.g., `ikan_`) before rendering widgets. Use `comp.sukses_rerun()` after successful mutations.
- Widgets with a `key` must not be assigned via `st.session_state`; keep mutable state in separate keys (see the sales cart in `ui/penjualan.py`).
