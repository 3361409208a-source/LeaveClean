"""个人文件清理 - 桌面/下载/文档/图片/视频/回收站/临时文件"""
import os
import shutil
import ctypes
import subprocess
from utils.scanner import check_path_exists, get_dir_size_fast, format_size, scan_directory


class FileCleaner:
    DISPLAY_NAME = "个人文件"

    def __init__(self):
        home = os.path.expanduser("~")
        self.dirs = {
            "桌面": os.path.join(home, "Desktop"),
            "下载": os.path.join(home, "Downloads"),
            "文档": os.path.join(home, "Documents"),
            "图片": os.path.join(home, "Pictures"),
            "视频": os.path.join(home, "Videos"),
            "音乐": os.path.join(home, "Music"),
        }
        self.temp_dir = os.environ.get("TEMP", os.path.join(home, "AppData", "Local", "Temp"))
        self.recent_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Recent")

    def scan(self) -> list:
        results = []
        # 用户目录
        for name, path in self.dirs.items():
            if check_path_exists(path):
                size = format_size(get_dir_size_fast(path))
                items = scan_directory(path)
                results.append((f"{name} ({len(items)}项)", path, size, True))
            else:
                results.append((name, path, "0 B", False))

        # 临时文件
        if check_path_exists(self.temp_dir):
            size = format_size(get_dir_size_fast(self.temp_dir))
            results.append(("临时文件 (%TEMP%)", self.temp_dir, size, True))

        # 最近文件记录
        if check_path_exists(self.recent_dir):
            size = format_size(get_dir_size_fast(self.recent_dir))
            results.append(("最近文件记录", self.recent_dir, size, True))

        # 回收站
        results.append(("回收站", "$RECYCLE", "需扫描", True))

        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for path in paths:
            try:
                if path == "$RECYCLE":
                    self._empty_recycle_bin(logger)
                    cleaned += 1
                elif path == self.temp_dir:
                    self._clean_temp(logger)
                    cleaned += 1
                elif path == self.recent_dir:
                    self._clean_recent(logger)
                    cleaned += 1
                elif os.path.isdir(path):
                    # 清理目录内容，但保留目录本身
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                        except (PermissionError, OSError):
                            pass
                    logger.success(f"已清理目录内容: {path}")
                    cleaned += 1
            except Exception as e:
                logger.error(f"清理失败 {path}: {e}")
        return cleaned

    def _empty_recycle_bin(self, logger):
        """清空回收站"""
        try:
            # SHEmptyRecycleBin flags: SHERB_NOCONFIRMATION=1 | SHERB_NOPROGRESSUI=2 | SHERB_NOSOUND=4
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
            logger.success("已清空回收站")
        except Exception as e:
            logger.error(f"清空回收站失败: {e}")

    def _clean_temp(self, logger):
        """清理临时文件"""
        count = 0
        for item in os.listdir(self.temp_dir):
            item_path = os.path.join(self.temp_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    count += 1
            except (PermissionError, OSError):
                pass
        logger.success(f"已清理 {count} 个临时文件/目录")

    def _clean_recent(self, logger):
        """清理最近文件记录"""
        count = 0
        for item in os.listdir(self.recent_dir):
            item_path = os.path.join(self.recent_dir, item)
            try:
                os.remove(item_path)
                count += 1
            except (PermissionError, OSError):
                pass
        logger.success(f"已清理 {count} 条最近文件记录")
