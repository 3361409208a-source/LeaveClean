"""凭据与隐私清理 - Windows凭据管理器/剪贴板/搜索历史"""
import os
import subprocess
import ctypes
from utils.scanner import check_path_exists


class CredentialCleaner:
    DISPLAY_NAME = "凭据与隐私"

    def __init__(self):
        self.items = {
            "Windows 保存的凭据": "credentials",
            "剪贴板内容": "clipboard",
            "Windows 搜索历史": "search_history",
            "运行对话框历史": "run_history",
            "资源管理器地址栏历史": "explorer_history",
        }

    def scan(self) -> list:
        results = []

        # Windows 凭据
        cred_count = self._count_credentials()
        results.append((
            f"Windows 保存的凭据 ({cred_count}条)",
            "credentials", f"{cred_count} 条记录",
            cred_count > 0
        ))

        # 剪贴板
        results.append(("剪贴板内容", "clipboard", "当前内容", True))

        # 搜索历史
        results.append(("Windows 搜索历史", "search_history", "注册表", True))

        # 运行对话框历史
        results.append(("运行对话框历史 (Win+R)", "run_history", "注册表", True))

        # 地址栏历史
        results.append(("资源管理器地址栏历史", "explorer_history", "注册表", True))

        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for item in paths:
            try:
                if item == "credentials":
                    cleaned += self._clean_credentials(logger)
                elif item == "clipboard":
                    self._clean_clipboard(logger)
                    cleaned += 1
                elif item == "search_history":
                    self._clean_search_history(logger)
                    cleaned += 1
                elif item == "run_history":
                    self._clean_run_history(logger)
                    cleaned += 1
                elif item == "explorer_history":
                    self._clean_explorer_history(logger)
                    cleaned += 1
            except Exception as e:
                logger.error(f"清理失败 {item}: {e}")
        return cleaned

    def _count_credentials(self) -> int:
        try:
            result = subprocess.run(
                ["cmdkey", "/list"], capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.stdout.count("目标:") + result.stdout.count("Target:")
        except Exception:
            return 0

    def _clean_credentials(self, logger) -> int:
        """删除所有保存的 Windows 凭据"""
        try:
            result = subprocess.run(
                ["cmdkey", "/list"], capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            count = 0
            for line in result.stdout.splitlines():
                line = line.strip()
                for prefix in ["目标:", "Target:"]:
                    if line.startswith(prefix):
                        target = line[len(prefix):].strip()
                        subprocess.run(
                            ["cmdkey", "/delete:" + target],
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        count += 1
            logger.success(f"已删除 {count} 条 Windows 凭据")
            return 1
        except Exception as e:
            logger.error(f"清理凭据失败: {e}")
            return 0

    def _clean_clipboard(self, logger):
        """清空剪贴板"""
        try:
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()
            logger.success("已清空剪贴板")
        except Exception as e:
            logger.error(f"清空剪贴板失败: {e}")

    def _clean_search_history(self, logger):
        """清理 Windows 搜索历史"""
        try:
            subprocess.run(
                ["reg", "delete",
                 r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery",
                 "/f"],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.success("已清理 Windows 搜索历史")
        except Exception as e:
            logger.error(f"清理搜索历史失败: {e}")

    def _clean_run_history(self, logger):
        """清理运行对话框历史"""
        try:
            subprocess.run(
                ["reg", "delete",
                 r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                 "/f"],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.success("已清理运行对话框历史")
        except Exception as e:
            logger.error(f"清理运行历史失败: {e}")

    def _clean_explorer_history(self, logger):
        """清理资源管理器地址栏历史"""
        try:
            subprocess.run(
                ["reg", "delete",
                 r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths",
                 "/f"],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.success("已清理资源管理器地址栏历史")
        except Exception as e:
            logger.error(f"清理地址栏历史失败: {e}")
