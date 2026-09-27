import json
import re
from dataclasses import dataclass, field


@dataclass
class Instruction:
    type: str
    param: str
    content: str
    line: int


@dataclass
class ParseError:
    line: int
    message: str


@dataclass
class ParseResult:
    instructions: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.errors) == 0 and len(self.instructions) > 0


_PAIR_MARKERS = ("CREATE", "EDIT", "DOWNLOAD", "CODE", "DATA")
_PAIR_OPEN = {
    t: re.compile(r"^\[" + t + r":\s*(.*?)\s*\]$") for t in _PAIR_MARKERS
}
_PAIR_OPEN_FALLBACK = {
    t: re.compile(r"^\[" + t + r":\s*(.*)$") for t in _PAIR_MARKERS
}
_CLOSE = {
    t: "[/" + t + "]" for t in _PAIR_MARKERS
}
_SINGLE_DELETE = re.compile(r"^\[DELETE:\s*(.*?)\s*\]$")
_SINGLE_DELETE_FALLBACK = re.compile(r"^\[DELETE:\s*(.*)$")
_SINGLE_URL = re.compile(r"^\[URL:\s*(.*?)\s*\]$")
_SINGLE_URL_FALLBACK = re.compile(r"^\[URL:\s*(.*)$")


def _valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


class AIParser:
    def parse(self, text: str) -> ParseResult:
        lines = text.splitlines()
        instructions = []
        errors = []

        i = 0
        while i < len(lines):
            stripped = lines[i].strip()

            if stripped.startswith("[URL:"):
                i = self._parse_url(stripped, i, instructions, errors)
                continue

            if stripped.startswith("[DELETE:"):
                i = self._parse_delete(stripped, i, instructions, errors)
                continue

            if stripped.startswith("["):
                i = self._parse_pair(stripped, i, lines, instructions, errors)
                continue

            i += 1

        if not instructions and not errors:
            errors.append(ParseError(1, "未找到任何指令标记"))

        return ParseResult(instructions, errors)

    def _parse_url(self, line, i, instructions, errors):
        m = _SINGLE_URL.match(line)
        if m:
            param = m.group(1).strip()
            self._check_url(param, i, instructions, errors)
            return i + 1
        fb = _SINGLE_URL_FALLBACK.match(line)
        if fb:
            param = fb.group(1).strip()
            if param.endswith("]"):
                param = param[:-1].strip()
                self._check_url(param, i, instructions, errors)
            else:
                errors.append(ParseError(i + 1, "URL 标记格式不完整，缺少关闭括号 ]"))
        return i + 1

    def _check_url(self, param, i, instructions, errors):
        if not param:
            errors.append(ParseError(i + 1, "URL 地址不能为空"))
        elif not _valid_url(param):
            errors.append(ParseError(i + 1, "URL 必须以 http:// 或 https:// 开头"))
        else:
            instructions.append(Instruction("URL", param, "", i + 1))

    def _parse_delete(self, line, i, instructions, errors):
        m = _SINGLE_DELETE.match(line)
        if m:
            param = m.group(1).strip()
            if not param:
                errors.append(ParseError(i + 1, "DELETE 路径不能为空"))
            else:
                instructions.append(Instruction("DELETE", param, "", i + 1))
            return i + 1
        fb = _SINGLE_DELETE_FALLBACK.match(line)
        if fb:
            param = fb.group(1).strip()
            if param.endswith("]"):
                param = param[:-1].strip()
            if not param:
                errors.append(ParseError(i + 1, "DELETE 路径不能为空"))
            else:
                instructions.append(Instruction("DELETE", param, "", i + 1))
        return i + 1

    def _parse_pair(self, line, i, lines, instructions, errors):
        for marker in _PAIR_MARKERS:
            m = _PAIR_OPEN[marker].match(line)
            if m:
                param = m.group(1).strip()
                start_line = i + 1
                if not param:
                    errors.append(ParseError(start_line, f"[{marker}] 的参数不能为空"))
                    return self._skip_to_close(marker, i, lines)
                j = i + 1
                closed = False
                content_lines = []
                while j < len(lines):
                    if lines[j].strip() == _CLOSE[marker]:
                        closed = True
                        j += 1
                        break
                    content_lines.append(lines[j])
                    j += 1
                if not closed:
                    errors.append(ParseError(start_line, f"[{marker}] 缺少关闭标记 {_CLOSE[marker]}"))
                else:
                    content = "\n".join(content_lines)
                    self._finish_pair(marker, param, content, start_line, instructions, errors)
                return j
            fb = _PAIR_OPEN_FALLBACK[marker].match(line)
            if fb:
                errors.append(ParseError(i + 1, f"[{marker}: 标记格式不完整，缺少关闭括号 ]"))
                return i + 1
        return i + 1

    def _skip_to_close(self, marker, i, lines):
        j = i + 1
        while j < len(lines):
            if lines[j].strip() == _CLOSE[marker]:
                return j + 1
            j += 1
        return j

    def _finish_pair(self, marker, param, content, start_line, instructions, errors):
        if marker == "DOWNLOAD":
            url = param
            save_path = ""
            if content.strip():
                save_path = content.strip().splitlines()[0].strip()
            if not _valid_url(url):
                errors.append(ParseError(start_line, "DOWNLOAD URL 必须以 http:// 或 https:// 开头"))
            else:
                instructions.append(Instruction("DOWNLOAD", url, save_path, start_line))
        elif marker == "DATA":
            if not self._is_valid_data(content):
                errors.append(ParseError(start_line, "DATA 内容必须是有效的 JSON 或 CSV"))
            else:
                instructions.append(Instruction("DATA", param, content, start_line))
        else:
            instructions.append(Instruction(marker, param, content, start_line))

    @staticmethod
    def _is_valid_data(content: str) -> bool:
        stripped = content.strip()
        if not stripped:
            return False
        try:
            json.loads(stripped)
            return True
        except (json.JSONDecodeError, ValueError):
            pass
        non_empty = [l for l in stripped.splitlines() if l.strip()]
        return len(non_empty) >= 1
