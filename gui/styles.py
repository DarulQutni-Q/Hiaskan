"""
Stylesheet minimalis untuk GUI Hiaskan.

Palet: putih bersih, abu-abu lembut, aksen biru teal.
Tipografi: system font, bersih, tanpa ornamen berlebih.
"""

COLORS = {
    "bg": "#FAFAFA",
    "surface": "#FFFFFF",
    "border": "#E0E0E0",
    "border_focus": "#26A69A",
    "text": "#212121",
    "text_secondary": "#757575",
    "accent": "#26A69A",
    "accent_hover": "#00897B",
    "accent_pressed": "#00796B",
    "danger": "#E53935",
    "danger_hover": "#C62828",
    "success": "#43A047",
    "warning": "#FB8C00",
    "tab_active_bg": "#FFFFFF",
    "tab_inactive_bg": "#F5F5F5",
    "header_bg": "#26A69A",
    "header_text": "#FFFFFF",
    "row_alt": "#FAFAFA",
    "selection": "#B2DFDB",
}

STYLESHEET = f"""
/* ---- Global ---- */
QMainWindow, QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: "Segoe UI", "Inter", "SF Pro Display", system-ui, sans-serif;
    font-size: 13px;
}}

/* ---- Tab Widget ---- */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background: {COLORS['surface']};
    margin-top: -1px;
}}
QTabBar::tab {{
    background: {COLORS['tab_inactive_bg']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    padding: 10px 22px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {COLORS['tab_active_bg']};
    color: {COLORS['accent']};
    border-bottom: 2px solid {COLORS['accent']};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    background: {COLORS['surface']};
    color: {COLORS['text']};
}}

/* ---- Table ---- */
QTableWidget {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    gridline-color: {COLORS['border']};
    selection-background-color: {COLORS['selection']};
    selection-color: {COLORS['text']};
    alternate-background-color: {COLORS['row_alt']};
}}
QTableWidget::item {{
    padding: 6px 10px;
}}
QHeaderView::section {{
    background: {COLORS['bg']};
    color: {COLORS['text']};
    font-weight: 600;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid {COLORS['border']};
    border-right: 1px solid {COLORS['border']};
}}

/* ---- Buttons ---- */
QPushButton {{
    background: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {COLORS['accent_hover']};
}}
QPushButton:pressed {{
    background: {COLORS['accent_pressed']};
}}
QPushButton:disabled {{
    background: {COLORS['border']};
    color: {COLORS['text_secondary']};
}}
QPushButton[class="danger"] {{
    background: {COLORS['danger']};
}}
QPushButton[class="danger"]:hover {{
    background: {COLORS['danger_hover']};
}}
QPushButton[class="secondary"] {{
    background: transparent;
    color: {COLORS['accent']};
    border: 1px solid {COLORS['accent']};
}}
QPushButton[class="secondary"]:hover {{
    background: {COLORS['selection']};
}}

/* ---- Inputs ---- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    background: {COLORS['surface']};
    color: {COLORS['text']};
    font-size: 13px;
    min-height: 20px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QTextEdit:focus {{
    border-color: {COLORS['border_focus']};
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    selection-background-color: {COLORS['selection']};
    padding: 4px;
}}

/* ---- Labels ---- */
QLabel {{
    color: {COLORS['text']};
}}
QLabel[class="heading"] {{
    font-size: 18px;
    font-weight: 700;
    color: {COLORS['text']};
    padding: 4px 0;
}}
QLabel[class="subheading"] {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}
QLabel[class="stat-value"] {{
    font-size: 24px;
    font-weight: 700;
    color: {COLORS['accent']};
}}
QLabel[class="stat-label"] {{
    font-size: 11px;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
}}

/* ---- Group Box ---- */
QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 20px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    color: {COLORS['accent']};
}}

/* ---- Status Bar ---- */
QStatusBar {{
    background: {COLORS['surface']};
    border-top: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
    font-size: 12px;
    padding: 4px 12px;
}}

/* ---- Scroll Bar ---- */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_secondary']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ---- Dialog ---- */
QDialog {{
    background: {COLORS['surface']};
}}

/* ---- Message Box ---- */
QMessageBox {{
    background: {COLORS['surface']};
}}
"""
