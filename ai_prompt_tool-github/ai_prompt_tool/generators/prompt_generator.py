import os


_DIR_DOC_TPL = {
    "zh": {
        "header": "# 目录文件内容 ({path})\n",
        "empty_dir": "(目录为空)",
        "empty_file": "(空文件)",
        "too_large": "({size} 字节，文件过大已省略)",
        "read_fail": "(读取失败: {err})",
        "omit_more": "\n... (更多文件已省略)",
        "footer": "\n---\n共 {n} 个文件{extra}",
        "footer_extra": "，另有 {skipped} 个文件已省略",
    },
    "en": {
        "header": "# Directory Contents ({path})\n",
        "empty_dir": "(Directory is empty)",
        "empty_file": "(empty file)",
        "too_large": "({size} bytes, file too large, content omitted)",
        "read_fail": "(read failed: {err})",
        "omit_more": "\n... (more files omitted)",
        "footer": "\n---\nTotal {n} files{extra}",
        "footer_extra": ", and {skipped} more omitted",
    },
}


def _tpl(lang):
    return _DIR_DOC_TPL[lang] if lang in _DIR_DOC_TPL else _DIR_DOC_TPL["zh"]


def collect_dir_files(dir_path: str, lang: str = "zh", max_files: int = 50, max_file_size: int = 51200) -> str:
    tpl = _tpl(lang)
    lines = [tpl["header"].format(path=dir_path)]
    file_count = 0
    skipped = 0
    for root, _dirs, files in os.walk(dir_path):
        for fname in sorted(files):
            if file_count >= max_files:
                remaining = len(files) - files.index(fname) if fname in files else 0
                skipped += remaining
                lines.append(tpl["omit_more"])
                break
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, dir_path)
            try:
                size = os.path.getsize(fpath)
                if size == 0:
                    lines.append(f"\n## {rel} {tpl['empty_file']}")
                    file_count += 1
                    continue
                if size > max_file_size:
                    lines.append(f"\n## {rel} " + tpl["too_large"].format(size=size))
                    file_count += 1
                    continue
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                lines.append(f"\n## {rel} ({size} bytes)" if lang == "en" else f"\n## {rel} ({size} 字节)")
                lines.append(content)
                file_count += 1
            except Exception as e:
                lines.append(f"\n## {rel} " + tpl["read_fail"].format(err=e))
                file_count += 1
        if file_count >= max_files:
            break
    if file_count == 0:
        lines.append(tpl["empty_dir"])
    else:
        extra = tpl["footer_extra"].format(skipped=skipped) if skipped else ""
        lines.append(tpl["footer"].format(n=file_count, extra=extra))
    return "\n".join(lines)


_PROMPT_TPL = {
    "zh": {
        "opening": "你是一位专业的 AI 助手。请根据以下需求完成任务，并在回复中使用指定的标记标签包裹所有内容。\n",
        "req_header": "\n## 用户需求\n\n",
        "note_header": "\n## 注意事项\n\n",
        "notes": (
            "- 请阅读随本提示词一起提供的独立文档（目录文件内容和回复格式规则），并严格遵守其中的标记格式要求\n"
            "- 如果用户没有提供目录文件文档，则根据用户需求自由发挥\n"
            "- 回复中除标记内容外，请简要说明你的操作理由\n"
        ),
    },
    "en": {
        "opening": "You are a professional AI assistant. Please complete the following requirement and wrap all content with the specified marker tags in your reply.\n",
        "req_header": "\n## User Requirement\n\n",
        "note_header": "\n## Notes\n\n",
        "notes": (
            "- Read the standalone documents provided with this prompt (directory file contents and reply format rules), and strictly follow the marker format requirements in them\n"
            "- If the user did not provide the directory file document, act freely based on the requirement\n"
            "- In addition to the marker content, briefly explain your reasoning in the reply\n"
        ),
    },
}


class PromptGenerator:
    def generate(self, requirement: str, lang: str = "zh") -> str:
        tpl = _PROMPT_TPL[lang] if lang in _PROMPT_TPL else _PROMPT_TPL["zh"]
        return (
            tpl["opening"]
            + tpl["req_header"]
            + requirement + "\n"
            + tpl["note_header"]
            + tpl["notes"]
        )


_RULE_DOC_ZH = """AI 回复格式规则说明
========================

当 AI 助手需要执行文件操作、网页访问或输出结构化数据时，必须使用以下 7 种标记标签格式。

标记格式说明
------------

1. 创建文件
   [CREATE: 文件路径]
   文件内容
   [/CREATE]
   说明：创建新文件，路径可以是相对路径或绝对路径，内容为完整文件内容。

2. 编辑文件
   [EDIT: 文件路径]
   完整的新文件内容
   [/EDIT]
   说明：修改现有文件，内容为全量替换，即整个文件的新版本。

3. 删除文件
   [DELETE: 文件路径]
   说明：删除指定路径的文件，单独一行标记。

4. 获取网页
   [URL: URL地址]
   说明：访问指定 URL 获取网页内容，单独一行标记，URL 必须以 http:// 或 https:// 开头。

5. 下载文件
   [DOWNLOAD: URL地址]
   保存路径
   [/DOWNLOAD]
   说明：下载指定 URL 的文件并保存到指定路径，URL 必须以 http:// 或 https:// 开头。

6. 保存代码
   [CODE: 文件名]
   代码内容
   [/CODE]
   说明：将代码片段保存到指定文件，文件名支持相对路径。

7. 结构化数据
   [DATA: 数据类型]
   数据内容
   [/DATA]
   说明：输出 JSON 或 CSV 格式的结构化数据，数据类型标注为 "JSON" 或 "CSV"。

重要注意事项
------------
- 文件路径可以是相对路径或绝对路径
- URL 必须以 http:// 或 https:// 开头
- DATA 标记内的内容必须是合法的 JSON 或 CSV 格式
- 每个标记块必须独立使用，不要混合嵌套
- 不需要的操作类型不要使用对应标记
- 标记内的内容会被程序解析执行，请确保格式正确

完整示例
--------
以下示例展示了如何在一次回复中同时使用多种标记：

[CREATE: config/settings.json]
{"debug": true, "version": "1.0.0"}
[/CREATE]

[EDIT: src/app.py]
def main():
    print("app started")

if __name__ == "__main__":
    main()
[/EDIT]

[DELETE: temp/old_data.txt]

[URL: https://api.example.com/latest]

[DOWNLOAD: https://example.com/assets/logo.png]
assets/logo.png
[/DOWNLOAD]

[CODE: utils/helper.py]
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))
[/CODE]

[DATA: JSON]
{"status": "success", "files_created": 1, "files_edited": 1, "files_deleted": 1}
[/DATA]

在上述示例中，AI 创建了配置文件、修改了应用代码、删除了临时文件、获取了 API 页面、下载了图片资源、保存了工具函数，并输出了执行状态的结构化数据。
"""

_RULE_DOC_EN = """AI Response Format Rules
========================

When the AI assistant needs to perform file operations, web access, or output structured data, it MUST use the following 7 marker tag formats.

Marker Format Description
-------------------------

1. Create File
   [CREATE: file path]
   file content
   [/CREATE]
   Note: create a new file. The path may be relative or absolute; the content is the full file content.

2. Edit File
   [EDIT: file path]
   complete new file content
   [/EDIT]
   Note: modify an existing file. The content is a full replacement, i.e. the new version of the entire file.

3. Delete File
   [DELETE: file path]
   Note: delete the file at the given path. A single-line marker.

4. Fetch Web Page
   [URL: URL]
   Note: visit the given URL to fetch the web page content. A single-line marker; the URL must start with http:// or https://.

5. Download File
   [DOWNLOAD: URL]
   save path
   [/DOWNLOAD]
   Note: download the file at the given URL and save it to the given path. The URL must start with http:// or https://.

6. Save Code
   [CODE: file name]
   code content
   [/CODE]
   Note: save a code snippet to the given file. The file name may use a relative path.

7. Structured Data
   [DATA: data type]
   data content
   [/DATA]
   Note: output structured data in JSON or CSV format. The data type must be labeled "JSON" or "CSV".

Important Notes
---------------
- File paths may be relative or absolute
- URLs must start with http:// or https://
- The content inside a DATA marker must be valid JSON or CSV
- Each marker block must be used independently; do not nest or mix them
- Do not use a marker for an operation type that is not needed
- The content inside markers will be parsed and executed; make sure the format is correct

Full Example
------------
The following example shows how to use multiple markers in a single reply:

[CREATE: config/settings.json]
{"debug": true, "version": "1.0.0"}
[/CREATE]

[EDIT: src/app.py]
def main():
    print("app started")

if __name__ == "__main__":
    main()
[/EDIT]

[DELETE: temp/old_data.txt]

[URL: https://api.example.com/latest]

[DOWNLOAD: https://example.com/assets/logo.png]
assets/logo.png
[/DOWNLOAD]

[CODE: utils/helper.py]
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))
[/CODE]

[DATA: JSON]
{"status": "success", "files_created": 1, "files_edited": 1, "files_deleted": 1}
[/DATA]

In the example above, the AI created a config file, edited application code, deleted a temporary file, fetched an API page, downloaded an image asset, saved a utility function, and output structured data about the execution status.
"""


class RuleDocGenerator:
    def generate(self, lang: str = "zh") -> str:
        return _RULE_DOC_EN if lang == "en" else _RULE_DOC_ZH
