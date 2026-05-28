"""
离职数据清理助手 v1.0
智能辅助清除工作电脑上的个人隐私数据
"""
import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cleaners.browser import BrowserCleaner
from cleaners.chat import ChatCleaner
from cleaners.files import FileCleaner
from cleaners.credentials import CredentialCleaner
from cleaners.software import SoftwareCleaner
from utils.logger import CleanLogger


class LeaveCleanApp:
    """离职清理助手主窗口"""

    TITLE = "离职数据清理助手 v1.0"
    WIDTH = 1000
    HEIGHT = 700

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.minsize(800, 550)
        self.root.configure(bg="#f0f0f0")

        # 初始化清理器
        self.cleaners = {
            "browser": BrowserCleaner(),
            "chat": ChatCleaner(),
            "files": FileCleaner(),
            "credentials": CredentialCleaner(),
            "software": SoftwareCleaner(),
        }

        self.logger = CleanLogger()
        self.scan_results = {}  # {category: [(desc, path, size, exists, var)]}
        self.check_vars = {}  # 所有勾选变量

        self._build_ui()

    def _build_ui(self):
        """构建主界面"""
        # ===== 顶部标题栏 =====
        header = tk.Frame(self.root, bg="#1a73e8", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="🧹 离职数据清理助手",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg="white", bg="#1a73e8"
        ).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            header, text="安全清理个人隐私数据，保护您的隐私",
            font=("Microsoft YaHei UI", 10),
            fg="#cce0ff", bg="#1a73e8"
        ).pack(side=tk.LEFT, padx=10, pady=10)

        # ===== 主内容区 =====
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#d0d0d0")
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        # --- 左侧：分类勾选区 ---
        left_frame = tk.LabelFrame(
            main_pane, text="  清理项目  ",
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=10
        )
        main_pane.add(left_frame, width=360)

        # 全选/取消全选
        ctrl_frame = tk.Frame(left_frame)
        ctrl_frame.pack(fill=tk.X, pady=(0, 5))

        self.select_all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            ctrl_frame, text="全选 / 取消全选",
            variable=self.select_all_var,
            command=self._toggle_select_all,
            font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)

        # 可滚动的勾选列表
        canvas = tk.Canvas(left_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.checklist_frame = tk.Frame(canvas)

        self.checklist_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.checklist_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 初始提示
        self.placeholder_label = tk.Label(
            self.checklist_frame,
            text="\n\n    请先点击「扫描」按钮\n    检测可清理的数据项\n",
            font=("Microsoft YaHei UI", 10),
            fg="#888", justify=tk.LEFT
        )
        self.placeholder_label.pack(pady=30)

        # --- 右侧：详情与日志 ---
        right_frame = tk.Frame(main_pane)
        main_pane.add(right_frame)

        # 扫描详情
        detail_frame = tk.LabelFrame(
            right_frame, text="  扫描详情  ",
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=5
        )
        detail_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("项目", "路径", "大小", "状态")
        self.detail_tree = ttk.Treeview(detail_frame, columns=columns, show="headings", height=12)
        self.detail_tree.heading("项目", text="项目")
        self.detail_tree.heading("路径", text="路径")
        self.detail_tree.heading("大小", text="大小")
        self.detail_tree.heading("状态", text="状态")
        self.detail_tree.column("项目", width=200)
        self.detail_tree.column("路径", width=250)
        self.detail_tree.column("大小", width=80, anchor=tk.CENTER)
        self.detail_tree.column("状态", width=80, anchor=tk.CENTER)

        tree_scroll = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=tree_scroll.set)
        self.detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 操作日志
        log_frame = tk.LabelFrame(
            right_frame, text="  操作日志  ",
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=5
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=8, wrap=tk.WORD,
            font=("Consolas", 9), state=tk.DISABLED,
            bg="#1e1e1e", fg="#00ff00"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ===== 底部按钮栏 =====
        bottom = tk.Frame(self.root, bg="#f0f0f0", height=55)
        bottom.pack(fill=tk.X, padx=10, pady=(5, 10))

        # 状态标签
        self.status_label = tk.Label(
            bottom, text="就绪 - 请先扫描",
            font=("Microsoft YaHei UI", 9),
            fg="#666", bg="#f0f0f0", anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        # 按钮
        btn_style = {"font": ("Microsoft YaHei UI", 11), "width": 14, "height": 1, "cursor": "hand2"}

        self.clean_btn = tk.Button(
            bottom, text="🗑️ 一键清理",
            bg="#d93025", fg="white", activebackground="#c62828",
            command=self._on_clean, state=tk.DISABLED, **btn_style
        )
        self.clean_btn.pack(side=tk.RIGHT, padx=5)

        self.scan_btn = tk.Button(
            bottom, text="🔍 扫描检测",
            bg="#1a73e8", fg="white", activebackground="#1565c0",
            command=self._on_scan, **btn_style
        )
        self.scan_btn.pack(side=tk.RIGHT, padx=5)

    # ==================== 扫描逻辑 ====================

    def _on_scan(self):
        """点击扫描按钮"""
        self.scan_btn.config(state=tk.DISABLED, text="扫描中...")
        self.clean_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在扫描...")
        self._clear_detail_tree()
        self._log("开始扫描个人数据...")

        thread = threading.Thread(target=self._do_scan, daemon=True)
        thread.start()

    def _do_scan(self):
        """在子线程中执行扫描"""
        self.scan_results.clear()
        total_found = 0

        for key, cleaner in self.cleaners.items():
            try:
                results = cleaner.scan()
                found = [r for r in results if r[3]]  # 只保留存在的
                self.scan_results[key] = results
                total_found += len(found)
                self.root.after(0, self._log, f"[{cleaner.DISPLAY_NAME}] 发现 {len(found)} 项可清理数据")
            except Exception as e:
                self.root.after(0, self._log, f"[错误] 扫描 {cleaner.DISPLAY_NAME} 失败: {e}")

        self.root.after(0, self._scan_complete, total_found)

    def _scan_complete(self, total):
        """扫描完成，更新 UI"""
        self._build_checklist()
        self._fill_detail_tree()
        self.scan_btn.config(state=tk.NORMAL, text="🔍 重新扫描")
        self.clean_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"扫描完成 - 发现 {total} 项可清理数据")
        self._log(f"扫描完成，共发现 {total} 项可清理数据")

    # ==================== 勾选列表 ====================

    def _build_checklist(self):
        """根据扫描结果构建左侧勾选列表"""
        for widget in self.checklist_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        category_names = {
            "browser": "🌐 浏览器数据",
            "chat": "💬 聊天软件",
            "files": "📁 个人文件",
            "credentials": "🔑 凭据与隐私",
            "software": "📦 个人软件痕迹",
        }

        for key, results in self.scan_results.items():
            found = [r for r in results if r[3]]
            if not found:
                continue

            # 分类标题
            cat_frame = tk.Frame(self.checklist_frame)
            cat_frame.pack(fill=tk.X, pady=(8, 2))

            cat_var = tk.BooleanVar(value=False)
            cat_cb = tk.Checkbutton(
                cat_frame,
                text=f"{category_names.get(key, key)} ({len(found)}项)",
                variable=cat_var,
                font=("Microsoft YaHei UI", 10, "bold"),
                fg="#1a73e8",
                command=lambda k=key, v=cat_var: self._toggle_category(k, v.get())
            )
            cat_cb.pack(anchor=tk.W)

            # 子项
            for desc, path, size, exists in found:
                item_frame = tk.Frame(self.checklist_frame)
                item_frame.pack(fill=tk.X, padx=(25, 0))

                var = tk.BooleanVar(value=False)
                text = f"{desc}  [{size}]"
                cb = tk.Checkbutton(
                    item_frame, text=text, variable=var,
                    font=("Microsoft YaHei UI", 9),
                    wraplength=300, justify=tk.LEFT
                )
                cb.pack(anchor=tk.W)

                item_key = f"{key}:{path}"
                self.check_vars[item_key] = {
                    "var": var,
                    "category": key,
                    "path": path,
                    "desc": desc,
                    "cat_var": cat_var,
                }

    def _toggle_category(self, category, checked):
        """切换分类下所有项的勾选状态"""
        for key, info in self.check_vars.items():
            if info["category"] == category:
                info["var"].set(checked)

    def _toggle_select_all(self):
        """全选/取消全选"""
        checked = self.select_all_var.get()
        for info in self.check_vars.items():
            info[1]["var"].set(checked)
            info[1]["cat_var"].set(checked)

    # ==================== 详情树 ====================

    def _clear_detail_tree(self):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

    def _fill_detail_tree(self):
        self._clear_detail_tree()
        for key, results in self.scan_results.items():
            for desc, path, size, exists in results:
                if not exists:
                    status = "❌ 无"
                elif path.startswith("uninstall:"):
                    status = "🔧 可卸载"
                elif path.startswith("regclean:"):
                    status = "📋 注册表"
                elif path.startswith("data:"):
                    status = "📂 数据"
                else:
                    status = "✅ 存在"
                # 显示路径时去掉前缀
                display_path = path
                for prefix in ("uninstall:", "data:", "regclean:"):
                    if display_path.startswith(prefix):
                        display_path = display_path[len(prefix):]
                        break
                if len(display_path) > 50:
                    display_path = "..." + display_path[-47:]
                self.detail_tree.insert("", tk.END, values=(desc, display_path, size, status))

    # ==================== 清理逻辑 ====================

    def _on_clean(self):
        """点击清理按钮"""
        selected = self._get_selected()
        if not selected:
            messagebox.showwarning("提示", "请先勾选需要清理的项目！")
            return

        count = sum(len(v) for v in selected.values())
        msg = f"即将处理 {count} 个项目，此操作不可撤销！\n\n"

        # 分类统计并特别标注卸载项
        uninstall_count = 0
        data_count = 0
        for cat, items in selected.items():
            name = self.cleaners[cat].DISPLAY_NAME
            if cat == "software":
                u = sum(1 for i in items if i.startswith("uninstall:"))
                d = len(items) - u
                uninstall_count += u
                data_count += d
                if u > 0:
                    msg += f"  [{name}] {u} 个软件将被卸载\n"
                if d > 0:
                    msg += f"  [{name}] {d} 项数据/残留将被清除\n"
            else:
                msg += f"  [{name}] {len(items)} 项\n"

        if uninstall_count > 0:
            msg += f"\n⚠️ 其中 {uninstall_count} 个软件将被卸载！\n"
            msg += "部分软件可能弹出卸载向导，请配合完成。\n"
        msg += "\n确定要继续吗？"

        if not messagebox.askyesno("确认清理", msg, icon="warning"):
            return

        # 二次确认
        confirm_msg = "⚠️ 数据删除后无法恢复"
        if uninstall_count > 0:
            confirm_msg += f"，且 {uninstall_count} 个软件将被卸载"
        confirm_msg += "，是否继续？"
        if not messagebox.askyesno("最终确认", confirm_msg, icon="warning"):
            return

        self.clean_btn.config(state=tk.DISABLED, text="清理中...")
        self.scan_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在清理...")
        self._log("=" * 40)
        self._log("开始清理操作...")

        thread = threading.Thread(target=self._do_clean, args=(selected,), daemon=True)
        thread.start()

    def _do_clean(self, selected):
        """在子线程中执行清理"""
        total_cleaned = 0
        for cat, paths in selected.items():
            cleaner = self.cleaners[cat]
            self.root.after(0, self._log, f"正在清理 [{cleaner.DISPLAY_NAME}]...")
            cleaned = cleaner.clean(paths, self.logger)
            total_cleaned += cleaned

        # 将 logger 记录同步到 UI
        for record in self.logger.get_records():
            self.root.after(0, self._log, record)
        self.logger.records.clear()

        self.root.after(0, self._clean_complete, total_cleaned)

    def _clean_complete(self, total):
        self.clean_btn.config(state=tk.NORMAL, text="🗑️ 一键清理")
        self.scan_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"清理完成 - 已处理 {total} 项")
        self._log(f"清理完成，共处理 {total} 项")
        self._log("=" * 40)
        messagebox.showinfo("完成", f"清理完成！共处理 {total} 项数据。\n\n建议重新扫描确认清理效果。")

    def _get_selected(self) -> dict:
        """获取已勾选的项目，按分类分组 {category: [path1, path2, ...]}"""
        selected = {}
        for key, info in self.check_vars.items():
            if info["var"].get():
                cat = info["category"]
                if cat not in selected:
                    selected[cat] = []
                selected[cat].append(info["path"])
        return selected

    # ==================== 日志 ====================

    def _log(self, msg: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ==================== 启动 ====================

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LeaveCleanApp()
    app.run()
