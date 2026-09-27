import csv
import json
import os
import shutil
from dataclasses import dataclass, field

import requests


@dataclass
class ExecResult:
    instruction_type: str
    param: str
    success: bool
    message: str


class WorkflowExecutor:
    def execute(self, instructions, work_dir: str) -> list:
        results = []
        for inst in instructions:
            inst_type = inst.type
            param = inst.param
            content = inst.content
            try:
                result = self._execute_single(inst_type, param, content, work_dir)
            except Exception as e:
                result = ExecResult(inst_type, param, False, f"执行异常: {e}")
            results.append(result)
        return results

    def _execute_single(self, inst_type, param, content, work_dir):
        if inst_type == "CREATE":
            return self._do_create(param, content, work_dir)
        elif inst_type == "EDIT":
            return self._do_edit(param, content, work_dir)
        elif inst_type == "DELETE":
            return self._do_delete(param, work_dir)
        elif inst_type == "URL":
            return self._do_url(param, work_dir)
        elif inst_type == "DOWNLOAD":
            return self._do_download(param, content, work_dir)
        elif inst_type == "CODE":
            return self._do_code(param, content, work_dir)
        elif inst_type == "DATA":
            return self._do_data(param, content, work_dir)
        else:
            return ExecResult(inst_type, param, False, f"未知指令类型: {inst_type}")

    def _resolve_path(self, work_dir, target):
        target = (target or "").strip()
        if os.path.isabs(target):
            return target
        if not target:
            return work_dir
        return os.path.join(work_dir, target)

    def _check_path_safety(self, work_dir, resolved):
        real_work_dir = os.path.realpath(work_dir)
        real_resolved = os.path.realpath(resolved)
        if real_resolved.startswith(real_work_dir + os.sep) or real_resolved == real_work_dir:
            return ""
        return f" 警告: 路径超出工作目录范围 ({real_resolved})"

    def _backup(self, resolved):
        if os.path.exists(resolved):
            backup = resolved + ".bak"
            shutil.copy2(resolved, backup)
            return backup
        return None

    def _do_create(self, param, content, work_dir):
        resolved = self._resolve_path(work_dir, param)
        warning = self._check_path_safety(work_dir, resolved)
        parent = os.path.dirname(resolved)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        msg = f"已创建文件: {param}"
        if warning:
            msg += warning
        return ExecResult("CREATE", param, True, msg)

    def _do_edit(self, param, content, work_dir):
        resolved = self._resolve_path(work_dir, param)
        warning = self._check_path_safety(work_dir, resolved)
        if not os.path.exists(resolved):
            msg = f"文件不存在: {param}"
            if warning:
                msg += warning
            return ExecResult("EDIT", param, False, msg)
        backup = self._backup(resolved)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        msg = f"已编辑文件: {param}"
        if backup:
            msg += f"（已备份为 {os.path.basename(backup)}）"
        if warning:
            msg += warning
        return ExecResult("EDIT", param, True, msg)

    def _do_delete(self, param, work_dir):
        resolved = self._resolve_path(work_dir, param)
        warning = self._check_path_safety(work_dir, resolved)
        if not os.path.exists(resolved):
            msg = f"文件不存在: {param}"
            if warning:
                msg += warning
            return ExecResult("DELETE", param, False, msg)
        os.remove(resolved)
        msg = f"已删除文件: {param}"
        if warning:
            msg += warning
        return ExecResult("DELETE", param, True, msg)

    def _do_url(self, param, work_dir):
        try:
            resp = requests.get(param, timeout=30)
            if resp.status_code >= 400:
                return ExecResult("URL", param, False, f"请求失败, HTTP {resp.status_code}")
            return ExecResult("URL", param, True, f"请求成功, 状态码: {resp.status_code}")
        except Exception as e:
            return ExecResult("URL", param, False, f"请求失败: {e}")

    def _do_download(self, param, content, work_dir):
        save_path = (content or "").strip()
        if not save_path:
            return ExecResult("DOWNLOAD", param, False, "缺少保存路径")
        url = param
        if not (url.startswith("http://") or url.startswith("https://")):
            return ExecResult("DOWNLOAD", url, False, "URL 格式无效，必须以 http:// 或 https:// 开头")
        resolved = self._resolve_path(work_dir, save_path)
        warning = self._check_path_safety(work_dir, resolved)
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code >= 400:
                return ExecResult("DOWNLOAD", url, False, f"下载失败, HTTP {resp.status_code}")
            parent = os.path.dirname(resolved)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(resolved, "wb") as f:
                f.write(resp.content)
            msg = f"已下载并保存: {save_path} ({len(resp.content)} 字节)"
            if warning:
                msg += warning
            return ExecResult("DOWNLOAD", url, True, msg)
        except Exception as e:
            msg = f"下载失败: {e}"
            if warning:
                msg += warning
            return ExecResult("DOWNLOAD", url, False, msg)

    def _do_code(self, param, content, work_dir):
        resolved = self._resolve_path(work_dir, param)
        warning = self._check_path_safety(work_dir, resolved)
        parent = os.path.dirname(resolved)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        msg = f"已保存代码: {param}"
        if warning:
            msg += warning
        return ExecResult("CODE", param, True, msg)

    def _do_data(self, param, content, work_dir):
        data_type = (param or "").strip()
        base_name = os.path.splitext(data_type)[0] or data_type
        if not base_name:
            base_name = "data"
        resolved = self._resolve_path(work_dir, base_name)

        is_json = False
        try:
            json.loads(content)
            is_json = True
        except (json.JSONDecodeError, ValueError):
            pass

        if is_json:
            filename = os.path.basename(resolved) + ".json"
        else:
            if not self._is_valid_csv(content):
                return ExecResult("DATA", param, False, "DATA 内容既不是有效的 JSON 也不是有效的 CSV")
            filename = os.path.basename(resolved) + ".csv"

        out_path = os.path.join(work_dir, filename)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        return ExecResult("DATA", param, True, f"已保存数据文件: {filename}")

    @staticmethod
    def _is_valid_csv(content: str) -> bool:
        stripped = (content or "").strip()
        if not stripped:
            return False
        try:
            reader = csv.reader(stripped.splitlines())
            for row in reader:
                if not row:
                    continue
        except csv.Error:
            return False
        return True
