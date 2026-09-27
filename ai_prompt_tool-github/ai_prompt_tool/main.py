import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout, QComboBox, QFrame
)
from PyQt5.QtCore import Qt

from ui.prompt_tab import PromptTab
from ui.execute_tab import ExecuteTab
from ui import style
from i18n import i18n, t


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("app.title"))
        self.resize(1100, 720)
        self.setMinimumSize(900, 560)

        self.shared_work_dir = os.getcwd()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.prompt_tab = PromptTab()
        self.execute_tab = ExecuteTab()

        self.prompt_tab.work_dir = self.shared_work_dir
        self.execute_tab.work_dir = self.shared_work_dir

        self._sync_dirs_on_tab_change = False
        self.tabs.currentChanged.connect(self._sync_work_dir)

        self.tabs.addTab(self.prompt_tab, t("tab.prompt"))
        self.tabs.addTab(self.execute_tab, t("tab.execute"))

        self._sync_work_dir()

        central = QWidget()
        vlayout = QVBoxLayout(central)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)

        # 顶部工具栏（语言切换）
        self._build_top_bar()
        vlayout.addWidget(self._top_bar)

        vlayout.addWidget(self.tabs, 1)
        self.setCentralWidget(central)

        self.statusBar().showMessage(t("status.ready"))

        app = QApplication.instance()
        if app:
            app.setStyleSheet(style.global_stylesheet())

        # 语言切换信号
        i18n.change_event.connect(self._on_language_changed)

    def _build_top_bar(self):
        self._top_bar = QFrame()
        self._top_bar.setFixedHeight(52)
        self._top_bar.setStyleSheet(
            f"QFrame {{ background: {style.COLOR_SURFACE}; border-bottom: 1px solid {style.COLOR_BORDER}; }}"
        )
        layout = QHBoxLayout(self._top_bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        app_title = QLabel(t("app.title"))
        app_title.setStyleSheet(
            f"color: {style.COLOR_TEXT}; font-size: 14px; font-weight: 700;"
        )
        layout.addWidget(app_title)
        layout.addStretch()

        lang_label = QLabel("语言 / Language")
        lang_label.setStyleSheet(f"color: {style.COLOR_TEXT_DIM}; font-size: 12px;")
        layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "English"])
        self.lang_combo.setCurrentIndex(0 if i18n.current == "zh" else 1)
        self.lang_combo.setFixedWidth(120)
        self.lang_combo.setStyleSheet(f"""
            QComboBox {{
                background: {style.COLOR_SURFACE_LIGHT};
                border: 1px solid {style.COLOR_BORDER};
                border-radius: 8px;
                padding: 6px 12px;
                min-height: 28px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {style.COLOR_CARD};
                border: 1px solid {style.COLOR_BORDER};
                selection-background-color: {style.COLOR_PRIMARY_HOVER};
                selection-color: #ffffff;
            }}
        """)
        self.lang_combo.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self.lang_combo)

    def _on_combo_changed(self, index):
        lang = "zh" if index == 0 else "en"
        i18n.set_current(lang)

    def _on_language_changed(self, lang):
        self.setWindowTitle(t("app.title"))
        self.tabs.setTabText(0, t("tab.prompt"))
        self.tabs.setTabText(1, t("tab.execute"))
        self.statusBar().showMessage(t("status.ready"))
        self.prompt_tab.retranslate()
        self.execute_tab.retranslate()

    def _sync_work_dir(self):
        src = self.tabs.currentWidget()
        dir_label = getattr(src, "dir_label", None)
        if dir_label:
            path = getattr(src, "work_dir", None) or self.shared_work_dir
            dir_label.setText(t("work.dir.unselected") if not path else t("work.dir.label", path=path))
            if hasattr(src, "work_dir"):
                src.work_dir = path
        self.shared_work_dir = getattr(src, "work_dir", self.shared_work_dir) or self.shared_work_dir

    def set_shared_work_dir(self, path):
        self.shared_work_dir = path
        for tab in [self.prompt_tab, self.execute_tab]:
            tab.work_dir = path
            tab.dir_label.setText(t("work.dir.label", path=path))


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(style.global_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
