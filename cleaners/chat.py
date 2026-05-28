"""聊天软件数据清理 - 微信/QQ/钉钉/飞书"""
import os
import shutil
from utils.scanner import check_path_exists, get_dir_size, format_size, count_files


class ChatCleaner:
    DISPLAY_NAME = "聊天软件"

    def __init__(self):
        docs = os.path.join(os.path.expanduser("~"), "Documents")
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")

        self.targets = {
            "微信": {
                "聊天记录与文件": os.path.join(docs, "WeChat Files"),
                "缓存数据": os.path.join(roaming, "Tencent", "WeChat"),
            },
            "QQ": {
                "聊天记录": os.path.join(docs, "Tencent Files"),
                "缓存数据": os.path.join(local, "Tencent", "QQ"),
            },
            "钉钉": {
                "应用数据": os.path.join(local, "DingTalk"),
                "缓存": os.path.join(roaming, "DingTalk"),
            },
            "飞书": {
                "应用数据": os.path.join(local, "Lark"),
                "缓存": os.path.join(roaming, "Lark"),
            },
            "企业微信": {
                "应用数据": os.path.join(roaming, "Tencent", "WXWork"),
                "缓存": os.path.join(local, "Tencent", "WXWork"),
            },
            "Telegram": {
                "应用数据": os.path.join(roaming, "Telegram Desktop"),
            },
        }

    def scan(self) -> list:
        results = []
        for app, items in self.targets.items():
            for name, path in items.items():
                exists = check_path_exists(path)
                if exists:
                    size = format_size(get_dir_size(path))
                    files = count_files(path)
                    desc = f"{app} - {name} ({files}个文件)"
                else:
                    size = "0 B"
                    desc = f"{app} - {name}"
                results.append((desc, path, size, exists))
        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for path in paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    logger.success(f"已删除: {path}")
                    cleaned += 1
            except PermissionError:
                logger.error(f"权限不足: {path}（请先退出该软件）")
            except Exception as e:
                logger.error(f"删除失败 {path}: {e}")
        return cleaned
