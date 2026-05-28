"""凭据与隐私清理 - 全面覆盖版"""
import os
import subprocess
import ctypes
from utils.scanner import check_path_exists, get_dir_size_fast, format_size


class CredentialCleaner:
    DISPLAY_NAME = "凭据与隐私"

    def __init__(self):
        roaming = os.environ.get("APPDATA", "")
        local = os.environ.get("LOCALAPPDATA", "")
        home = os.path.expanduser("~")

        # 需要扫描的隐私目录
        self.privacy_dirs = {
            "WiFi保存的密码": None,  # 通过 netsh 处理
            "Windows 凭据管理器": "credentials",
            "剪贴板内容": "clipboard",
            "Windows 搜索历史": "search_history",
            "运行对话框历史 (Win+R)": "run_history",
            "资源管理器地址栏历史": "explorer_history",
            "最近打开的文档": "recent_docs",
            "任务栏最近项目": "taskbar_recent",
            "缩略图缓存": os.path.join(local, "Microsoft", "Windows", "Explorer"),
            "Windows临时文件": os.environ.get("TEMP", ""),
            "Windows预取文件": r"C:\Windows\Prefetch",
            "DNS缓存": "dns_cache",
            "Git凭据": os.path.join(home, ".gitconfig"),
            "Git凭据存储": os.path.join(home, ".git-credentials"),
            "SSH密钥": os.path.join(home, ".ssh"),
            "npm配置": os.path.join(home, ".npmrc"),
            "pip配置": os.path.join(roaming, "pip"),
            "Docker凭据": os.path.join(home, ".docker"),
            "AWS凭据": os.path.join(home, ".aws"),
            "Azure凭据": os.path.join(home, ".azure"),
            "Kubernetes配置": os.path.join(home, ".kube"),
            "远程桌面连接记录": "rdp_history",
            "Windows事件日志(个人相关)": "event_log",
        }

    def scan(self) -> list:
        results = []

        # 1. Windows 凭据
        cred_count = self._count_credentials()
        results.append((
            f"Windows 凭据管理器 ({cred_count}条)",
            "credentials", f"{cred_count} 条",
            cred_count > 0))

        # 2. WiFi密码
        wifi_count = self._count_wifi()
        results.append((
            f"WiFi保存的密码 ({wifi_count}个)",
            "wifi_passwords", f"{wifi_count} 个",
            wifi_count > 0))

        # 3. 剪贴板
        results.append(("剪贴板内容", "clipboard", "当前内容", True))

        # 4. 注册表历史
        reg_items = [
            ("Windows 搜索历史", "search_history"),
            ("运行对话框历史 (Win+R)", "run_history"),
            ("资源管理器地址栏历史", "explorer_history"),
            ("最近打开的文档记录", "recent_docs"),
            ("任务栏跳转列表", "taskbar_recent"),
            ("远程桌面连接记录", "rdp_history"),
        ]
        for name, key in reg_items:
            results.append((name, key, "注册表", True))

        # 5. DNS缓存
        results.append(("DNS缓存", "dns_cache", "内存", True))

        # 6. 缩略图缓存
        thumb_path = os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Microsoft", "Windows", "Explorer")
        if check_path_exists(thumb_path):
            size = format_size(get_dir_size_fast(thumb_path))
            results.append((f"缩略图缓存 (thumbcache)", thumb_path, size, True))

        # 7. 开发者凭据文件
        home = os.path.expanduser("~")
        dev_files = {
            "Git全局配置": os.path.join(home, ".gitconfig"),
            "Git凭据存储": os.path.join(home, ".git-credentials"),
            "SSH密钥目录": os.path.join(home, ".ssh"),
            "npm配置 (.npmrc)": os.path.join(home, ".npmrc"),
            "pip配置": os.path.join(os.environ.get("APPDATA", ""), "pip"),
            "Docker配置": os.path.join(home, ".docker"),
            "AWS凭据": os.path.join(home, ".aws"),
            "Azure配置": os.path.join(home, ".azure"),
            "Kubernetes配置": os.path.join(home, ".kube"),
            "Conda配置": os.path.join(home, ".condarc"),
            "Python历史": os.path.join(home, ".python_history"),
            "Node REPL历史": os.path.join(home, ".node_repl_history"),
            "bash历史": os.path.join(home, ".bash_history"),
            "PowerShell历史": os.path.join(
                os.environ.get("APPDATA", ""),
                r"Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"),
        }
        for name, path in dev_files.items():
            if check_path_exists(path):
                if os.path.isdir(path):
                    size = format_size(get_dir_size_fast(path))
                else:
                    try:
                        size = format_size(os.path.getsize(path))
                    except OSError:
                        size = "未知"
                results.append((name, path, size, True))

        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for item in paths:
            try:
                if item == "credentials":
                    cleaned += self._clean_credentials(logger)
                elif item == "wifi_passwords":
                    cleaned += self._clean_wifi(logger)
                elif item == "clipboard":
                    self._clean_clipboard(logger)
                    cleaned += 1
                elif item == "search_history":
                    self._clean_reg(logger,
                        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery",
                        "Windows 搜索历史")
                    cleaned += 1
                elif item == "run_history":
                    self._clean_reg(logger,
                        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                        "运行对话框历史")
                    cleaned += 1
                elif item == "explorer_history":
                    self._clean_reg(logger,
                        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths",
                        "资源管理器地址栏历史")
                    cleaned += 1
                elif item == "recent_docs":
                    self._clean_recent_docs(logger)
                    cleaned += 1
                elif item == "taskbar_recent":
                    self._clean_taskbar_recent(logger)
                    cleaned += 1
                elif item == "rdp_history":
                    self._clean_reg(logger,
                        r"HKCU\Software\Microsoft\Terminal Server Client\Default",
                        "远程桌面连接记录")
                    cleaned += 1
                elif item == "dns_cache":
                    self._clean_dns(logger)
                    cleaned += 1
                elif os.path.exists(item):
                    # 文件或目录路径
                    self._clean_path(item, logger)
                    cleaned += 1
            except Exception as e:
                logger.error(f"清理失败 {item}: {e}")
        return cleaned

    # ==================== Windows 凭据 ====================

    def _count_credentials(self) -> int:
        try:
            r = subprocess.run(["cmdkey", "/list"], capture_output=True, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            return r.stdout.count("目标:") + r.stdout.count("Target:")
        except Exception:
            return 0

    def _clean_credentials(self, logger) -> int:
        try:
            r = subprocess.run(["cmdkey", "/list"], capture_output=True, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            count = 0
            for line in r.stdout.splitlines():
                line = line.strip()
                for prefix in ["目标:", "Target:"]:
                    if line.startswith(prefix):
                        target = line[len(prefix):].strip()
                        subprocess.run(["cmdkey", "/delete:" + target],
                                       capture_output=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                        count += 1
            logger.success(f"已删除 {count} 条 Windows 凭据")
            return 1
        except Exception as e:
            logger.error(f"清理凭据失败: {e}")
            return 0

    # ==================== WiFi ====================

    def _count_wifi(self) -> int:
        try:
            r = subprocess.run(["netsh", "wlan", "show", "profiles"],
                               capture_output=True, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            count = 0
            for line in r.stdout.splitlines():
                if "所有用户配置文件" in line or "All User Profile" in line:
                    count += 1
            return count
        except Exception:
            return 0

    def _clean_wifi(self, logger) -> int:
        try:
            r = subprocess.run(["netsh", "wlan", "show", "profiles"],
                               capture_output=True, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            count = 0
            for line in r.stdout.splitlines():
                for prefix in ["所有用户配置文件 : ", "All User Profile     : "]:
                    if prefix in line:
                        name = line.split(prefix)[-1].strip()
                        subprocess.run(
                            ["netsh", "wlan", "delete", "profile", f"name={name}"],
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        count += 1
            logger.success(f"已删除 {count} 个 WiFi 配置")
            return 1
        except Exception as e:
            logger.error(f"清理WiFi密码失败: {e}")
            return 0

    # ==================== 剪贴板 ====================

    def _clean_clipboard(self, logger):
        try:
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()
            logger.success("已清空剪贴板")
        except Exception as e:
            logger.error(f"清空剪贴板失败: {e}")

    # ==================== 注册表通用清理 ====================

    def _clean_reg(self, logger, reg_path, name):
        try:
            subprocess.run(["reg", "delete", reg_path, "/f"],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logger.success(f"已清理{name}")
        except Exception as e:
            logger.error(f"清理{name}失败: {e}")

    # ==================== 最近文档 ====================

    def _clean_recent_docs(self, logger):
        recent = os.path.join(os.environ.get("APPDATA", ""),
                              r"Microsoft\Windows\Recent")
        count = 0
        if os.path.isdir(recent):
            for f in os.listdir(recent):
                try:
                    fp = os.path.join(recent, f)
                    if os.path.isfile(fp):
                        os.remove(fp)
                        count += 1
                except (OSError, PermissionError):
                    pass
        logger.success(f"已清理 {count} 条最近文档记录")

    # ==================== 任务栏跳转列表 ====================

    def _clean_taskbar_recent(self, logger):
        paths = [
            os.path.join(os.environ.get("APPDATA", ""),
                         r"Microsoft\Windows\Recent\AutomaticDestinations"),
            os.path.join(os.environ.get("APPDATA", ""),
                         r"Microsoft\Windows\Recent\CustomDestinations"),
        ]
        count = 0
        for p in paths:
            if os.path.isdir(p):
                for f in os.listdir(p):
                    try:
                        os.remove(os.path.join(p, f))
                        count += 1
                    except (OSError, PermissionError):
                        pass
        logger.success(f"已清理 {count} 个任务栏跳转列表项")

    # ==================== DNS ====================

    def _clean_dns(self, logger):
        try:
            subprocess.run(["ipconfig", "/flushdns"],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logger.success("已清空 DNS 缓存")
        except Exception as e:
            logger.error(f"清空DNS缓存失败: {e}")

    # ==================== 文件/目录 ====================

    def _clean_path(self, path, logger):
        import shutil
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.success(f"已删除: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
                logger.success(f"已删除目录: {path}")
        except PermissionError:
            logger.error(f"权限不足: {path}")
        except Exception as e:
            logger.error(f"删除失败 {path}: {e}")
