"""聊天/通讯/会议软件数据清理 — 同一软件合并展示"""
import os
import shutil
from utils.scanner import check_path_exists, get_dir_size_fast, format_size, count_files_fast


class ChatCleaner:
    DISPLAY_NAME = "聊天与通讯"

    def __init__(self):
        home = os.path.expanduser("~")
        docs = os.path.join(home, "Documents")
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")

        # 每个 app 一个列表, 所有路径集中在一起
        # 格式: (路径, 描述, 类型标签)
        # 类型: 图片/视频/文件/语音/缓存/聊天记录/配置/账号

        self.apps = {}

        # ===== 微信 (所有版本合并) =====
        wechat_paths = []
        # 新版
        wechat_root = os.path.join(docs, "xwechat_files")
        for acc_dir in self._find_subdirs(wechat_root, prefix="wxid_"):
            wechat_paths += [
                (os.path.join(acc_dir, "msg", "attach"), "聊天图片/表情", "图片"),
                (os.path.join(acc_dir, "msg", "video"), "聊天视频", "视频"),
                (os.path.join(acc_dir, "msg", "file"), "聊天文件/文档", "文件"),
                (os.path.join(acc_dir, "msg", "migrate"), "迁移数据", "文件"),
                (os.path.join(acc_dir, "resource"), "头像/资源图", "图片"),
                (os.path.join(acc_dir, "cache"), "缓存(按月)", "缓存"),
                (os.path.join(acc_dir, "temp", "ImageTemp"), "临时图片", "图片"),
                (os.path.join(acc_dir, "temp", "head_image"), "头像缓存", "图片"),
                (os.path.join(acc_dir, "temp", "InputTemp"), "输入临时文件", "缓存"),
                (os.path.join(acc_dir, "temp", "RWTemp"), "读写临时", "缓存"),
                (os.path.join(acc_dir, "db_storage"), "聊天数据库", "聊天记录"),
                (os.path.join(acc_dir, "config"), "账号配置", "配置"),
                (os.path.join(acc_dir, "business"), "小程序/公众号", "缓存"),
            ]
        wechat_paths.append((os.path.join(wechat_root, "Backup"), "聊天备份", "文件"))
        wechat_paths.append((os.path.join(wechat_root, "all_users"), "全局用户数据", "配置"))
        # 经典版
        wechat_classic = os.path.join(docs, "WeChat Files")
        for acc_dir in self._find_subdirs(wechat_classic, prefix="wxid_"):
            wechat_paths += [
                (os.path.join(acc_dir, "FileStorage", "Image"), "经典版-图片", "图片"),
                (os.path.join(acc_dir, "FileStorage", "Video"), "经典版-视频", "视频"),
                (os.path.join(acc_dir, "FileStorage", "File"), "经典版-文件", "文件"),
                (os.path.join(acc_dir, "FileStorage", "Voice"), "经典版-语音", "语音"),
                (os.path.join(acc_dir, "FileStorage", "Cache"), "经典版-缓存", "缓存"),
                (os.path.join(acc_dir, "FileStorage", "Fav"), "经典版-收藏", "文件"),
                (os.path.join(acc_dir, "Msg"), "经典版-聊天数据库", "聊天记录"),
            ]
        if not self._find_subdirs(wechat_classic, prefix="wxid_") and check_path_exists(wechat_classic):
            wechat_paths.append((wechat_classic, "经典版数据目录", "聊天记录"))
        # 微信其他
        wechat_paths += [
            (os.path.join(roaming, "Tencent", "WeChat"), "应用缓存", "缓存"),
            (os.path.join(roaming, "WXDrive"), "微信云盘同步", "文件"),
            (os.path.join(local, "微信开发者工具"), "开发者工具数据", "缓存"),
        ]
        self.apps["微信"] = wechat_paths

        # ===== QQ (所有版本合并) =====
        qq_paths = []
        qq_root = os.path.join(docs, "Tencent Files")
        for acc_dir in self._find_subdirs(qq_root, digits_only=True):
            qq_paths += [
                (os.path.join(acc_dir, "Image"), "聊天图片", "图片"),
                (os.path.join(acc_dir, "Video"), "聊天视频", "视频"),
                (os.path.join(acc_dir, "FileRecv"), "接收文件", "文件"),
                (os.path.join(acc_dir, "Audio"), "语音消息", "语音"),
                (os.path.join(acc_dir, "Msg2.0.db"), "聊天数据库", "聊天记录"),
            ]
        qq_nt = os.path.join(qq_root, "nt_qq")
        qq_paths += [
            (os.path.join(qq_nt, "global", "nt_data"), "NT版聊天数据", "聊天记录"),
            (os.path.join(qq_nt, "global", "nt_db"), "NT版数据库", "聊天记录"),
            (os.path.join(qq_nt, "global", "nt_temp"), "NT版临时文件", "缓存"),
            (os.path.join(roaming, "QQ", "Cache"), "浏览器缓存", "缓存"),
            (os.path.join(roaming, "QQ", "IndexedDB"), "IndexedDB", "缓存"),
            (os.path.join(roaming, "QQ", "blob_storage"), "Blob存储", "缓存"),
            (os.path.join(roaming, "QQ", "Local Storage"), "本地存储", "缓存"),
            (os.path.join(roaming, "QQ", "miniapp"), "QQ小程序", "缓存"),
            (os.path.join(roaming, "QQ", "log"), "运行日志", "缓存"),
            (os.path.join(roaming, "QQ", "auth"), "登录凭据", "账号"),
            (os.path.join(roaming, "QQEX"), "QQEX/TIM数据", "缓存"),
        ]
        self.apps["QQ"] = qq_paths

        # ===== 企业微信 (合并所有账号) =====
        wxwork_paths = []
        wxwork_root = os.path.join(docs, "WXWork")
        for acc_dir in self._find_subdirs(wxwork_root, digits_only=True):
            wxwork_paths += [
                (os.path.join(acc_dir, "Cache", "Image"), "聊天图片", "图片"),
                (os.path.join(acc_dir, "Cache", "Video"), "聊天视频", "视频"),
                (os.path.join(acc_dir, "Cache", "File"), "聊天文件", "文件"),
                (acc_dir, "账号数据", "聊天记录"),
            ]
        wxwork_paths += [
            (os.path.join(roaming, "Tencent", "WXWork"), "应用数据", "缓存"),
            (os.path.join(local, "Tencent", "WXWork"), "本地缓存", "缓存"),
            (os.path.join(roaming, "wxworkweb"), "Web版缓存", "缓存"),
        ]
        self.apps["企业微信"] = wxwork_paths

        # ===== 钉钉 =====
        self.apps["钉钉"] = [
            (os.path.join(local, "DingTalk"), "应用数据/聊天文件", "文件"),
            (os.path.join(local, "DingTalk_108"), "108版数据", "文件"),
            (os.path.join(roaming, "DingTalk"), "配置/缓存", "缓存"),
            (os.path.join(roaming, "dinglive"), "直播缓存", "视频"),
        ]

        # ===== 飞书 =====
        self.apps["飞书"] = [
            (os.path.join(local, "Feishu"), "应用数据/聊天文件", "文件"),
            (os.path.join(roaming, "LarkShell"), "Shell数据", "缓存"),
        ]

        # ===== 腾讯会议 =====
        self.apps["腾讯会议"] = [
            (os.path.join(roaming, "WeMeetApp"), "录制/应用数据", "视频"),
            (os.path.join(local, "Tencent", "Wemeet"), "本地缓存", "缓存"),
        ]

        # ===== Telegram =====
        self.apps["Telegram"] = [
            (os.path.join(roaming, "Telegram Desktop"), "聊天/图片/文件/缓存", "聊天记录"),
        ]

        # ===== Foxmail =====
        self.apps["Foxmail"] = [
            (os.path.join(roaming, "Foxmail7"), "邮件/附件/账号", "文件"),
        ]

    def scan(self) -> list:
        results = []
        for app_name, paths in self.apps.items():
            for path, detail, tag in paths:
                if not check_path_exists(path):
                    continue
                if os.path.isdir(path):
                    size = format_size(get_dir_size_fast(path))
                    fcount = count_files_fast(path)
                    desc = f"[{tag}] {detail} (~{fcount}文件)"
                else:
                    try:
                        size = format_size(os.path.getsize(path))
                    except OSError:
                        size = "未知"
                    desc = f"[{tag}] {detail}"

                if tag in ("账号", "聊天记录"):
                    desc = "⚠ " + desc

                # 前缀加 app 名，方便 GUI 分组
                results.append((f"{app_name} - {desc}", path, size, True))
        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for path in paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.success(f"已删除: {path}")
                    cleaned += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    logger.success(f"已删除: {path}")
                    cleaned += 1
            except PermissionError:
                logger.error(f"权限不足: {path}（请先退出该软件）")
            except Exception as e:
                logger.error(f"删除失败 {path}: {e}")
        return cleaned

    @staticmethod
    def _find_subdirs(parent, prefix=None, digits_only=False):
        results = []
        if not os.path.isdir(parent):
            return results
        try:
            for entry in os.scandir(parent):
                if not entry.is_dir():
                    continue
                if prefix and entry.name.startswith(prefix):
                    results.append(entry.path)
                elif digits_only and entry.name.isdigit():
                    results.append(entry.path)
        except (OSError, PermissionError):
            pass
        return results
