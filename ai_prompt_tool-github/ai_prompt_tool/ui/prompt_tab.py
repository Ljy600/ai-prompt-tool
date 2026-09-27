import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QFileDialog, QLabel, QTextEdit, QFrame,
    QSplitter, QSizePolicy, QScrollArea
)
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt

from generators import PromptGenerator, RuleDocGenerator, collect_dir_files
from ui import style
from ui.log_panel import LogPanel
from i18n import t, i18n


class PromptTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def _section_label(self, text, key=None):
        label = QLabel(text)
        label.setStyleSheet(style.section_label_style())
        if key:
            setattr(self, f"_section_{key}", label)
        return label

    def _dim_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(style.dim_label_style())
        return label

    def _card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(style.card_style())
        return card

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {style.COLOR_BORDER};
            }}
            QSplitter {{
                background: transparent;
            }}
        """)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([520, 440])

        outer.addWidget(splitter, 1)

        self.work_dir = None

    def retranslate(self):
        """语言切换后刷新界面文本。"""
        self.dir_label.setText(t("work.dir.unselected") if not self.work_dir
                               else t("work.dir.label", path=self.work_dir))
        self.btn_choose_dir.setText(t("work.dir.choose"))
        self._title_label.setText(t("tab.prompt"))
        self._section_req.setText(t("prompt.section"))
        self._section_output.setText(t("output.section"))
        self._section_preview.setText(t("preview.section"))
        self.btn_generate.setText(t("btn.generate"))
        self.btn_download.setText(t("btn.download_rule_doc"))
        self.btn_download_dir_doc.setText(t("btn.download_dir_doc"))
        self.btn_copy.setText(t("btn.copy"))
        self.input_edit.setPlaceholderText(t("prompt.input.placeholder"))
        self.output_edit.setPlaceholderText(t("output.placeholder"))
        self.preview_edit.setPlaceholderText(t("preview.placeholder"))
        self.log_panel.retranslate()

    def _build_left_panel(self):
        left = QFrame()
        left.setStyleSheet("QFrame { background: transparent; border: none; }")
        outer_layout = QVBoxLayout(left)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        left_body = QFrame()
        left_body.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(left_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self._title_label = QLabel(t("tab.prompt"))
        self._title_label.setStyleSheet(style.title_label_style())
        header.addWidget(self._title_label)
        header.addStretch()
        layout.addLayout(header)

        dir_card = self._card()
        dir_layout = QHBoxLayout(dir_card)
        dir_layout.setContentsMargins(16, 10, 16, 10)
        dir_layout.setSpacing(12)
        self.dir_label = self._dim_label(t("work.dir.unselected"))
        dir_layout.addWidget(self.dir_label, 1)
        self.btn_choose_dir = QPushButton(t("work.dir.choose"))
        self.btn_choose_dir.setStyleSheet(style.accent_button_style())
        self.btn_choose_dir.clicked.connect(self.on_choose_dir)
        dir_layout.addWidget(self.btn_choose_dir)
        layout.addWidget(dir_card)

        input_card = self._card()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(16, 14, 16, 14)
        input_layout.setSpacing(8)

        input_layout.addWidget(self._section_label(t("prompt.section"), "req"))
        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText(t("prompt.input.placeholder"))
        self.input_edit.setFixedHeight(90)
        input_layout.addWidget(self.input_edit)

        layout.addWidget(input_card)

        action_card = self._card()
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(16, 10, 16, 10)
        action_layout.setSpacing(10)

        self.btn_generate = QPushButton(t("btn.generate"))
        self.btn_generate.setStyleSheet(style.primary_button_style())
        self.btn_generate.clicked.connect(self.on_generate)
        self.btn_generate.setMinimumWidth(110)
        action_layout.addWidget(self.btn_generate)

        self.btn_download = QPushButton(t("btn.download_rule_doc"))
        self.btn_download.setStyleSheet(style.accent_button_style())
        self.btn_download.clicked.connect(self.on_download_rule_doc)
        action_layout.addWidget(self.btn_download)

        self.btn_download_dir_doc = QPushButton(t("btn.download_dir_doc"))
        self.btn_download_dir_doc.setStyleSheet(style.accent_button_style())
        self.btn_download_dir_doc.clicked.connect(self.on_download_dir_doc)
        action_layout.addWidget(self.btn_download_dir_doc)

        self.btn_copy = QPushButton(t("btn.copy"))
        self.btn_copy.setStyleSheet(style.accent_button_style())
        self.btn_copy.clicked.connect(self.on_copy)
        action_layout.addWidget(self.btn_copy)

        action_layout.addStretch()
        layout.addWidget(action_card)

        output_card = self._card()
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(16, 14, 16, 14)
        output_layout.setSpacing(8)

        output_header = QHBoxLayout()
        output_header.addWidget(self._section_label(t("output.section"), "output"))
        output_header.addStretch()
        output_layout.addLayout(output_header)

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText(t("output.placeholder"))
        output_layout.addWidget(self.output_edit)

        layout.addWidget(output_card)

        preview_card = self._card()
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(16, 14, 16, 14)
        preview_layout.setSpacing(8)

        preview_header = QHBoxLayout()
        preview_header.addWidget(self._section_label(t("preview.section"), "preview"))
        preview_header.addStretch()
        preview_layout.addLayout(preview_header)

        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setPlaceholderText(t("preview.placeholder"))
        self.preview_edit.setFixedHeight(140)
        preview_layout.addWidget(self.preview_edit)

        layout.addWidget(preview_card)

        scroll.setWidget(left_body)
        outer_layout.addWidget(scroll)

        return left

    def _build_right_panel(self):
        self.log_panel = LogPanel(title=t("log.title"))
        return self.log_panel

    def _log(self, level, op_type, detail):
        self.log_panel.log(level, op_type, detail)

    def on_choose_dir(self):
        path = QFileDialog.getExistingDirectory(self, t("work.dir.choose"))
        if path:
            self.work_dir = path
            self.dir_label.setText(t("work.dir.label", path=path))
            main_win = self._find_main_window()
            if main_win:
                main_win.set_shared_work_dir(path)
            self._log("info", "SETUP", t("log.setup.dir", path=path))

    def on_generate(self):
        requirement = self.input_edit.toPlainText()
        if not requirement.strip():
            self._log("error", "PROMPT", t("log.req.empty"))
            return
        if not self.work_dir:
            self._log("error", "PROMPT", t("log.req.no_dir"))
            self._flash_status(t("log.req.no_dir_hint"))
            return
        generator = PromptGenerator()
        result = generator.generate(requirement, i18n.current)
        self.output_edit.setPlainText(result)

        rule_doc = RuleDocGenerator()
        doc_content = rule_doc.generate(i18n.current)
        self.preview_edit.setPlainText(doc_content)

        self._log("success", "PROMPT", t("log.prompt.ok", n=len(result)))
        self._flash_status(t("log.prompt.ok_hint"))

    def on_download_rule_doc(self):
        if not self.work_dir:
            self._log("error", "DOWNLOAD", t("log.dl.no_dir"))
            self._flash_status(t("log.req.no_dir_hint"))
            return
        generator = RuleDocGenerator()
        content = generator.generate(i18n.current)
        path, _ = QFileDialog.getSaveFileName(
            self, t("btn.download_rule_doc"), "ai_generation_rules.txt", "Text file (*.txt)"
        )
        if not path:
            self._log("info", "DOWNLOAD", t("log.dl.cancel_rule"))
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.preview_edit.setPlainText(content)
        name = os.path.basename(path)
        self._log("success", "DOWNLOAD", t("log.dl.ok_rule", name=name))
        self._flash_status(t("log.dl.ok_rule_hint", name=name))

    def on_download_dir_doc(self):
        if not self.work_dir:
            self._log("error", "DOWNLOAD", t("log.dl.no_dir"))
            self._flash_status(t("log.req.no_dir_hint"))
            return
        content = collect_dir_files(self.work_dir, i18n.current)
        default = "目录文件内容.txt" if i18n.current == "zh" else "directory_contents.txt"
        path, _ = QFileDialog.getSaveFileName(
            self, t("btn.download_dir_doc"), default, "Text file (*.txt)"
        )
        if not path:
            self._log("info", "DOWNLOAD", t("log.dl.cancel_dir"))
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        name = os.path.basename(path)
        self._log("success", "DOWNLOAD", t("log.dl.ok_dir", name=name))
        self._flash_status(t("log.dl.ok_dir_hint", name=name))

    def on_copy(self):
        text = self.output_edit.toPlainText()
        if not text:
            self._log("error", "COPY", t("log.copy.empty"))
            self._flash_status(t("log.copy.empty"))
            return
        QGuiApplication.clipboard().setText(text)
        self._log("success", "COPY", t("log.copy.ok"))
        self._flash_status(t("log.copy.ok_hint"))

    def _find_main_window(self):
        from PyQt5.QtWidgets import QMainWindow
        p = self.parent()
        while p:
            if isinstance(p, QMainWindow) and hasattr(p, "set_shared_work_dir"):
                return p
            p = p.parent()
        return None

    def _flash_status(self, msg):
        p = self.parent()
        while p:
            if hasattr(p, "statusBar"):
                p.statusBar().showMessage(msg, 4000)
                return
            p = p.parent()
