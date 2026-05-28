"""
离职数据清理助手 v4.0 (PyWebView Entry)
桥接 Python 后端与 Vue 3 前端
"""

import os
import sys
import time
import threading
import webview

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cleaners.browser import BrowserCleaner
from cleaners.chat import ChatCleaner
from cleaners.files import FileCleaner
from cleaners.credentials import CredentialCleaner
from cleaners.software import SoftwareCleaner
from cleaners.aitools import AIToolsCleaner
from cleaners.devenv import DevEnvCleaner
from cleaners.selfclean import SelfCleaner
from utils.logger import CleanLogger
from utils.scanner import format_size


class PyAPI:
    def __init__(self):
        self._logger = CleanLogger()
        self._cleaners = {
            "browser": BrowserCleaner(),
            "chat": ChatCleaner(),
            "files": FileCleaner(),
            "credentials": CredentialCleaner(),
            "aitools": AIToolsCleaner(),
            "devenv": DevEnvCleaner(),
            "software": SoftwareCleaner(),
            "selfclean": SelfCleaner(),
        }
        self._window = None

    def scan(self):
        self._logger.info("开始系统数据痕迹扫描...")
        results = {}
        for key, cl in self._cleaners.items():
            t0 = time.time()
            try:
                res = cl.scan()
                results[key] = res
                self._logger.success(f"加载 [{cl.DISPLAY_NAME}] 模块成功 ({time.time() - t0:.2f}s)")
            except Exception as e:
                self._logger.error(f"加载 [{cl.DISPLAY_NAME}] 模块失败: {e}")
                results[key] = []
        return results

    def clean_paths(self, cat_key, paths):
        cl = self._cleaners.get(cat_key)
        if not cl:
            return 0
        t0 = time.time()
        try:
            count = cl.clean(paths, self._logger)
            self._logger.success(f"[{cl.DISPLAY_NAME}] 清理完成，共清理 {count} 项 ({time.time() - t0:.2f}s)")
            
            # 自卸载自毁逻辑
            if getattr(cl, "self_destruct_triggered", False):
                import subprocess
                import tempfile
                batch_path = os.path.join(tempfile.gettempdir(), "leaveclean_selfdestruct.bat")
                subprocess.Popen(
                    ["cmd.exe", "/c", batch_path],
                    shell=False,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    close_fds=True,
                )
                
                # 延时关闭窗口
                def delay_close():
                    time.sleep(1.5)
                    if self._window:
                        self._window.destroy()
                threading.Thread(target=delay_close, daemon=True).start()
                
            return count
        except Exception as e:
            self._logger.error(f"[{cl.DISPLAY_NAME}] 清理失败: {e}")
            return 0

    def get_new_logs(self):
        logs = list(self._logger.records)
        self._logger.records.clear()
        return logs

    def get_path_details(self, cat_key, path):
        real_path = path
        for prefix in ["uninstall:", "data:", "regclean:", "selfdestruct:", "manual_review:"]:
            if real_path.startswith(prefix):
                real_path = real_path[len(prefix):]
                break
        
        if path.startswith("uninstall:"):
            return f"类型: 软件卸载\n卸载命令: {real_path}\n\n点击“清除选中”或使用右键以执行静默/交互式卸载。"
        if path.startswith("regclean:"):
            return f"类型: 注册表残留\n项路径: {real_path}\n\n执行清理后将彻底删除该注册表项。"
        if path.startswith("manual_review:"):
            return f"类型: 建议手动处理目录\n目录路径: {real_path}\n\n【安全提醒】本应用不会自动删除此目录以防误杀您的个人重要文件（如简历、照片、合同等）。建议在该目录下手动核对备份后进行清理。"

        if not os.path.exists(real_path):
            return f"路径不存在: {real_path}"

        if os.path.isfile(real_path):
            try:
                ext = os.path.splitext(real_path)[1].lower()
                if ext in (".json", ".txt", ".log", ".ini", ".cfg", ".conf", ".xml", ".yaml", ".yml", ".toml", ".gitconfig", ".npmrc", ".condarc", ".zshrc", ".history"):
                    with open(real_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()[:20]
                    content = ""
                    for line in lines:
                        d = line.rstrip()
                        for kw in ["password", "token", "secret", "key", "credential", "api_key", "private"]:
                            if kw in d.lower() and ("=" in d or ":" in d):
                                sep = "=" if "=" in d else ":"
                                parts = d.split(sep, 1)
                                if len(parts[1].strip()) > 3:
                                    d = parts[0] + sep + " ********"
                                break
                        content += d + "\n"
                    return f"文件大小: {format_size(os.path.getsize(real_path))}\n内容预览:\n---\n{content}"
                elif ext in (".pub", ".pem") or "id_rsa" in real_path:
                    return f"⚠️ 极度敏感的密钥文件！请务必清理。\n文件大小: {format_size(os.path.getsize(real_path))}"
                else:
                    return f"类型: 二进制文件\n大小: {format_size(os.path.getsize(real_path))}"
            except Exception as e:
                return f"无法读取文件详情: {e}"

        if os.path.isdir(real_path):
            try:
                ents = []
                for e in os.scandir(real_path):
                    try:
                        if e.is_dir(follow_symlinks=False):
                            ents.append(f"📁 {e.name}")
                        else:
                            ents.append(f"📄 {e.name} ({format_size(e.stat(follow_symlinks=False).st_size)})")
                    except Exception:
                        pass
                if not ents:
                    return "空目录"
                ents.sort()
                content = "\n".join(ents[:30])
                if len(ents) > 30:
                    content += f"\n... 以及其它 {len(ents) - 30} 项"
                return f"目录包含 {len(ents)} 个子项:\n---\n{content}"
            except Exception as e:
                return f"无法读取目录详情: {e}"

        return f"未识别的项目路径: {real_path}"

    def open_path(self, path):
        real_path = path
        for prefix in ["uninstall:", "data:", "regclean:", "selfdestruct:", "manual_review:"]:
            if real_path.startswith(prefix):
                real_path = real_path[len(prefix):]
                break
        if os.path.isfile(real_path):
            real_path = os.path.dirname(real_path)
        if os.path.isdir(real_path):
            try:
                os.startfile(real_path)
                return True
            except Exception:
                return False
        return False

    def copy_path(self, path):
        real_path = path
        for prefix in ["uninstall:", "data:", "regclean:", "selfdestruct:", "manual_review:"]:
            if real_path.startswith(prefix):
                real_path = real_path[len(prefix):]
                break
        try:
            import tkinter as tk
            r = tk.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(real_path)
            r.update()
            r.destroy()
            return True
        except Exception:
            return False


def get_entry_url():
    # 检测本地开发目录。如果在开发阶段，Vite 服务器会在 5173 端口运行，直接加载 localhost
    # 发布时：查找打包编译生成的 frontend/dist/index.html 静态资源并加载它
    dev_url = "http://localhost:5173"
    dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist", "index.html")
    if os.path.exists(dist_path):
        return dist_path
    return dev_url


if __name__ == "__main__":
    py_api = PyAPI()
    
    # 窗口宽度高度匹配原 GUI 尺寸
    window = webview.create_window(
        title="离职数据清理助手 v4.0",
        url=get_entry_url(),
        js_api=py_api,
        width=1150,
        height=750,
        min_size=(900, 600),
        resizable=True
    )
    
    # 保存窗口实例引用，供自毁逻辑调用 destroy
    py_api._window = window
    
    # 启动 PyWebView 渲染循环
    webview.start()
