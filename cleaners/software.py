"""个人软件卸载与数据清理（全面覆盖版）"""
import os
import shutil
import subprocess
import winreg
from utils.scanner import check_path_exists, get_dir_size_fast, format_size


class SoftwareCleaner:
    DISPLAY_NAME = "个人软件管理"

    # ========== 个人软件数据库 ==========
    # 每项: keywords(注册表匹配), data_dirs(数据目录), reg_keys(注册表残留)
    PERSONAL_APPS = {
        # ----- 音乐 -----
        "网易云音乐": {
            "keywords": ["netease", "cloudmusic", "网易云"],
            "data_dirs": [
                r"%LOCALAPPDATA%\NetEase",
                r"%APPDATA%\Netease",
            ],
            "reg_keys": [r"SOFTWARE\Netease"],
        },
        "QQ音乐": {
            "keywords": ["qqmusic", "qq音乐"],
            "data_dirs": [
                r"%APPDATA%\Tencent\QQMusic",
                r"%LOCALAPPDATA%\Tencent\QQMusic",
            ],
            "reg_keys": [],
        },
        "汽水音乐/Soda Music": {
            "keywords": ["sodamusic", "soda music"],
            "data_dirs": [r"%APPDATA%\SodaMusic"],
            "reg_keys": [],
        },
        "Spotify": {
            "keywords": ["spotify"],
            "data_dirs": [r"%APPDATA%\Spotify", r"%LOCALAPPDATA%\Spotify"],
            "reg_keys": [r"SOFTWARE\Spotify"],
        },
        # ----- 视频 -----
        "腾讯视频": {
            "keywords": ["qqlive", "腾讯视频"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Tencent\QQLive",
                r"%APPDATA%\Tencent\QQLive",
            ],
            "reg_keys": [],
        },
        "爱奇艺": {
            "keywords": ["iqiyi", "爱奇艺"],
            "data_dirs": [r"%LOCALAPPDATA%\iqiyi", r"%APPDATA%\iqiyi"],
            "reg_keys": [r"SOFTWARE\iqiyi"],
        },
        "哔哩哔哩": {
            "keywords": ["bilibili", "哔哩哔哩"],
            "data_dirs": [r"%LOCALAPPDATA%\bilibili"],
            "reg_keys": [],
        },
        "剪映专业版": {
            "keywords": ["jianyingpro", "剪映"],
            "data_dirs": [
                r"%LOCALAPPDATA%\JianyingPro",
                r"%APPDATA%\JianyingPro",
            ],
            "reg_keys": [],
        },
        # ----- 网盘/下载 -----
        "百度网盘": {
            "keywords": ["baidu", "baidunetdisk", "百度网盘"],
            "data_dirs": [
                r"%APPDATA%\baidu",
                r"%APPDATA%\BaiduYunGuanjia",
                r"%APPDATA%\BaiduYunKernel",
                r"%LOCALAPPDATA%\BaiduNetdisk",
            ],
            "reg_keys": [r"SOFTWARE\Baidu"],
        },
        "夸克网盘": {
            "keywords": ["quark", "夸克"],
            "data_dirs": [
                r"%APPDATA%\Quark",
                r"%APPDATA%\The Quark Authors",
            ],
            "reg_keys": [],
        },
        "迅雷": {
            "keywords": ["thunder", "迅雷", "xunlei"],
            "data_dirs": [
                r"%APPDATA%\thunder",
                r"%LOCALAPPDATA%\Thunder Network",
            ],
            "reg_keys": [r"SOFTWARE\Thunder Network"],
        },
        # ----- 远程控制 -----
        "向日葵远程控制": {
            "keywords": ["sunlogin", "oray", "向日葵"],
            "data_dirs": [
                r"%APPDATA%\Oray",
                r"%LOCALAPPDATA%\Oray",
                r"%LOCALAPPDATA%\SunBrowse",
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
        "AweSun": {
            "keywords": ["awesun"],
            "data_dirs": [r"%APPDATA%\AweSun"],
            "reg_keys": [],
        },
        # ----- VPN/代理 -----
        "Clash Verge": {
            "keywords": ["clash", "clash-verge"],
            "data_dirs": [
                r"%APPDATA%\clash_win",
                r"%APPDATA%\io.github.clash-verge-rev.clash-verge-rev",
                r"%LOCALAPPDATA%\io.github.clash-verge-rev.clash-verge-rev",
            ],
            "reg_keys": [],
        },
        "v2rayN": {
            "keywords": ["v2ray"],
            "data_dirs": [r"%LOCALAPPDATA%\v2rayN"],
            "reg_keys": [],
        },
        # ----- 办公 -----
        "WPS Office": {
            "keywords": ["wps", "kingsoft"],
            "data_dirs": [
                r"%APPDATA%\kingsoft",
                r"%LOCALAPPDATA%\Kingsoft",
                r"%USERPROFILE%\Documents\WPSDrive",
                r"%USERPROFILE%\Documents\KingsoftData",
                r"%APPDATA%\third_wpsdc",
            ],
            "reg_keys": [r"SOFTWARE\Kingsoft"],
        },
        "Postman": {
            "keywords": ["postman"],
            "data_dirs": [r"%APPDATA%\Postman"],
            "reg_keys": [],
        },
        "Apifox": {
            "keywords": ["apifox"],
            "data_dirs": [
                r"%APPDATA%\apifox",
                r"%LOCALAPPDATA%\apifox-updater",
            ],
            "reg_keys": [],
        },
        "Navicat": {
            "keywords": ["navicat"],
            "data_dirs": [r"%USERPROFILE%\Documents\Navicat"],
            "reg_keys": [],
        },
        # ----- 开发工具 -----
        "Visual Studio Code": {
            "keywords": ["visual studio code", "vscode"],
            "data_dirs": [
                r"%APPDATA%\Code",
                r"%USERPROFILE%\.vscode",
            ],
            "reg_keys": [],
        },
        "Cursor": {
            "keywords": ["cursor"],
            "data_dirs": [r"%APPDATA%\Cursor"],
            "reg_keys": [],
        },
        "Windsurf": {
            "keywords": ["windsurf"],
            "data_dirs": [
                r"%APPDATA%\Windsurf",
                r"%APPDATA%\WindsurfTools",
            ],
            "reg_keys": [],
        },
        "Trae / Trae CN": {
            "keywords": ["trae"],
            "data_dirs": [
                r"%APPDATA%\Trae",
                r"%APPDATA%\Trae CN",
                r"%APPDATA%\TRAE SOLO",
            ],
            "reg_keys": [],
        },
        "Kiro": {
            "keywords": ["kiro"],
            "data_dirs": [
                r"%APPDATA%\Kiro",
                r"%APPDATA%\kiro-account-manager",
            ],
            "reg_keys": [],
        },
        "JetBrains 全家桶": {
            "keywords": ["jetbrains", "intellij", "pycharm", "webstorm", "goland", "rider", "clion", "datagrip"],
            "data_dirs": [
                r"%APPDATA%\JetBrains",
                r"%LOCALAPPDATA%\JetBrains",
            ],
            "reg_keys": [],
        },
        "HBuilder X": {
            "keywords": ["hbuilder"],
            "data_dirs": [
                r"%APPDATA%\HBuilder X",
                r"%LOCALAPPDATA%\HBuilder X",
            ],
            "reg_keys": [],
        },
        "SourceTree": {
            "keywords": ["sourcetree", "atlassian"],
            "data_dirs": [
                r"%LOCALAPPDATA%\SourceTree",
                r"%LOCALAPPDATA%\Atlassian",
                r"%APPDATA%\Atlassian",
            ],
            "reg_keys": [],
        },
        "Docker Desktop": {
            "keywords": ["docker"],
            "data_dirs": [
                r"%APPDATA%\Docker",
                r"%APPDATA%\Docker Desktop",
                r"%LOCALAPPDATA%\Docker",
            ],
            "reg_keys": [],
        },
        "Anaconda/Conda": {
            "keywords": ["anaconda", "conda", "miniconda"],
            "data_dirs": [
                r"%LOCALAPPDATA%\conda",
                r"%APPDATA%\conda-anaconda-tos",
            ],
            "reg_keys": [],
        },
        # ----- 浏览器 -----
        "搜狗浏览器": {
            "keywords": ["sogou", "搜狗"],
            "data_dirs": [r"%APPDATA%\SogouExplorer"],
            "reg_keys": [],
        },
        "360浏览器": {
            "keywords": ["360se", "360浏览器", "360安全浏览器"],
            "data_dirs": [r"%APPDATA%\360se6"],
            "reg_keys": [],
        },
        "猎豹浏览器": {
            "keywords": ["liebao", "猎豹"],
            "data_dirs": [r"%LOCALAPPDATA%\liebao"],
            "reg_keys": [],
        },
        # ----- 游戏 -----
        "Steam": {
            "keywords": ["steam", "valve"],
            "data_dirs": [r"%LOCALAPPDATA%\Steam"],
            "reg_keys": [r"SOFTWARE\Valve"],
        },
        "WeGame": {
            "keywords": ["wegame"],
            "data_dirs": [r"%LOCALAPPDATA%\WeGame"],
            "reg_keys": [],
        },
        # ----- 社交/娱乐 -----
        "抖音(PC)": {
            "keywords": ["douyin", "抖音", "bytedance"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Douyin",
                r"%LOCALAPPDATA%\Bytedance",
            ],
            "reg_keys": [],
        },
        "小红书": {
            "keywords": ["小红书", "xhs"],
            "data_dirs": [r"%APPDATA%\@xhs"],
            "reg_keys": [],
        },
        "微博": {
            "keywords": ["weibo", "微博"],
            "data_dirs": [r"%APPDATA%\weibo"],
            "reg_keys": [],
        },
        # ----- 笔记/知识 -----
        "有道云笔记": {
            "keywords": ["youdao", "有道"],
            "data_dirs": [r"%APPDATA%\youdao", r"%LOCALAPPDATA%\youdao"],
            "reg_keys": [r"SOFTWARE\Youdao"],
        },
        "Notion": {
            "keywords": ["notion"],
            "data_dirs": [r"%APPDATA%\Notion"],
            "reg_keys": [],
        },
        "Obsidian": {
            "keywords": ["obsidian"],
            "data_dirs": [r"%APPDATA%\obsidian"],
            "reg_keys": [],
        },
        "Typora": {
            "keywords": ["typora"],
            "data_dirs": [r"%APPDATA%\Typora"],
            "reg_keys": [],
        },
        # ----- 华为云/阿里云 -----
        "华为云": {
            "keywords": ["huaweicloud", "华为云"],
            "data_dirs": [
                r"%LOCALAPPDATA%\HuaweiCloud",
                r"%APPDATA%\HuaweiCloud",
                r"%APPDATA%\com.huawei.cloud.accountkit",
                r"%LOCALAPPDATA%\Huawei",
                r"%APPDATA%\Huawei",
            ],
            "reg_keys": [],
        },
        # ----- 杀毒/安全 -----
        "Avast": {
            "keywords": ["avast"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Avast Software",
                r"%APPDATA%\Avast Software",
            ],
            "reg_keys": [],
        },
        "McAfee": {
            "keywords": ["mcafee"],
            "data_dirs": [r"%LOCALAPPDATA%\McAfee"],
            "reg_keys": [],
        },
        # ----- 其他工具 -----
        "uTools": {
            "keywords": ["utools"],
            "data_dirs": [
                r"%APPDATA%\uTools",
                r"%LOCALAPPDATA%\utools-updater",
            ],
            "reg_keys": [],
        },
        "OrcaTerm": {
            "keywords": ["orcaterm"],
            "data_dirs": [
                r"%LOCALAPPDATA%\OrcaTerm",
                r"%APPDATA%\com.orcaterm-desktop.app",
            ],
            "reg_keys": [],
        },
        "ChatBox AI": {
            "keywords": ["chatbox"],
            "data_dirs": [r"%APPDATA%\xyz.chatboxapp.app"],
            "reg_keys": [],
        },
        "Ollama": {
            "keywords": ["ollama"],
            "data_dirs": [r"%USERPROFILE%\.ollama"],
            "reg_keys": [],
        },
        "VMware": {
            "keywords": ["vmware"],
            "data_dirs": [
                r"%APPDATA%\VMware",
                r"%LOCALAPPDATA%\VMware",
            ],
            "reg_keys": [],
        },
        "MuMu模拟器": {
            "keywords": ["mumu", "nemu"],
            "data_dirs": [r"%LOCALAPPDATA%\MuMuNxDevice"],
            "reg_keys": [],
        },
        "Godot引擎": {
            "keywords": ["godot"],
            "data_dirs": [
                r"%APPDATA%\Godot",
                r"%LOCALAPPDATA%\Godot",
            ],
            "reg_keys": [],
        },
        "Axure RP": {
            "keywords": ["axure"],
            "data_dirs": [
                r"%LOCALAPPDATA%\Axure",
                r"%USERPROFILE%\Documents\Axure",
            ],
            "reg_keys": [],
        },
        "腾讯元宝": {
            "keywords": ["yuanbao", "元宝"],
            "data_dirs": [r"%APPDATA%\com.tencent.yuanbao"],
            "reg_keys": [],
        },
        "Devin": {
            "keywords": ["devin"],
            "data_dirs": [
                r"%LOCALAPPDATA%\devin",
                r"%APPDATA%\devin",
            ],
            "reg_keys": [],
        },
        "Antigravity": {
            "keywords": ["antigravity"],
            "data_dirs": [
                r"%LOCALAPPDATA%\antigravity",
                r"%APPDATA%\Antigravity",
                r"%APPDATA%\Antigravity IDE",
            ],
            "reg_keys": [],
        },
        "AdsPoweR": {
            "keywords": ["adspower"],
            "data_dirs": [
                r"%APPDATA%\adspower_global",
                r"%LOCALAPPDATA%\adspower_global-updater",
            ],
            "reg_keys": [],
        },
        "TortoiseGit": {
            "keywords": ["tortoisegit"],
            "data_dirs": [r"%APPDATA%\TortoiseGit"],
            "reg_keys": [],
        },
        "NetSarang (Xshell/Xftp)": {
            "keywords": ["netsarang", "xshell", "xftp"],
            "data_dirs": [r"%USERPROFILE%\Documents\NetSarang Computer"],
            "reg_keys": [],
        },
        "MagicDanmaku": {
            "keywords": ["magicdanmaku"],
            "data_dirs": [r"%LOCALAPPDATA%\MagicDanmaku"],
            "reg_keys": [],
        },
    }

    # 注册表匹配关键词（用于卸载列表）
    INSTALL_KEYWORDS = [
        # 通讯
        "wechat", "微信", "qq", "telegram", "dingtalk", "钉钉", "飞书", "lark",
        "feishu", "foxmail", "企业微信", "wxwork",
        # 音视频
        "网易", "netease", "qqmusic", "qq音乐", "spotify", "soda music",
        "爱奇艺", "iqiyi", "腾讯视频", "qqlive", "bilibili", "哔哩哔哩",
        "剪映", "jianyingpro",
        # 网盘下载
        "百度", "baidu", "迅雷", "thunder", "xunlei", "quark", "夸克",
        # 远程
        "向日葵", "sunlogin", "todesk", "awesun",
        # VPN
        "clash", "v2ray", "shadowsocks",
        # 办公
        "wps", "kingsoft", "postman", "apifox", "navicat",
        # 开发
        "vscode", "visual studio code", "cursor", "windsurf", "trae",
        "kiro", "jetbrains", "intellij", "pycharm", "webstorm", "goland",
        "hbuilder", "sourcetree", "docker", "anaconda", "conda",
        # 浏览器
        "sogou", "搜狗", "360se", "360浏览器", "猎豹", "liebao",
        # 游戏
        "steam", "wegame",
        # 社交
        "抖音", "douyin", "tiktok", "小红书", "xhs", "weibo", "微博",
        # 笔记
        "有道", "youdao", "notion", "obsidian", "typora",
        # 工具
        "utools", "orcaterm", "chatbox", "ollama", "vmware", "mumu",
        "axure", "tortoisegit", "netsarang", "xshell", "xftp",
        "antigravity", "adspower", "avast", "mcafee",
        "huaweicloud", "华为云", "godot", "devin",
        "腾讯元宝", "magicdan",
    ]

    def __init__(self):
        pass

    def scan(self) -> list:
        """扫描结果格式: [(描述, action_key, 大小/状态, 存在)]"""
        results = []

        # 1) 数据目录残留
        for app_name, info in self.PERSONAL_APPS.items():
            for tmpl in info["data_dirs"]:
                path = os.path.expandvars(tmpl)
                if check_path_exists(path):
                    size = format_size(get_dir_size_fast(path))
                    results.append((f"[数据] {app_name}", f"data:{path}", size, True))

        # 2) 注册表残留
        for app_name, info in self.PERSONAL_APPS.items():
            for reg_path in info.get("reg_keys", []):
                if self._reg_key_exists(reg_path):
                    results.append((
                        f"[注册表] {app_name}",
                        f"regclean:HKCU\\{reg_path}",
                        "注册表残留", True))

        # 3) 桌面快捷方式
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        for name, path in self._scan_shortcuts(desktop):
            results.append((f"[快捷方式] {name}", f"data:{path}", "快捷方式", True))

        # 4) 开始菜单快捷方式
        start_menu = os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs")
        for name, path in self._scan_shortcuts(start_menu):
            results.append((f"[开始菜单] {name}", f"data:{path}", "快捷方式", True))

        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for action_key in paths:
            try:
                if action_key.startswith("data:"):
                    cleaned += self._do_remove_data(action_key[5:], logger)
                elif action_key.startswith("regclean:"):
                    cleaned += self._do_remove_reg(action_key[9:], logger)
            except Exception as e:
                logger.error(f"操作失败 {action_key}: {e}")
        return cleaned

    # ==================== 删除数据 ====================

    def _do_remove_data(self, path: str, logger) -> int:
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
            try:
                subprocess.run(
                    f'rd /s /q "{path}"', shell=True,
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if not os.path.exists(path):
                    logger.success(f"已强制删除: {path}")
                    return 1
                logger.error(f"权限不足: {path}（请先关闭相关软件）")
                return 0
            except Exception:
                logger.error(f"权限不足: {path}")
                return 0
        except Exception as e:
            logger.error(f"删除失败 {path}: {e}")
            return 0

    # ==================== 注册表 ====================

    def _do_remove_reg(self, reg_path: str, logger) -> int:
        try:
            result = subprocess.run(
                f'reg delete "{reg_path}" /f', shell=True,
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                logger.success(f"已清除注册表: {reg_path}")
                return 1
            logger.warning(f"注册表项不存在或无权限: {reg_path}")
            return 0
        except Exception as e:
            logger.error(f"清除注册表失败 {reg_path}: {e}")
            return 0

    # ==================== 扫描工具 ====================


    def _scan_shortcuts(self, directory: str) -> list:
        results = []
        if not os.path.isdir(directory):
            return results
        kws = []
        for info in self.PERSONAL_APPS.values():
            kws.extend(info["keywords"])
        try:
            for entry in os.scandir(directory):
                nl = entry.name.lower()
                if entry.name.lower().endswith(('.lnk', '.url')):
                    if any(kw in nl for kw in kws):
                        results.append((entry.name, entry.path))
                elif entry.is_dir():
                    if any(kw in nl for kw in kws):
                        results.append((entry.name, entry.path))
        except (OSError, PermissionError):
            pass
        return results

    @staticmethod
    def _rv(key, name, default):
        try:
            return winreg.QueryValueEx(key, name)[0]
        except FileNotFoundError:
            return default

    @staticmethod
    def _reg_key_exists(subpath):
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subpath)
            winreg.CloseKey(k)
            return True
        except OSError:
            return False
