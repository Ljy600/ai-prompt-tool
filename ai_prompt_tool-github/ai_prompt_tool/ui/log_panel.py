from datetime import datetime

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtGui import QTextCursor

from ui import style
from i18n import t


class LogPanel(QFrame):
    def __init__(self, title="AI 操作日志", parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background: transparent; border: none; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self._title_label = QLabel(title)
        self._title_label.setStyleSheet(style.title_label_style())
        header.addWidget(self._title_label)
        header.addStretch()

        layout.addLayout(header)

        log_card = QFrame()
        log_card.setObjectName("card")
        log_card.setStyleSheet(style.card_style())
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(0)

        self._log_edit = QTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setPlaceholderText(t("log.placeholder"))
        log_layout.addWidget(self._log_edit)

        layout.addWidget(log_card, 1)

        self._clear_btn = QPushButton(t("log.clear"))
        self._clear_btn.setStyleSheet(
            f"QPushButton {{ padding: 4px 12px; min-height: 28px; font-size: 12px; "
            f"background: transparent; border: 1px solid {style.COLOR_BORDER}; "
            f"border-radius: 6px; color: {style.COLOR_TEXT_DIM}; }}"
            f"QPushButton:hover {{ background: {style.COLOR_SURFACE_LIGHT}; }}"
        )
        self._clear_btn.clicked.connect(self._log_edit.clear)
        header.addWidget(self._clear_btn)

    def retranslate(self):
        """语言切换后刷新标题/清空按钮/占位符文本。"""
        self._title_label.setText(t("log.title"))
        self._clear_btn.setText(t("log.clear"))
        self._log_edit.setPlaceholderText(t("log.placeholder"))

    def log(self, level, op_type, detail):
        ts = datetime.now().strftime("%H:%M:%S")
        if level == "success":
            color = style.COLOR_SUCCESS
            icon = "✅"
        elif level == "error":
            color = style.COLOR_ERROR
            icon = "❌"
        else:
            color = style.COLOR_TEXT_DIM
            icon = "ℹ️"
        html = (
            f'<div style="padding:6px 12px; margin:2px 8px; border-radius:6px; '
            f'background:{style.COLOR_SURFACE_LIGHT}; font-family:'
            f'"{style.FONT_MONO.split(",")[0]}"; font-size:12px; color:{style.COLOR_TEXT};">'
            f'<span style="color:{style.COLOR_TEXT_MUTED};">{ts}</span> '
            f'<span style="color:{color}; font-weight:700;">{icon} [{op_type}]</span> '
            f'{detail}</div>'
        )
        self._log_edit.append(html)
        cursor = self._log_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self._log_edit.setTextCursor(cursor)
