"""国际化（i18n）模块：提供中/英文切换与全局文本检索。

设计原则：
- 以 key 检索文本（key 稳定，不随语言变化），避免把中文文本本身作为 dict key。
- `current` 全局默认 "zh"；`set_current` 供语言切换调用。
- `t(key)` 默认按当前语言取文本；`t(key, lang)` 指定语言。
- 支持 `{...}` 占位符：先按当前语言取模板，再 format，避免占位符与语言混用。
- `change_event` 供 UI 在语言切换后刷新界面（QSignal）。
"""

from PyQt5.QtCore import QObject, pyqtSignal

__all__ = ["i18n", "I18N", "t"]

DEFAULT_LANG = "zh"
SUPPORTED = ("zh", "en")


class I18N(QObject):
    change_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current = DEFAULT_LANG

    def set_current(self, lang: str):
        lang = lang if lang in SUPPORTED else DEFAULT_LANG
        if lang != self.current:
            self.current = lang
            self.change_event.emit(lang)

    def get(self, key: str, lang: str = None) -> str:
        lang = lang or self.current
        if lang not in _DICTS:
            lang = DEFAULT_LANG
        return _DICTS[lang].get(key, key)

    def translate(self, key: str, lang: str = None, **kwargs) -> str:
        """返回带占位符替换后的文本。"""
        return self.get(key, lang).format(**kwargs)


_DICTS = {
    "zh": {
        "app.title": "AI 提示词工具",
        "tab.prompt": "生成提示词",
        "tab.execute": "导入并执行",
        "status.ready": "就绪",
        "work.dir.label": "工作目录: {path}",
        "work.dir.choose": "选择目录",
        "work.dir.unselected": "工作目录: 未选择",
        "prompt.section": "需求描述",
        "prompt.input.placeholder": "请输入需求描述，例如：帮我创建一个 Python 项目...",
        "btn.generate": "生成提示词",
        "btn.download_rule_doc": "下载规则文档",
        "btn.download_dir_doc": "下载目录文件内容",
        "btn.copy": "复制提示词",
        "output.section": "提示词输出",
        "output.placeholder": "点击「生成提示词」按钮后显示结果...",
        "preview.section": "规则文档预览",
        "preview.placeholder": "点击「下载规则文档」按钮后显示内容...",
        "execute.section.input": "AI 回复内容",
        "execute.input.placeholder": "请粘贴 AI 回复内容，须包含 [CREATE:] [EDIT:] [DELETE:] [URL:] [DOWNLOAD:] [CODE:] [DATA:] 等标记...",
        "execute.section.result": "执行结果",
        "execute.result.placeholder": "点击「解析并执行」或「仅解析预览」后显示结果...",
        "btn.parse_execute": "解析并执行",
        "btn.preview": "仅解析预览",
        "btn.clear": "清除",
        "log.title": "AI 操作日志",
        "log.clear": "清空",
        "log.placeholder": "这里会显示 AI 的每次操作记录，包括时间、操作类型和结果详情...",
        "confirm.title": "确认执行",
        "confirm.message": (
            "即将执行 {total} 条指令（含文件写入/删除操作）\n"
            "工作目录: {work_dir}\n\n"
            "⚠️ 修改文件会自动备份为 .bak；删除不可撤销。\n确认执行？"
        ),
        "log.req.empty": "需求描述为空，无法生成",
        "log.req.no_dir": "请先选择工作目录，再生成提示词",
        "log.req.no_dir_hint": "请先选择工作目录",
        "log.prompt.ok": "提示词已生成（{n} 字符）",
        "log.prompt.ok_hint": "提示词已生成，请复制或下载文档后发给 AI",
        "log.dl.no_dir": "请先选择工作目录，再生成文档",
        "log.dl.cancel_rule": "取消保存规则文档",
        "log.dl.ok_rule": "规则文档已保存: {name}",
        "log.dl.ok_rule_hint": "规则文档已保存: {name}",
        "log.dl.cancel_dir": "取消保存目录文件内容",
        "log.dl.ok_dir": "目录文件内容已保存: {name}",
        "log.dl.ok_dir_hint": "目录文件内容已保存: {name}",
        "log.copy.empty": "提示词输出为空，无法复制",
        "log.copy.ok": "提示词已复制到剪贴板",
        "log.copy.ok_hint": "提示词已复制到剪贴板",
        "log.setup.dir": "工作目录设为: {path}",
        "log.input.empty": "AI 回复内容为空，无法执行",
        "log.input.empty_hint": "请先粘贴 AI 回复内容",
        "log.parse.err": "校验失败，共 {n} 个错误",
        "log.parse.err_hint": "校验失败: {n} 个错误",
        "log.parse.no_mark": "未找到任何指令标记",
        "log.parse.no_mark_hint": "未找到任何指令标记",
        "log.exec.cancel": "已取消执行",
        "log.exec.cancel_hint": "已取消执行",
        "log.summary": "共 {total} 条指令: {success} 成功, {fail} 失败",
        "log.preview.done": "解析预览完成",
        "log.clear.done": "已清空输入和结果",
        "log.clear.done_hint": "已清除",
        "result.err.line": "❌ 第 {line} 行: {msg}，请让 AI 重新生成",
        "result.err.block": "⚠️ 校验失败，无法执行。请让 AI 按规则重新生成。",
        "result.no_mark": "❌ 未找到任何指令标记",
        "result.list.title": "解析到的指令列表:",
        "result.list.item": "  {i}. [{type}] {param} (第 {line} 行)",
        "result.summary": "共 {total} 条指令: {success} 成功, {fail} 失败",
        "status.exec.done": "执行完成: {success} 成功, {fail} 失败",
        "parse.err.title": "校验失败",
        "parse.err.no_mark": "未找到任何指令标记",
    },
    "en": {
        "app.title": "AI Prompt Tool",
        "tab.prompt": "Generate Prompt",
        "tab.execute": "Import & Execute",
        "status.ready": "Ready",
        "work.dir.label": "Working directory: {path}",
        "work.dir.choose": "Choose directory",
        "work.dir.unselected": "Working directory: not selected",
        "prompt.section": "Requirement",
        "prompt.input.placeholder": "Enter your requirement, e.g.: create a Python project for me...",
        "btn.generate": "Generate Prompt",
        "btn.download_rule_doc": "Download Rules Doc",
        "btn.download_dir_doc": "Download Directory Contents",
        "btn.copy": "Copy Prompt",
        "output.section": "Prompt Output",
        "output.placeholder": "Click \u201cGenerate Prompt\u201d to see the result...",
        "preview.section": "Rules Doc Preview",
        "preview.placeholder": "Click \u201cDownload Rules Doc\u201d to view content...",
        "execute.section.input": "AI Response Content",
        "execute.input.placeholder": (
            "Paste the AI response here. It must contain markers like "
            "[CREATE:] [EDIT:] [DELETE:] [URL:] [DOWNLOAD:] [CODE:] [DATA:] ..."
        ),
        "execute.section.result": "Execution Result",
        "execute.result.placeholder": "Click \u201cParse & Execute\u201d or \u201cPreview Only\u201d to see results...",
        "btn.parse_execute": "Parse & Execute",
        "btn.preview": "Preview Only",
        "btn.clear": "Clear",
        "log.title": "AI Operation Log",
        "log.clear": "Clear",
        "log.placeholder": "Each AI operation will be recorded here with time, type and result details...",
        "confirm.title": "Confirm Execution",
        "confirm.message": (
            "About to execute {total} instructions (includes file write/delete operations)\n"
            "Working directory: {work_dir}\n\n"
            "\u26a0\ufe0f File edits are auto-backed up as .bak; deletion is irreversible.\nConfirm execution?"
        ),
        "log.req.empty": "Requirement is empty, cannot generate",
        "log.req.no_dir": "Please select a working directory first",
        "log.req.no_dir_hint": "Please select a working directory first",
        "log.prompt.ok": "Prompt generated ({n} chars)",
        "log.prompt.ok_hint": "Prompt generated. Copy it or download the docs and send to AI",
        "log.dl.no_dir": "Please select a working directory first",
        "log.dl.cancel_rule": "Saved rules doc cancelled",
        "log.dl.ok_rule": "Rules doc saved: {name}",
        "log.dl.ok_rule_hint": "Rules doc saved: {name}",
        "log.dl.cancel_dir": "Saved directory contents cancelled",
        "log.dl.ok_dir": "Directory contents saved: {name}",
        "log.dl.ok_dir_hint": "Directory contents saved: {name}",
        "log.copy.empty": "Prompt output is empty, nothing to copy",
        "log.copy.ok": "Prompt copied to clipboard",
        "log.copy.ok_hint": "Prompt copied to clipboard",
        "log.setup.dir": "Working directory set to: {path}",
        "log.input.empty": "AI response is empty, cannot execute",
        "log.input.empty_hint": "Please paste the AI response first",
        "log.parse.err": "Validation failed, {n} error(s)",
        "log.parse.err_hint": "Validation failed: {n} error(s)",
        "log.parse.no_mark": "No instruction markers found",
        "log.parse.no_mark_hint": "No instruction markers found",
        "log.exec.cancel": "Execution cancelled",
        "log.exec.cancel_hint": "Execution cancelled",
        "log.summary": "Total {total} instructions: {success} succeeded, {fail} failed",
        "log.preview.done": "Parse preview done",
        "log.clear.done": "Input and results cleared",
        "log.clear.done_hint": "Cleared",
        "result.err.line": "\u274c Line {line}: {msg}, please let AI regenerate",
        "result.err.block": "\u26a0\ufe0f Validation failed, cannot execute. Ask the AI to regenerate per the rules.",
        "result.no_mark": "\u274c No instruction markers found",
        "result.list.title": "Parsed instructions:",
        "result.list.item": "  {i}. [{type}] {param} (line {line})",
        "result.summary": "Total {total} instructions: {success} succeeded, {fail} failed",
        "status.exec.done": "Execution done: {success} succeeded, {fail} failed",
        "parse.err.title": "Validation failed",
        "parse.err.no_mark": "No instruction markers found",
    },
}


i18n = I18N()


def t(key: str, lang: str = None, **kwargs) -> str:
    """返回带占位符替换后的文本。kwargs 为空时等价于 i18n.get。"""
    if kwargs:
        return i18n.translate(key, lang, **kwargs)
    return i18n.get(key, lang)
