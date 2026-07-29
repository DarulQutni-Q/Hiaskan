# OpenCode Agents Instructions

This repository is a desktop application for managing ornamental fish breeding and sales. It uses **Python 3.11+**, **PyQt6**, and a localized JSON/CSV data store instead of a traditional SQL database.

## Essential Commands
- **Run the app:** `python main.py`
- **Run tests:** `python -m pytest tests/ -v`

## Architecture & Boundaries
- **GUI (PyQt6):** Handled entirely in the `gui/` directory. `main_window.py` contains the tab layouts, while `dialogs.py` contains the popup forms. Do not mix business logic into GUI event handlers.
- **Data Persistence:** Managed *exclusively* via `services/file_handler.py`. It handles JSON (for fish, ponds, customers) and CSV (for sales records) operations. Data files live in `data/`.
- **Strategy Pattern (Pricing):** Fish pricing is determined dynamically using the Strategy pattern (`strategies/harga_strategy.py`). 
- **Open/Closed Principle (OCP):** To add a new fish type (e.g., Arwana), create a new subclass in `models/ikan.py` and a new pricing strategy in `strategies/harga_strategy.py`. Do not modify existing service logic to accommodate new types.

## Development Quirks
- Virtual environment is created at `.venv`. Be aware that activation commands differ slightly depending on the user's shell (e.g., fish shell).
- Custom domain exceptions are defined in `exceptions/custom_errors.py` (e.g., `StokIkanTidakCukupError`).
- Keep `requirements.txt` strictly to external dependencies (`PyQt6`, `pytest`). Built-in libraries like `tkinter` do not belong there.
