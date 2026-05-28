"""浏览器数据清理 - 账号/同步/隐私/缓存全覆盖"""
import os
import shutil
import json
from utils.scanner import check_path_exists, get_dir_size_fast, format_size


class BrowserCleaner:
    DISPLAY_NAME = "浏览器数据"

    def __init__(self):
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")

        # ===== Chromium 子路径分组 =====

        # 账号与同步数据（核心隐私）
        account_items = [
            ("登录的Google/MS账号", r"Default\Preferences"),
            ("账号同步数据", r"Default\Sync Data"),
            ("账号同步数据(LevelDB)", r"Default\Sync Data LevelDB"),
            ("账号令牌", r"Default\Web Data"),
            ("Google服务令牌", r"Default\AccountData"),
            ("已登录网站状态", r"Default\Login Data"),
            ("已登录网站(Journal)", r"Default\Login Data-journal"),
            ("OAuth令牌", r"Default\Token Service"),
            ("已保存的密码", r"Default\Login Data"),
            ("支付信息/银行卡", r"Default\Web Data"),
            ("地址自动填充", r"Default\Web Data"),
        ]

        # 浏览隐私
        privacy_items = [
            ("历史记录", r"Default\History"),
            ("历史记录(Journal)", r"Default\History-journal"),
            ("Cookie", r"Default\Cookies"),
            ("Cookie(新版)", r"Default\Network\Cookies"),
            ("书签", r"Default\Bookmarks"),
            ("书签备份", r"Default\Bookmarks.bak"),
            ("访问最多的网站", r"Default\Top Sites"),
            ("搜索关键词", r"Default\Shortcuts"),
            ("下载记录", r"Default\DownloadMetadata"),
            ("表单自动填充", r"Default\Web Data"),
            ("网站权限设置", r"Default\Preferences"),
            ("媒体播放记录", r"Default\Media History"),
            ("阅读列表", r"Default\Reading List"),
        ]

        # 扩展与应用
        extension_items = [
            ("已安装的扩展", r"Default\Extensions"),
            ("扩展数据", r"Default\Extension State"),
            ("扩展规则", r"Default\Extension Rules"),
            ("Web应用数据", r"Default\Web Applications"),
            ("PWA应用", r"Default\Web Apps"),
        ]

        # 缓存（占空间最大）
        cache_items = [
            ("浏览器缓存", r"Default\Cache"),
            ("Code Cache", r"Default\Code Cache"),
            ("GPU缓存", r"GPUCache"),
            ("ShaderCache", r"ShaderCache"),
            ("媒体缓存", r"Default\Media Cache"),
            ("Service Worker", r"Default\Service Worker"),
            ("Service Worker缓存", r"Service Worker\CacheStorage"),
            ("IndexedDB", r"Default\IndexedDB"),
            ("Local Storage", r"Default\Local Storage"),
            ("Session Storage", r"Default\Session Storage"),
            ("File System", r"Default\File System"),
            ("Blob存储", r"Default\blob_storage"),
            ("网络日志", r"Default\Network Action Predictor"),
        ]

        # 会话与状态
        session_items = [
            ("当前会话/标签页", r"Default\Sessions"),
            ("崩溃恢复数据", r"Default\Sessions\Session_*"),
            ("当前标签组", r"Default\Sessions\Tabs_*"),
            ("最近关闭的标签", r"Default\Current Tabs"),
            ("最近关闭的会话", r"Default\Current Session"),
            ("Last Session", r"Default\Last Session"),
            ("Last Tabs", r"Default\Last Tabs"),
        ]

        # 整个用户配置（核弹级清理）
        profile_items = [
            ("整个用户配置(Default)", r"Default"),
        ]

        # 全部合并
        all_items = (
            [("★ " + n, p) for n, p in account_items] +
            privacy_items + extension_items +
            cache_items + session_items + profile_items
        )

        # Chromium 浏览器根路径
        chromium_roots = {
            "Chrome": os.path.join(local, r"Google\Chrome\User Data"),
            "Edge": os.path.join(local, r"Microsoft\Edge\User Data"),
            "QQ浏览器": os.path.join(local, r"Tencent\QQBrowser\User Data"),
            "搜狗浏览器": os.path.join(roaming, r"SogouExplorer"),
            "360安全浏览器": os.path.join(roaming, r"360se6"),
        }

        self.targets = {}
        self.account_paths = {}  # 记录哪些是账号相关路径

        for browser, root in chromium_roots.items():
            items = {}
            for name, sub in all_items:
                full = os.path.join(root, sub)
                items[name] = full
                if name.startswith("★"):
                    if browser not in self.account_paths:
                        self.account_paths[browser] = []
                    self.account_paths[browser].append((name, full))
            self.targets[browser] = items

        # Firefox
        self.targets["Firefox"] = {
            "★ Firefox配置目录(含账号)": os.path.join(roaming, r"Mozilla\Firefox\Profiles"),
            "Firefox缓存": os.path.join(local, r"Mozilla\Firefox\Profiles"),
            "Firefox崩溃报告": os.path.join(roaming, r"Mozilla\Firefox\Crash Reports"),
            "Firefox更新数据": os.path.join(local, r"Mozilla\Updates"),
        }

        # 浏览器扩展缓存(独立目录)
        self.extra_paths = {
            "Chrome扩展缓存": os.path.join(local, r"Google\Chrome\User Data\Default\Extension State"),
            "Chrome崩溃报告": os.path.join(local, r"Google\Chrome\User Data\Crashpad"),
            "Chrome更新缓存": os.path.join(local, r"Google\Update"),
            "Edge更新缓存": os.path.join(local, r"Microsoft\EdgeUpdate"),
            "Chrome远程桌面": os.path.join(local, r"Google\Chrome Remote Desktop"),
        }

    def scan(self) -> list:
        results = []

        for browser, items in self.targets.items():
            browser_exists = False
            browser_items = []

            for name, path in items.items():
                exists = check_path_exists(path)
                if exists:
                    browser_exists = True
                    if os.path.isdir(path):
                        size = format_size(get_dir_size_fast(path))
                    else:
                        try:
                            size = format_size(os.path.getsize(path))
                        except OSError:
                            size = "0 B"
                    browser_items.append((f"{browser} - {name}", path, size, True))

            if browser_exists:
                # 尝试读取已登录的账号信息
                account_info = self._detect_account(browser)
                if account_info:
                    browser_items.insert(0, (
                        f"{browser} - 已登录账号: {account_info}",
                        list(items.values())[0],  # 指向 Preferences
                        "账号数据",
                        True
                    ))
                results.extend(browser_items)

        # 额外独立路径
        for name, path in self.extra_paths.items():
            if check_path_exists(path):
                size = format_size(get_dir_size_fast(path))
                results.append((name, path, size, True))

        return results

    def _detect_account(self, browser: str) -> str:
        """尝试从 Preferences 中读取已登录的 Google/MS 账号"""
        items = self.targets.get(browser, {})
        pref_path = None
        for name, path in items.items():
            if "Preferences" in name:
                pref_path = path
                break
        if not pref_path or not os.path.isfile(pref_path):
            return ""
        try:
            with open(pref_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            # Chrome: account_info -> [{"email": "..."}]
            accounts = data.get("account_info", [])
            if accounts:
                emails = [a.get("email", "") for a in accounts if a.get("email")]
                if emails:
                    return ", ".join(emails)
            # Edge: profile.name / signin
            signin = data.get("signin", {})
            if signin.get("allowed"):
                gaia = data.get("account_info", [])
                if gaia:
                    return gaia[0].get("email", "")
            # 尝试 profile.name
            profile = data.get("profile", {})
            name = profile.get("name", "")
            gaia_name = profile.get("gaia_info_picture_url", "")
            if name and name != "Person 1":
                return name
        except Exception:
            pass
        return ""

    def clean(self, paths: list, logger) -> int:
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
                logger.error(f"权限不足: {path}（请先关闭浏览器）")
            except Exception as e:
                logger.error(f"删除失败 {path}: {e}")
        return cleaned
