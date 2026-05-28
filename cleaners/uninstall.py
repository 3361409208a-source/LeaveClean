"""个人软件卸载模块"""
import os
import subprocess
import winreg
import shutil
from utils.scanner import get_dir_size_fast, format_size

class UninstallCleaner:
    DISPLAY_NAME = "软件卸载"

    # 注册表匹配关键词
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

    def scan(self) -> list:
        results = []
        installed = self._scan_installed_apps()
        for name, uninstall_cmd, install_loc, _ in installed:
            size_str = "已安装"
            if install_loc and os.path.isdir(install_loc):
                size_str = format_size(get_dir_size_fast(install_loc))
            results.append((f"[卸载] {name}", f"uninstall:{uninstall_cmd}", size_str, True))
        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for action_key in paths:
            try:
                if action_key.startswith("uninstall:"):
                    cleaned += self._do_uninstall(action_key[10:], logger)
            except Exception as e:
                logger.error(f"卸载操作失败 {action_key}: {e}")
        return cleaned

    def _do_uninstall(self, uninstall_cmd: str, logger) -> int:
        if not uninstall_cmd or uninstall_cmd == "无卸载命令":
            logger.warning("该软件无卸载命令，请手动卸载")
            return 0
        logger.info(f"正在卸载: {uninstall_cmd}")
        try:
            cmd = uninstall_cmd.strip('"')
            silent_flags = ["/S", "/silent", "/quiet", "--uninstall", "/uninstall"]
            has_silent = any(f.lower() in cmd.lower() for f in silent_flags)
            if not has_silent:
                if cmd.lower().endswith(".exe"):
                    cmd = f'"{cmd}" /S'
                elif "msiexec" in cmd.lower() and "/quiet" not in cmd.lower():
                    cmd += " /quiet /norestart"

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                logger.success(f"卸载成功: {uninstall_cmd}")
                return 1
            else:
                logger.warning(f"静默卸载未成功(code={result.returncode})，启动交互式卸载...")
                subprocess.Popen(uninstall_cmd, shell=True)
                logger.info("已启动卸载程序，请在弹出窗口中完成")
                return 1
        except subprocess.TimeoutExpired:
            logger.warning("卸载超时，请手动完成")
            return 1
        except Exception as e:
            logger.error(f"卸载失败: {e}")
            try:
                subprocess.Popen(uninstall_cmd, shell=True)
                logger.info("已启动卸载程序，请手动完成")
                return 1
            except Exception:
                logger.error(f"无法启动卸载程序: {uninstall_cmd}")
                return 0

    def _scan_installed_apps(self) -> list:
        results = []
        seen = set()
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
                        sub_name = winreg.EnumKey(key, i)
                        sub = winreg.OpenKey(key, sub_name)
                        try:
                            name = winreg.QueryValueEx(sub, "DisplayName")[0]
                            nl = name.lower()
                            if nl in seen:
                                continue
                            if any(kw in nl for kw in self.INSTALL_KEYWORDS):
                                seen.add(nl)
                                uninst = self._rv(sub, "UninstallString", "无卸载命令")
                                loc = self._rv(sub, "InstallLocation", "")
                                h = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
                                results.append((name, uninst, loc, f"{h}\\{reg_path}\\{sub_name}"))
                        except FileNotFoundError:
                            pass
                        winreg.CloseKey(sub)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass
        return results

    @staticmethod
    def _rv(key, name, default):
        try:
            return winreg.QueryValueEx(key, name)[0]
        except FileNotFoundError:
            return default
