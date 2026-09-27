from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

COLOR_BG = "#f5f6f8"
COLOR_SURFACE = "#ffffff"
COLOR_SURFACE_LIGHT = "#f0f1f5"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e2e4ea"
COLOR_PRIMARY = "#4f46e5"
COLOR_PRIMARY_HOVER = "#6366f1"
COLOR_PRIMARY_PRESSED = "#4338ca"
COLOR_ACCENT = "#0d9488"
COLOR_SUCCESS = "#16a34a"
COLOR_ERROR = "#dc2626"
COLOR_WARNING = "#d97706"
COLOR_TEXT = "#1e2033"
COLOR_TEXT_DIM = "#6b7280"
COLOR_TEXT_MUTED = "#9ca3af"

FONT_FAMILY = "Segoe UI, Microsoft YaHei, PingFang SC, sans-serif"
FONT_MONO = "Cascadia Code, Consolas, JetBrains Mono, monospace"


def make_font(size=13, bold=False, mono=False):
    family = FONT_MONO if mono else FONT_FAMILY
    font = QFont(family, size)
    font.setBold(bold)
    font.setStyleHint(Qt.PreferAntialias)
    return font


def global_stylesheet():
    return f"""
QMainWindow, QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-family: '{FONT_FAMILY}';
    font-size: 13px;
}}

QTabWidget::pane {{
    border: none;
    background: {COLOR_BG};
}}

QTabBar {{
    background: {COLOR_SURFACE};
    border-bottom: 1px solid {COLOR_BORDER};
}}

QTabBar::tab {{
    background: transparent;
    color: {COLOR_TEXT_DIM};
    padding: 12px 28px;
    border: none;
    border-bottom: 2px solid transparent;
    font-family: '{FONT_FAMILY}';
    font-size: 14px;
    font-weight: 600;
    min-height: 42px;
}}

QTabBar::tab:hover {{
    color: {COLOR_TEXT};
    background: {COLOR_SURFACE_LIGHT};
}}

QTabBar::tab:selected {{
    color: {COLOR_PRIMARY};
    background: {COLOR_SURFACE};
    border-bottom: 2px solid {COLOR_PRIMARY};
}}

QPlainTextEdit, QTextEdit {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLOR_TEXT};
    font-family: '{FONT_MONO}';
    font-size: 13px;
    selection-background-color: {COLOR_PRIMARY_HOVER};
    selection-color: #ffffff;
}}

QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLOR_PRIMARY};
    background: {COLOR_SURFACE};
}}

QPlainTextEdit:read-only, QTextEdit:read-only {{
    background: {COLOR_SURFACE_LIGHT};
    border: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_DIM};
}}

QPushButton {{
    background: {COLOR_SURFACE};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    min-height: 38px;
}}

QPushButton:hover {{
    background: {COLOR_SURFACE_LIGHT};
    border: 1px solid {COLOR_TEXT_MUTED};
}}

QPushButton:pressed {{
    background: {COLOR_SURFACE_LIGHT};
}}

QLabel {{
    color: {COLOR_TEXT_DIM};
    font-size: 13px;
}}

QStatusBar {{
    background: {COLOR_SURFACE};
    color: {COLOR_TEXT_DIM};
    border-top: 1px solid {COLOR_BORDER};
    font-size: 12px;
    min-height: 32px;
}}

QScrollBar:vertical {{
    background: {COLOR_BG};
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {COLOR_BG};
    height: 8px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {COLOR_BORDER};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QToolTip {{
    background: {COLOR_SURFACE};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""


def primary_button_style():
    return f"""
QPushButton {{
    background: {COLOR_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 700;
    min-height: 38px;
}}

QPushButton:hover {{
    background: {COLOR_PRIMARY_HOVER};
}}

QPushButton:pressed {{
    background: {COLOR_PRIMARY_PRESSED};
}}
"""


def accent_button_style():
    return f"""
QPushButton {{
    background: transparent;
    color: {COLOR_ACCENT};
    border: 1px solid {COLOR_ACCENT};
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    min-height: 38px;
}}

QPushButton:hover {{
    background: {COLOR_SURFACE_LIGHT};
}}

QPushButton:pressed {{
    background: {COLOR_SURFACE_LIGHT};
}}
"""


def danger_button_style():
    return f"""
QPushButton {{
    background: transparent;
    color: {COLOR_ERROR};
    border: 1px solid {COLOR_ERROR};
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    min-height: 38px;
}}

QPushButton:hover {{
    background: #fef2f2;
}}

QPushButton:pressed {{
    background: #fee2e2;
}}
"""


def card_style():
    return f"""
QWidget#card {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}
"""


def section_label_style():
    return f"""
QLabel {{
    color: {COLOR_TEXT};
    font-size: 14px;
    font-weight: 700;
    padding: 4px 0px;
}}
"""


def dim_label_style():
    return f"""
QLabel {{
    color: {COLOR_TEXT_DIM};
    font-size: 12px;
    font-weight: 400;
    padding: 2px 0px;
}}
"""


def title_label_style():
    return f"""
QLabel {{
    color: {COLOR_TEXT};
    font-size: 18px;
    font-weight: 700;
}}
"""
