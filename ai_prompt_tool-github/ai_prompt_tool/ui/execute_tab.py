import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QLabel, QTextEdit, QFileDialog, QFrame,
    QSplitter, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt

from parsers import AIParser
from executors import WorkflowExecutor
from ui import style
from ui.log_panel import LogPanel
from i18n import t, i18n


class ExecuteTab(QWidget):
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

        self.work_dir = os.getcwd()

    def retranslate(self):
        """语言切换后刷新界面文本。"""
        self.dir_label.setText(t("work.dir.unselected") if not self.work_dir
                               else t("work.dir.label", path=self.work_dir))
        self.btn_choose_dir.setText(t("work.dir.choose"))
        self._title_label.setText(t("tab.execute"))
        self._section_input.setText(t("execute.section.input"))
        self._section_result.setText(t("execute.section.result"))
        self.btn_parse_execute.setText(t("btn.parse_execute"))
        self.btn_preview.setText(t("btn.preview"))
        self.btn_clear.setText(t("btn.clear"))
        self.input_edit.setPlaceholderText(t("execute.input.placeholder"))
        self.result_edit.setPlaceholderText(t("execute.result.placeholder"))
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
        self._title_label = QLabel(t("tab.execute"))
        self._title_label.setStyleSheet(style.title_label_style())
        header.addWidget(self._title_label)
        header.addStretch()
        layout.addLayout(header)

        input_card = self._card()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(16, 14, 16, 14)
        input_layout.setSpacing(8)
        input_layout.addWidget(self._section_label(t("execute.section.input"), "input"))
        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText(t("execute.input.placeholder"))
        self.input_edit.setFixedHeight(100)
        input_layout.addWidget(self.input_edit)
        layout.addWidget(input_card)

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

        action_card = self._card()
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(16, 10, 16, 10)
        action_layout.setSpacing(10)

        self.btn_parse_execute = QPushButton(t("btn.parse_execute"))
        self.btn_parse_execute.setStyleSheet(style.primary_button_style())
        self.btn_parse_execute.clicked.connect(self.on_parse_execute)
        self.btn_parse_execute.setMinimumWidth(110)
        action_layout.addWidget(self.btn_parse_execute)

        self.btn_preview = QPushButton(t("btn.preview"))
        self.btn_preview.setStyleSheet(style.accent_button_style())
        self.btn_preview.clicked.connect(self.on_preview)
        action_layout.addWidget(self.btn_preview)

        self.btn_clear = QPushButton(t("btn.clear"))
        self.btn_clear.setStyleSheet(style.danger_button_style())
        self.btn_clear.clicked.connect(self.on_clear)
        action_layout.addWidget(self.btn_clear)

        action_layout.addStretch()
        layout.addWidget(action_card)

        result_card = self._card()
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(16, 14, 16, 14)
        result_layout.setSpacing(8)
        result_layout.addWidget(self._section_label(t("execute.section.result"), "result"))
        self.result_edit = QTextEdit()
        self.result_edit.setReadOnly(True)
        self.result_edit.setPlaceholderText(t("execute.result.placeholder"))
        result_layout.addWidget(self.result_edit)
        layout.addWidget(result_card)

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

    def on_parse_execute(self):
        text = self.input_edit.toPlainText()
        if not text.strip():
            self._log("error", "INPUT", t("log.input.empty"))
            self._flash_status(t("log.input.empty_hint"))
            return

        work_dir = self._ensure_work_dir()
        if not work_dir:
            return

        parser = AIParser()
        parsed = parser.parse(text)
        if parsed.errors:
            self.result_edit.clear()
            for err in parsed.errors:
                self.result_edit.append(
                    f'<div style="color:{style.COLOR_ERROR};">{t("result.err.line", line=err.line, msg=err.message)}</div>'
                )
            self.result_edit.append(
                f'<div style="color:{style.COLOR_WARNING}; margin-top:8px;">{t("result.err.block")}</div>'
            )
            self._log("error", "PARSE", t("log.parse.err", n=len(parsed.errors)))
            self._flash_status(t("log.parse.err_hint", n=len(parsed.errors)))
            return
        if not parsed.instructions:
            self.result_edit.clear()
            self.result_edit.append(
                f'<div style="color:{style.COLOR_ERROR};">{t("result.no_mark")}</div>'
            )
            self._log("error", "PARSE", t("log.parse.no_mark"))
            self._flash_status(t("log.parse.no_mark_hint"))
            return

        confirm = self._confirm_execute(parsed, work_dir)
        if not confirm:
            self._log("info", "EXECUTE", t("log.exec.cancel"))
            self._flash_status(t("log.exec.cancel_hint"))
            return

        executor = WorkflowExecutor()
        results = executor.execute(parsed.instructions, work_dir)
        self._render_results(results, len(parsed.instructions))
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count
        self._flash_status(t("status.exec.done", success=success_count, fail=fail_count))

    def _ensure_work_dir(self):
        if not self.work_dir or not os.path.isdir(self.work_dir):
            self._log("error", "SETUP", t("log.req.no_dir"))
            self._flash_status(t("log.req.no_dir_hint"))
            return ""
        return self.work_dir

    def _confirm_execute(self, parsed, work_dir):
        from PyQt5.QtWidgets import QMessageBox
        has_write_op = any(inst.type in ("CREATE", "EDIT", "DELETE", "CODE", "DATA", "DOWNLOAD") for inst in parsed.instructions)
        if not has_write_op:
            return True
        msg = t("confirm.message", total=len(parsed.instructions), work_dir=work_dir)
        ret = QMessageBox.question(
            self, t("confirm.title"), msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return ret == QMessageBox.Yes

    def _render_results(self, results, total):
        self.result_edit.clear()
        for result in results:
            if result.success:
                mark = "✅"
                mark_color = style.COLOR_SUCCESS
            else:
                mark = "❌"
                mark_color = style.COLOR_ERROR
            self.result_edit.append(
                f'<div style="color:{mark_color};">{mark} [{result.instruction_type}] {result.message}</div>'
            )
            level = "success" if result.success else "error"
            self._log(level, result.instruction_type, result.message)
        success_count = sum(1 for r in results if r.success)
        fail_count = total - success_count
        self.result_edit.append(
            f'<div style="color:{style.COLOR_TEXT_DIM}; margin-top:8px; border-top: 1px solid {style.COLOR_BORDER}; padding-top:8px;">'
            f'{t("result.summary", total=total, success=success_count, fail=fail_count)}</div>'
        )
        self._log("info", "SUMMARY", t("log.summary", total=total, success=success_count, fail=fail_count))

    def on_preview(self):
        text = self.input_edit.toPlainText()
        if not text.strip():
            self._log("error", "INPUT", t("log.input.empty"))
            self._flash_status(t("log.input.empty_hint"))
            return
        parser = AIParser()
        parsed = parser.parse(text)
        self.result_edit.clear()
        if parsed.errors:
            for err in parsed.errors:
                self.result_edit.append(
                    f'<div style="color:{style.COLOR_ERROR};">{t("result.err.line", line=err.line, msg=err.message)}</div>'
                )
            self._log("error", "PARSE", t("log.parse.err", n=len(parsed.errors)))
        if parsed.instructions:
            self.result_edit.append(
                f'<div style="color:{style.COLOR_TEXT}; font-weight:700;">{t("result.list.title")}</div>'
            )
            for i, inst in enumerate(parsed.instructions, 1):
                self.result_edit.append(
                    f'<div style="color:{style.COLOR_TEXT_DIM};">{t("result.list.item", i=i, type=inst.type, param=inst.param, line=inst.line)}</div>'
                )
                self._log("info", inst.type, t("result.list.item", i=i, type=inst.type, param=inst.param, line=inst.line))
        if not parsed.errors and not parsed.instructions:
            self.result_edit.append(
                f'<div style="color:{style.COLOR_ERROR};">{t("result.no_mark")}</div>'
            )
            self._log("error", "PARSE", t("log.parse.no_mark"))
        self._flash_status(t("log.preview.done"))

    def on_clear(self):
        self.input_edit.clear()
        self.result_edit.clear()
        self._log("info", "CLEAR", t("log.clear.done"))
        self._flash_status(t("log.clear.done_hint"))

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
