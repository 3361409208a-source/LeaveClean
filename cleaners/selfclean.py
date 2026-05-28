"""本应用自身 — 卸载并删除所有关联数据"""

import os
import shutil
import subprocess
import sys
import tempfile
from utils.scanner import check_path_exists, get_dir_size_fast, format_size


class SelfCleaner:
    DISPLAY_NAME = "本应用自身"

    def __init__(self):
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.self_destruct_triggered = False

    def scan(self):
        results = []

        log_dir = os.path.join(self.app_dir, "logs")
        if check_path_exists(log_dir):
            size = format_size(get_dir_size_fast(log_dir))
            results.append(("[日志] 运行日志", f"data:{log_dir}", size, True))

        for root, dirs, _ in os.walk(self.app_dir):
            for d in dirs:
                if d == "__pycache__":
                    path = os.path.join(root, d)
                    size = format_size(get_dir_size_fast(path))
                    results.append(
                        (
                            f"[缓存] {os.path.relpath(path, self.app_dir)}",
                            f"data:{path}",
                            size,
                            True,
                        )
                    )

        total_size = format_size(get_dir_size_fast(self.app_dir))
        results.append(
            (
                "[本应用] LeaveClean 清理助手（自卸载）",
                f"selfdestruct:{self.app_dir}",
                total_size,
                True,
            )
        )

        return results

    def clean(self, paths, logger):
        cleaned = 0
        for action_key in paths:
            try:
                if action_key.startswith("selfdestruct:"):
                    self._prepare_self_destruct(logger)
                    cleaned += 1
                elif action_key.startswith("data:"):
                    cleaned += self._do_remove_data(action_key[5:], logger)
            except Exception as e:
                logger.error(f"操作失败 {action_key}: {e}")
        return cleaned

    def _do_remove_data(self, path, logger):
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.success(f"已删除文件: {path}")
                return 1
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
                logger.success(f"已删除目录: {path}")
                return 1
            else:
                logger.warning(f"路径不存在: {path}")
                return 0
        except Exception as e:
            logger.error(f"删除失败 {path}: {e}")
            return 0

    def _prepare_self_destruct(self, logger):
        batch_content = (
            f"@echo off\n"
            f"timeout /t 2 /nobreak >nul\n"
            f'rmdir /s /q "{self.app_dir}"\n'
            f'del "%~f0"\n'
        )
        batch_path = os.path.join(tempfile.gettempdir(), "leaveclean_selfdestruct.bat")
        with open(batch_path, "w", encoding="utf-8") as f:
            f.write(batch_content)

        logger.success("本应用即将卸载并删除所有数据，程序将自动关闭...")
        self.self_destruct_triggered = True
