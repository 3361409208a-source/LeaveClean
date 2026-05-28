"""个人软件卸载与数据清理"""
import os
import shutil
import subprocess
import winreg
from utils.scanner import check_path_exists, get_dir_size, format_size


class SoftwareCleaner:
    DISPLAY_NAME = "个人软件管理"

    # 常见个人软件：名称 -> (关键词列表, 数据目录模板列表, 注册表残留路径模板列表)
    PERSONAL_APPS = {
        "网易云音乐": {
            "keywords": ["netease", "cloudmusic", "网易云"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Netease\CloudMusic",
                r"%APPDATA%\Netease\CloudMusic",
                r"%LOCALAPPDATA%\Netease",
            ],
            "reg_keys": [r"SOFTWARE\Netease"],
        },
        "百度网盘": {
            "keywords": ["baidu", "baidunetdisk", "百度网盘"],
            "data_dirs": [
                r"%APPDATA%\baidu\BaiduNetdisk",
                r"%LOCALAPPDATA%\BaiduNetdisk",
                r"%APPDATA%\Baidu",
            ],
            "reg_keys": [r"SOFTWARE\Baidu"],
        },
        "迅雷": {
            "keywords": ["thunder", "迅雷"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Thunder Network",
                r"%APPDATA%\Thunder Network",
            ],
            "reg_keys": [r"SOFTWARE\Thunder Network"],
        },
        "QQ音乐": {
            "keywords": ["qqmusic", "qq音乐"],
            "data_dirs": [
                r"%APPDATA%\Tencent\QQMusic",
                r"%LOCALAPPDATA%\Tencent\QQMusic",
            ],
            "reg_keys": [],
        },
        "爱奇艺": {
            "keywords": ["iqiyi", "爱奇艺"],
            "data_dirs": [
                r"%LOCALAPPDATA%\iqiyi",
                r"%APPDATA%\iqiyi",
            ],
            "reg_keys": [r"SOFTWARE\iqiyi"],
        },
        "腾讯视频": {
            "keywords": ["qqlive", "腾讯视频"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Tencent\QQLive",
                r"%APPDATA%\Tencent\QQLive",
            ],
            "reg_keys": [],
        },
        "WPS Office": {
            "keywords": ["wps", "kingsoft"],
            "data_dirs": [
                r"%APPDATA%\kingsoft",
                r"%LOCALAPPDATA%\Kingsoft",
            ],
            "reg_keys": [r"SOFTWARE\Kingsoft"],
        },
        "有道云笔记": {
            "keywords": ["youdao", "有道"],
            "data_dirs": [
                r"%APPDATA%\youdao",
                r"%LOCALAPPDATA%\youdao",
            ],
            "reg_keys": [r"SOFTWARE\Youdao"],
        },
        "Spotify": {
            "keywords": ["spotify"],
            "data_dirs": [
                r"%APPDATA%\Spotify",
                r"%LOCALAPPDATA%\Spotify",
            ],
            "reg_keys": [r"SOFTWARE\Spotify"],
        },
        "Steam": {
            "keywords": ["steam", "valve"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Steam",
                r"%APPDATA%\Steam",
            ],
            "reg_keys": [r"SOFTWARE\Valve"],
        },
        "抖音(PC)": {
            "keywords": ["douyin", "抖音"],
            "data_dirs": [r"%LOCALAPPDATA%\Douyin"],
            "reg_keys": [],
        },
        "向日葵远程控制": {
            "keywords": ["sunlogin", "oray", "向日葵"],
            "data_dirs": [
                r"%APPDATA%\Oray\SunloginClient",
                r"%APPDATA%\Oray",
                r"%LOCALAPPDATA%\Oray",
            ],
            "reg_keys": [r"SOFTWARE\Oray"],
        },
        "ToDesk": {
            "keywords": ["todesk"],
            "data_dirs": [
                r"%APPDATA%\ToDesk",
                r"%LOCALAPPDATA%\ToDesk",
            ],
            "reg_keys": [],
        },
        "微博": {
            "keywords": ["weibo", "微博"],
            "data_dirs": [r"%APPDATA%\weibo"],
            "reg_keys": [],
        },
        "Telegram": {
            "keywords": ["telegram"],
            "data_dirs": [r"%APPDATA%\Telegram Desktop"],
            "reg_keys": [],
        },
        "Visual Studio Code": {
            "keywords": ["visual studio code", "vscode"],
            "data_dirs": [
                r"%APPDATA%\Code",
                r"%USERPROFILE%\.vscode",
            ],
            "reg_keys": [],
        },
        "个人版 Office": {
            "keywords": [],
            "data_dirs": [],
            "reg_keys": [],
        },
    }

    # 注册表中用于匹配个人软件的关键词
    INSTALL_KEYWORDS = [
        "网易", "netease", "百度", "baidu", "迅雷", "thunder",
        "qq音乐", "qqmusic", "爱奇艺", "iqiyi", "腾讯视频", "qqlive",
        "spotify", "steam", "wechat", "微信", "telegram",
        "抖音", "douyin", "tiktok", "向日葵", "sunlogin", "todesk",
        "wps office", "kingsoft", "有道", "youdao", "weibo", "微博",
        "哔哩哔哩", "bilibili", "clash", "v2ray", "shadowsocks",
        "notion", "obsidian", "typora", "picgo",
    ]

    def __init__(self):
        self._installed_cache = []  # [(name, uninstall_cmd, install_location, reg_subkey_path)]

    def scan(self) -> list:
        """
        扫描结果格式: [(描述, action_key, 大小/状态, 存在)]
        action_key 格式:
          - "data:<目录路径>"        → 清除数据目录
          - "uninstall:<卸载命令>"   → 执行卸载
          - "regclean:<注册表路径>"  → 清除注册表残留
        """
        results = []

        # 1) 扫描已安装的个人软件（可卸载）
        self._installed_cache = self._scan_installed_apps()
        for name, uninstall_cmd, install_loc, _ in self._installed_cache:
            size_str = "已安装"
            if install_loc and os.path.isdir(install_loc):
                size_str = format_size(get_dir_size(install_loc))
            results.append((
                f"[卸载] {name}",
                f"uninstall:{uninstall_cmd}",
                size_str,
                True
            ))

        # 2) 扫描数据目录残留
        for app_name, info in self.PERSONAL_APPS.items():
            for tmpl in info["data_dirs"]:
                path = os.path.expandvars(tmpl)
                if check_path_exists(path):
                    size = format_size(get_dir_size(path))
                    results.append((
                        f"[数据] {app_name}",
                        f"data:{path}",
                        size,
                        True
                    ))

        # 3) 扫描注册表残留
        for app_name, info in self.PERSONAL_APPS.items():
            for reg_path in info.get("reg_keys", []):
                if self._reg_key_exists(reg_path):
                    results.append((
                        f"[注册表] {app_name}",
                        f"regclean:HKCU\\{reg_path}",
                        "注册表残留",
                        True
                    ))

        # 4) 扫描桌面快捷方式残留
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcuts = self._scan_shortcuts(desktop)
        for name, path in shortcuts:
            results.append((
                f"[快捷方式] {name}",
                f"data:{path}",
                "快捷方式",
                True
            ))

        # 5) 扫描开始菜单残留
        start_menu = os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs"
        )
        start_shortcuts = self._scan_shortcuts(start_menu)
        for name, path in start_shortcuts:
            results.append((
                f"[开始菜单] {name}",
                f"data:{path}",
                "快捷方式",
                True
            ))

        return results

    def clean(self, paths: list, logger) -> int:
        """执行清理：卸载软件、删除数据、清注册表"""
        cleaned = 0
        for action_key in paths:
            try:
                if action_key.startswith("uninstall:"):
                    cmd = action_key[len("uninstall:"):]
                    cleaned += self._do_uninstall(cmd, logger)
                elif action_key.startswith("data:"):
                    path = action_key[len("data:"):]
                    cleaned += self._do_remove_data(path, logger)
                elif action_key.startswith("regclean:"):
                    reg = action_key[len("regclean:"):]
                    cleaned += self._do_remove_reg(reg, logger)
            except Exception as e:
                logger.error(f"操作失败 {action_key}: {e}")
        return cleaned

    # ==================== 卸载软件 ====================

    def _do_uninstall(self, uninstall_cmd: str, logger) -> int:
        """执行软件卸载"""
        if not uninstall_cmd or uninstall_cmd == "无卸载命令":
            logger.warning("该软件无卸载命令，请手动卸载")
            return 0

        logger.info(f"正在卸载: {uninstall_cmd}")
        try:
            # 处理卸载命令：有些带引号，有些带 /S 静默参数
            cmd = uninstall_cmd.strip('"')

            # 尝试静默卸载（常见静默参数）
            silent_flags = ["/S", "/silent", "/quiet", "--uninstall", "/uninstall"]
            for flag in silent_flags:
                if flag.lower() in cmd.lower():
                    break
            else:
                # 命令本身不含静默参数，尝试加 /S
                if cmd.lower().endswith(".exe"):
                    cmd = f'"{cmd}" /S'
                elif "msiexec" in cmd.lower():
                    if "/quiet" not in cmd.lower():
                        cmd = cmd + " /quiet /norestart"

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                logger.success(f"卸载成功: {uninstall_cmd}")
                return 1
            else:
                # 静默卸载失败，启动交互式卸载
                logger.warning(f"静默卸载未成功(code={result.returncode})，尝试交互式卸载...")
                subprocess.Popen(uninstall_cmd, shell=True)
                logger.info("已启动卸载程序，请在弹出的窗口中完成卸载")
                return 1
        except subprocess.TimeoutExpired:
            logger.warning("卸载超时，已启动卸载程序，请手动完成")
            return 1
        except Exception as e:
            logger.error(f"卸载失败: {e}")
            # 最后兜底：直接启动卸载程序
            try:
                subprocess.Popen(uninstall_cmd, shell=True)
                logger.info("已启动卸载程序，请手动完成卸载")
                return 1
            except Exception:
                logger.error(f"无法启动卸载程序: {uninstall_cmd}")
                return 0

    # ==================== 删除数据 ====================

    def _do_remove_data(self, path: str, logger) -> int:
        """删除数据文件或目录"""
        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.success(f"已删除文件: {path}")
                return 1
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=False)
                logger.success(f"已删除目录: {path}")
                return 1
            else:
                logger.warning(f"路径不存在: {path}")
                return 0
        except PermissionError:
            # 尝试强制删除（文件被占用时）
            try:
                subprocess.run(
                    f'rd /s /q "{path}"', shell=True,
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                if not os.path.exists(path):
                    logger.success(f"已强制删除: {path}")
                    return 1
                else:
                    logger.error(f"权限不足，无法删除: {path}（请先关闭相关软件）")
                    return 0
            except Exception:
                logger.error(f"权限不足: {path}（请先关闭相关软件）")
                return 0
        except Exception as e:
            logger.error(f"删除失败 {path}: {e}")
            return 0

    # ==================== 清除注册表残留 ====================

    def _do_remove_reg(self, reg_path: str, logger) -> int:
        """清除注册表残留"""
        # reg_path 格式: "HKCU\SOFTWARE\Xxx"
        try:
            result = subprocess.run(
                f'reg delete "{reg_path}" /f',
                shell=True, capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                logger.success(f"已清除注册表: {reg_path}")
                return 1
            else:
                logger.warning(f"注册表项不存在或无权限: {reg_path}")
                return 0
        except Exception as e:
            logger.error(f"清除注册表失败 {reg_path}: {e}")
            return 0

    # ==================== 扫描工具方法 ====================

    def _scan_installed_apps(self) -> list:
        """从注册表扫描已安装的个人软件
        返回: [(显示名, 卸载命令, 安装路径, 注册表子键路径)]
        """
        results = []
        seen_names = set()
        reg_roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for hive, reg_path in reg_roots:
            try:
                key = winreg.OpenKey(hive, reg_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            name_lower = name.lower()
                            if name_lower in seen_names:
                                continue
                            if any(kw in name_lower for kw in self.INSTALL_KEYWORDS):
                                seen_names.add(name_lower)
                                uninstall = self._reg_value(subkey, "UninstallString", "无卸载命令")
                                install_loc = self._reg_value(subkey, "InstallLocation", "")
                                hive_name = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
                                full_reg = f"{hive_name}\\{reg_path}\\{subkey_name}"
                                results.append((name, uninstall, install_loc, full_reg))
                        except FileNotFoundError:
                            pass
                        winreg.CloseKey(subkey)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass
        return results

    def _scan_shortcuts(self, directory: str) -> list:
        """扫描目录中属于个人软件的快捷方式"""
        results = []
        if not os.path.isdir(directory):
            return results
        all_keywords = []
        for info in self.PERSONAL_APPS.values():
            all_keywords.extend(info["keywords"])
        try:
            for entry in os.scandir(directory):
                if entry.name.lower().endswith(('.lnk', '.url')):
                    name_lower = entry.name.lower()
                    if any(kw in name_lower for kw in all_keywords):
                        results.append((entry.name, entry.path))
                elif entry.is_dir():
                    # 检查开始菜单子文件夹
                    folder_lower = entry.name.lower()
                    if any(kw in folder_lower for kw in all_keywords):
                        results.append((entry.name, entry.path))
        except (OSError, PermissionError):
            pass
        return results

    @staticmethod
    def _reg_value(key, name: str, default: str) -> str:
        try:
            return winreg.QueryValueEx(key, name)[0]
        except FileNotFoundError:
            return default

    @staticmethod
    def _reg_key_exists(subpath: str) -> bool:
        """检查 HKCU 下的注册表键是否存在"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subpath)
            winreg.CloseKey(key)
            return True
        except OSError:
            return False
