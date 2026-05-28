"""浏览器数据清理 - Chrome / Edge / Firefox"""
import os
import shutil
import sqlite3
from utils.scanner import check_path_exists, get_dir_size, format_size


class BrowserCleaner:
    DISPLAY_NAME = "浏览器数据"

    def __init__(self):
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")

        self.targets = {
            "Chrome": {
                "历史记录": os.path.join(local, r"Google\Chrome\User Data\Default\History"),
                "Cookie": os.path.join(local, r"Google\Chrome\User Data\Default\Cookies"),
                "缓存": os.path.join(local, r"Google\Chrome\User Data\Default\Cache"),
                "自动填充": os.path.join(local, r"Google\Chrome\User Data\Default\Web Data"),
                "保存的密码": os.path.join(local, r"Google\Chrome\User Data\Default\Login Data"),
                "书签": os.path.join(local, r"Google\Chrome\User Data\Default\Bookmarks"),
                "会话": os.path.join(local, r"Google\Chrome\User Data\Default\Sessions"),
            },
            "Edge": {
                "历史记录": os.path.join(local, r"Microsoft\Edge\User Data\Default\History"),
                "Cookie": os.path.join(local, r"Microsoft\Edge\User Data\Default\Cookies"),
                "缓存": os.path.join(local, r"Microsoft\Edge\User Data\Default\Cache"),
                "自动填充": os.path.join(local, r"Microsoft\Edge\User Data\Default\Web Data"),
                "保存的密码": os.path.join(local, r"Microsoft\Edge\User Data\Default\Login Data"),
                "书签": os.path.join(local, r"Microsoft\Edge\User Data\Default\Bookmarks"),
            },
            "Firefox": {
                "配置目录": os.path.join(roaming, r"Mozilla\Firefox\Profiles"),
            },
        }

    def scan(self) -> list:
        """扫描浏览器数据，返回 [(描述, 路径, 大小字符串, 存在)] 列表"""
        results = []
        for browser, items in self.targets.items():
            for name, path in items.items():
                exists = check_path_exists(path)
                if exists:
                    if os.path.isdir(path):
                        size = format_size(get_dir_size(path))
                    else:
                        size = format_size(os.path.getsize(path))
                else:
                    size = "0 B"
                results.append((f"{browser} - {name}", path, size, exists))
        return results

    def clean(self, paths: list, logger) -> int:
        """清理指定路径列表，返回成功清理数量"""
        cleaned = 0
        for path in paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    logger.success(f"已删除目录: {path}")
                elif os.path.isfile(path):
                    os.remove(path)
                    logger.success(f"已删除文件: {path}")
                cleaned += 1
            except PermissionError:
                logger.error(f"权限不足，无法删除: {path}（请先关闭浏览器）")
            except Exception as e:
                logger.error(f"删除失败 {path}: {e}")
        return cleaned
