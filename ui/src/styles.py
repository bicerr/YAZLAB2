
# ==========================================
# COLOR PALETTE (Sosialex - Midnight Blue)
# ==========================================
COLORS = {
    "background": "#0b1622",      # Deep Midnight
    "panel": "#111f2e",           # Panel Background
    "header": "#081018",          # Header Background
    "border": "#2c3e50",          # Borders
    "text": "#e2e8f0",            # Primary Text (Light Grey)
    "text_muted": "#64748b",      # Muted Text
    "accent_blue": "#0ea5e9",     # Sky Blue (Icons/Highlights)
    "accent_cyan": "#06b6d4",     # Cyan
    "accent_green": "#10b981",    # Success
    "glass_bg": "rgba(255, 255, 255, 0.03)", # Glass effect
    "glass_border": "rgba(255, 255, 255, 0.08)",
    "input_bg": "#0f2336"
}

# ==========================================
# STYLESHEETS (QSS)
# ==========================================

MAIN_APP_STYLE = f"""
    QMainWindow {{
        background-color: {COLORS["background"]};
    }}
    QWidget {{
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        color: {COLORS["text"]};
        font-size: 12px;
    }}
    QScrollBar:vertical {{
        background: {COLORS["background"]};
        width: 8px;
        margin: 0px 20px 0 20px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS["border"]};
        min-height: 20px;
        border-radius: 4px;
    }}
    QDialog {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["border"]};
    }}
    QMessageBox {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["glass_border"]};
    }}
    QMessageBox QLabel {{
        color: {COLORS["text"]};
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        background-color: transparent;
    }}
    QMessageBox QPushButton {{
        background-color: {COLORS["input_bg"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 6px 20px;
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {COLORS["border"]};
        border: 1px solid {COLORS["accent_blue"]};
        color: white;
    }}
"""

PANEL_STYLE = f"""
    QFrame#Panel {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["glass_border"]};
        border-radius: 8px;
    }}
    QLabel#PanelTitle {{
        color: {COLORS["accent_blue"]};
        font-weight: bold;
        font-size: 13px;
        padding-bottom: 5px;
        border-bottom: 1px solid {COLORS["glass_border"]};
    }}
"""

HEADER_STYLE = f"""
    QFrame#Header {{
        background-color: {COLORS["header"]};
        border-bottom: 1px solid {COLORS["border"]};
    }}
    QLabel#AppTitle {{
        color: {COLORS["text"]};
        font-size: 18px;
        font-weight: bold;
        padding-left: 10px;
    }}
"""

BUTTON_STYLE = f"""
    QPushButton {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a2736, stop:1 #0f1924);
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        color: {COLORS["text"]};
        padding: 8px 10px;
        text-align: left;
    }}
    QPushButton:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #253344, stop:1 #1a2736);
        border: 1px solid {COLORS["accent_blue"]};
        color: white;
    }}
    QPushButton:pressed {{
        background-color: {COLORS["accent_blue"]};
        color: black;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {COLORS["input_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        color: {COLORS["text"]};
        padding: 5px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {COLORS["accent_cyan"]};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS["input_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        gridline-color: {COLORS["border"]};
    }}
    QHeaderView::section {{
        background-color: {COLORS["panel"]};
        color: {COLORS["text_muted"]};
        border: none;
        padding: 4px;
    }}
"""
