"""
离职数据清理助手 v4.0
统一树形视图 — 勾选 + 详情 + 操作合为一体
"""

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cleaners.browser import BrowserCleaner
from cleaners.chat import ChatCleaner
from cleaners.files import FileCleaner
from cleaners.credentials import CredentialCleaner
from cleaners.software import SoftwareCleaner
from cleaners.aitools import AIToolsCleaner
from cleaners.devenv import DevEnvCleaner
from cleaners.selfclean import SelfCleaner
from cleaners.uninstall import UninstallCleaner
from utils.logger import CleanLogger


class LeaveCleanApp:
    TITLE = "离职数据清理助手 v4.0"
    WIDTH = 1150
    HEIGHT = 750

    CATEGORIES = {
        "uninstall": ("软件卸载", "#d32f2f"),
        "browser": ("浏览器数据", "#4285f4"),
        "chat": ("聊天与通讯", "#34a853"),
        "files": ("个人文件", "#ea4335"),
        "credentials": ("凭据与隐私", "#ff6d01"),
        "aitools": ("AI编程工具", "#00bcd4"),
        "devenv": ("开发环境", "#795548"),
        "software": ("个人软件管理", "#9c27b0"),
        "selfclean": ("本应用自身", "#e91e63"),
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.minsize(850, 550)
        self.root.configure(bg="#f0f0f0")

        self.cleaners = {
            k: cls()
            for k, cls in [
                ("uninstall", UninstallCleaner),
                ("browser", BrowserCleaner),
                ("chat", ChatCleaner),
                ("files", FileCleaner),
                ("credentials", CredentialCleaner),
                ("aitools", AIToolsCleaner),
                ("devenv", DevEnvCleaner),
                ("software", SoftwareCleaner),
                ("selfclean", SelfCleaner),
            ]
        }
        self.logger = CleanLogger()
        self.scan_results = {}
        self.scan_module_times = {}
        self.scan_start_time = 0
        self.scan_elapsed = 0
        self._timer_running = False

        # checked items: {tree_item_id: {"cat": str, "path": str, "desc": str}}
        self.checked = {}

        self._setup_styles()
        self._build_ui()

    # ================================================================
    #  样式
    # ================================================================

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(
            "green.Horizontal.TProgressbar", troughcolor="#e0e0e0", background="#34a853"
        )
        # 树行高
        s.configure("Main.Treeview", rowheight=24, font=("Microsoft YaHei UI", 9))
        s.configure("Main.Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"))

    # ================================================================
    #  UI
    # ================================================================

    def _build_ui(self):
        # ---- 1. 顶部 (固定) ----
        header = tk.Frame(self.root, bg="#1a73e8", height=40)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="  离职数据清理助手",
            font=("Microsoft YaHei UI", 13, "bold"),
            fg="white",
            bg="#1a73e8",
        ).pack(side=tk.LEFT, padx=8, pady=4)
        self.time_label = tk.Label(
            header, font=("Consolas", 10), fg="#cce0ff", bg="#1a73e8"
        )
        self.time_label.pack(side=tk.RIGHT, padx=12)
        self._update_clock()

        # ---- 2. 统计 + 进度 (固定) ----
        bar = tk.Frame(self.root, bg="#f0f0f0")
        bar.pack(fill=tk.X, side=tk.TOP, padx=6, pady=(3, 1))
        self.stat_cards = {}
        for key, desc, default, color in [
            ("total", "发现", "0", "#1a73e8"),
            ("size", "大小", "0 B", "#ea4335"),
            ("cleaned", "已清理", "0", "#34a853"),
            ("scan_time", "用时", "0.0s", "#ff6d01"),
            ("modules", "模块", "0/9", "#9c27b0"),
        ]:
            c = tk.Frame(bar, bg="white", relief=tk.RIDGE, bd=1, padx=8, pady=2)
            c.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            v = tk.Label(
                c,
                text=default,
                font=("Microsoft YaHei UI", 13, "bold"),
                fg=color,
                bg="white",
            )
            v.pack(side=tk.LEFT, padx=(0, 3))
            tk.Label(
                c, text=desc, font=("Microsoft YaHei UI", 8), fg="#888", bg="white"
            ).pack(side=tk.LEFT)
            self.stat_cards[key] = v

        pf = tk.Frame(self.root, bg="#f0f0f0")
        pf.pack(fill=tk.X, side=tk.TOP, padx=6, pady=(1, 2))
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(
            pf,
            variable=self.progress_var,
            maximum=100,
            style="green.Horizontal.TProgressbar",
        ).pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.progress_label = tk.Label(
            pf,
            text="就绪",
            font=("Microsoft YaHei UI", 8),
            fg="#666",
            bg="#f0f0f0",
            width=20,
            anchor=tk.W,
        )
        self.progress_label.pack(side=tk.RIGHT, padx=4)

        # ---- 3. 底部按钮 (固定, 先 pack!) ----
        bot = tk.Frame(self.root, bg="#e8e8e8", height=40)
        bot.pack(fill=tk.X, side=tk.BOTTOM)
        bot.pack_propagate(False)
        self.status_label = tk.Label(
            bot,
            text="就绪 - 请先扫描",
            font=("Microsoft YaHei UI", 9),
            fg="#555",
            bg="#e8e8e8",
        )
        self.status_label.pack(side=tk.LEFT, padx=8)
        bs = {
            "font": ("Microsoft YaHei UI", 10, "bold"),
            "width": 12,
            "cursor": "hand2",
            "relief": tk.RAISED,
            "bd": 2,
        }
        self.clean_btn = tk.Button(
            bot,
            text="一键清理",
            bg="#d93025",
            fg="white",
            activebackground="#b71c1c",
            activeforeground="white",
            command=self._on_clean,
            state=tk.DISABLED,
            **bs,
        )
        self.clean_btn.pack(side=tk.RIGHT, padx=6, pady=4)
        self.scan_btn = tk.Button(
            bot,
            text="扫描检测",
            bg="#1a73e8",
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            command=self._on_scan,
            **bs,
        )
        self.scan_btn.pack(side=tk.RIGHT, padx=3, pady=4)

        # ---- 4. 主内容 (expand) ----
        main = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=4, bg="#ccc")
        main.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=6, pady=2)

        # -- 上: 分类侧栏 + 按钮行 + 合并树 --
        upper = tk.Frame(main)
        main.add(upper, minsize=200)

        # 左侧分类导航
        nav_frame = tk.Frame(upper, width=140, bg="#f5f5f5")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 3))
        nav_frame.pack_propagate(False)

        tk.Label(
            nav_frame,
            text="分类",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#f5f5f5",
            fg="#333",
        ).pack(pady=(6, 4))

        self.nav_buttons = {}
        self.current_filter = "all"

        # "全部"按钮
        btn_all = tk.Button(
            nav_frame,
            text="  全部  ",
            anchor=tk.W,
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#1a73e8",
            fg="white",
            relief=tk.FLAT,
            activebackground="#1565c0",
            activeforeground="white",
            cursor="hand2",
            padx=8,
            pady=4,
            command=lambda: self._filter_tree("all"),
        )
        btn_all.pack(fill=tk.X, padx=4, pady=1)
        self.nav_buttons["all"] = btn_all

        for key, (name, color) in self.CATEGORIES.items():
            b = tk.Button(
                nav_frame,
                text=f"  {name}  ",
                anchor=tk.W,
                font=("Microsoft YaHei UI", 9),
                bg="#f5f5f5",
                fg="#333",
                relief=tk.FLAT,
                activebackground="#e0e0e0",
                cursor="hand2",
                padx=8,
                pady=4,
                command=lambda k=key: self._filter_tree(k),
            )
            b.pack(fill=tk.X, padx=4, pady=1)
            self.nav_buttons[key] = b

        # 分类项计数标签 (扫描后更新)
        self.nav_count_labels = {}
        # 暂不显示计数，扫描后通过 _update_nav_counts 更新

        # 右侧内容
        top_frame = tk.Frame(upper)
        top_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 按钮行
        tb = tk.Frame(top_frame)
        tb.pack(fill=tk.X, pady=(2, 3))

        self.select_all_var = tk.BooleanVar()
        tk.Checkbutton(
            tb,
            text="全选",
            variable=self.select_all_var,
            font=("Microsoft YaHei UI", 9, "bold"),
            command=self._toggle_select_all,
        ).pack(side=tk.LEFT, padx=4)

        dbs = {
            "font": ("Microsoft YaHei UI", 9, "bold"),
            "relief": tk.RAISED,
            "bd": 2,
            "padx": 8,
            "pady": 2,
            "cursor": "hand2",
        }
        self.btn_clean_sel = tk.Button(
            tb,
            text=" 清除选中 ",
            bg="#d93025",
            fg="white",
            activebackground="#b71c1c",
            activeforeground="white",
            command=self._on_single_clean,
            state=tk.DISABLED,
            **dbs,
        )
        self.btn_clean_sel.pack(side=tk.LEFT, padx=3)
        self.btn_uninstall = tk.Button(
            tb,
            text=" 卸载软件 ",
            bg="#e65100",
            fg="white",
            activebackground="#bf360c",
            activeforeground="white",
            command=self._on_single_uninstall,
            state=tk.DISABLED,
            **dbs,
        )
        self.btn_uninstall.pack(side=tk.LEFT, padx=3)
        self.btn_open = tk.Button(
            tb,
            text=" 打开目录 ",
            bg="#1565c0",
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            command=self._on_open_path,
            state=tk.DISABLED,
            **dbs,
        )
        self.btn_open.pack(side=tk.LEFT, padx=3)
        self.count_label = tk.Label(
            tb, text="共 0 项", font=("Microsoft YaHei UI", 9, "bold"), fg="#333"
        )
        self.count_label.pack(side=tk.RIGHT, padx=8)

        # 合并树: ☑ | 项目 | 路径 | 大小 | 状态 | 类型
        cols = ("chk", "item", "path", "size", "status", "optype")
        self.tree = ttk.Treeview(
            top_frame,
            columns=cols,
            show="tree headings",
            style="Main.Treeview",
            selectmode="browse",
        )
        self.tree.heading("#0", text="")
        self.tree.heading("chk", text="✓")
        self.tree.heading("item", text="项目")
        self.tree.heading("path", text="路径")
        self.tree.heading("size", text="大小")
        self.tree.heading("status", text="状态")
        self.tree.heading("optype", text="类型")
        self.tree.column("#0", width=30, stretch=False)
        self.tree.column("chk", width=30, anchor=tk.CENTER, stretch=False)
        self.tree.column("item", width=260, minwidth=150)
        self.tree.column("path", width=300, minwidth=100)
        self.tree.column("size", width=75, anchor=tk.CENTER)
        self.tree.column("status", width=60, anchor=tk.CENTER)
        self.tree.column("optype", width=70, anchor=tk.CENTER)

        # 颜色标签
        self.tree.tag_configure(
            "cat", background="#e8eaf6", font=("Microsoft YaHei UI", 10, "bold")
        )
        self.tree.tag_configure("warn", foreground="#d93025")
        self.tree.tag_configure("checked", background="#e8f5e9")
        self.tree.tag_configure("normal", background="white")

        ts = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ts.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ts.pack(side=tk.RIGHT, fill=tk.Y)

        # 事件
        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self._on_open_path())

        # 右键
        self.ctx = tk.Menu(self.root, tearoff=0, font=("Microsoft YaHei UI", 9))
        self.ctx.add_command(label="查看数据详情", command=self._ctx_preview)
        self.ctx.add_command(label="打开所在目录", command=self._on_open_path)
        self.ctx.add_command(label="复制路径", command=self._on_copy_path)
        self.ctx.add_separator()
        self.ctx.add_command(label="清除此项", command=self._on_single_clean)
        self.ctx.add_command(label="卸载此软件", command=self._on_single_uninstall)
        self.tree.bind("<Button-3>", self._on_right_click)

        # -- 下: 预览 + 日志 --
        bot_pane = tk.PanedWindow(main, orient=tk.HORIZONTAL, sashwidth=4, bg="#ccc")
        main.add(bot_pane, minsize=100)

        # 预览
        pv = tk.LabelFrame(
            bot_pane,
            text=" 数据详情 (点击行查看) ",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=4,
            pady=2,
        )
        bot_pane.add(pv, minsize=250)
        self.preview = scrolledtext.ScrolledText(
            pv,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#fafafa",
            fg="#333",
        )
        self.preview.pack(fill=tk.BOTH, expand=True)
        for tag, cfg in [
            (
                "title",
                {"font": ("Microsoft YaHei UI", 10, "bold"), "foreground": "#1a73e8"},
            ),
            ("key", {"font": ("Consolas", 9, "bold"), "foreground": "#795548"}),
            ("warn", {"foreground": "#d93025", "font": ("Consolas", 9, "bold")}),
            ("path", {"foreground": "#666"}),
        ]:
            self.preview.tag_config(tag, **cfg)

        # 日志
        lg = tk.LabelFrame(
            bot_pane,
            text=" 操作日志 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=4,
            pady=2,
        )
        bot_pane.add(lg, minsize=250)
        ltb = tk.Frame(lg)
        ltb.pack(fill=tk.X, pady=(0, 2))
        tk.Button(
            ltb, text="清空", font=("Microsoft YaHei UI", 8), command=self._clear_log
        ).pack(side=tk.RIGHT)
        tk.Button(
            ltb, text="导出", font=("Microsoft YaHei UI", 8), command=self._export_log
        ).pack(side=tk.RIGHT, padx=2)
        self.log_text = scrolledtext.ScrolledText(
            lg,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#1e1e1e",
            fg="#00ff00",
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        for tag, fg in [
            ("error", "#ff4444"),
            ("success", "#00ff00"),
            ("warning", "#ffaa00"),
            ("info", "#88ccff"),
            ("time", "#888"),
        ]:
            self.log_text.tag_config(tag, foreground=fg)

    # ================================================================
    #  时钟 / 计时器
    # ================================================================

    def _update_clock(self):
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def _start_timer(self):
        self.scan_start_time = time.time()
        self._timer_running = True
        self._tick()

    def _tick(self):
        if not self._timer_running:
            return
        e = time.time() - self.scan_start_time
        self.stat_cards["scan_time"].config(text=f"{e:.1f}s")
        self.root.after(100, self._tick)

    def _stop_timer(self):
        self._timer_running = False
        self.scan_elapsed = time.time() - self.scan_start_time
        self.stat_cards["scan_time"].config(text=f"{self.scan_elapsed:.1f}s")

    # ================================================================
    #  扫描
    # ================================================================

    def _on_scan(self):
        self.scan_btn.config(state=tk.DISABLED, text="扫描中...")
        self.clean_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.config(text="正在扫描...")
        self.status_label.config(text="正在扫描...")
        for k in ("total", "size"):
            self.stat_cards[k].config(text="...")
        self.stat_cards["cleaned"].config(text="0")
        self.stat_cards["modules"].config(text=f"0/{len(self.cleaners)}")
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.checked.clear()
        self._log("=" * 50, "info")
        self._log(f"开始扫描 [{datetime.now().strftime('%H:%M:%S')}]", "info")
        self._start_timer()
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        self.scan_results.clear()
        self.scan_module_times.clear()
        total_found = 0
        done = 0

        def timed(key, cl):
            t = time.time()
            r = cl.scan()
            return key, r, time.time() - t

        futs = {}
        with ThreadPoolExecutor(max_workers=5) as pool:
            for k, cl in self.cleaners.items():
                futs[pool.submit(timed, k, cl)] = k
            for f in as_completed(futs):
                k = futs[f]
                cl = self.cleaners[k]
                try:
                    _, res, el = f.result()
                    found = [r for r in res if r[3]]
                    self.scan_results[k] = res
                    self.scan_module_times[k] = el
                    total_found += len(found)
                    done += 1
                    pct = done / len(self.cleaners) * 100
                    self.root.after(
                        0,
                        self._scan_progress,
                        done,
                        total_found,
                        pct,
                        cl.DISPLAY_NAME,
                        len(found),
                        el,
                    )
                except Exception as e:
                    done += 1
                    self.root.after(
                        0, self._log, f"[错误] {cl.DISPLAY_NAME}: {e}", "error"
                    )
        self.root.after(0, self._scan_done, total_found)

    def _scan_progress(self, done, found, pct, name, n, el):
        self.progress_var.set(pct)
        self.progress_label.config(text=f"{done}/{len(self.cleaners)} 模块")
        self.stat_cards["total"].config(text=str(found))
        self.stat_cards["modules"].config(text=f"{done}/{len(self.cleaners)}")
        self._log(f"  [{name}] {n} 项 ({el:.2f}s)", "info")

    def _scan_done(self, total):
        self._stop_timer()
        self.current_filter = "all"
        self._fill_tree("all")
        self._update_nav_counts()
        # 重置导航高亮
        for k, btn in self.nav_buttons.items():
            if k == "all":
                btn.config(
                    bg="#1a73e8", fg="white", font=("Microsoft YaHei UI", 9, "bold")
                )
            else:
                btn.config(bg="#f5f5f5", fg="#333", font=("Microsoft YaHei UI", 9))
        self.stat_cards["total"].config(text=str(total))
        self.stat_cards["size"].config(text=self._calc_total_size())
        self.scan_btn.config(state=tk.NORMAL, text="重新扫描")
        self.clean_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.progress_label.config(text="扫描完成")
        self.status_label.config(
            text=f"扫描完成 - {total} 项 - {self.scan_elapsed:.1f}s"
        )
        self._log(f"扫描完成！{total} 项，用时 {self.scan_elapsed:.1f}s", "success")
        for k, t in sorted(self.scan_module_times.items(), key=lambda x: -x[1]):
            self._log(f"  {self.cleaners[k].DISPLAY_NAME}: {t:.2f}s", "time")
        self._log("=" * 50, "info")

    def _calc_total_size(self):
        from utils.scanner import format_size

        total = 0
        sm = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        for res in self.scan_results.values():
            for _, _, sz, ex in res:
                if not ex:
                    continue
                try:
                    p = sz.split()
                    if len(p) == 2 and p[1] in sm:
                        total += float(p[0]) * sm[p[1]]
                except (ValueError, IndexError):
                    pass
        return format_size(int(total))

    # ================================================================
    #  填充合并树
    # ================================================================

    def _fill_tree(self, filter_cat="all"):
        """填充树，filter_cat='all'显示全部，否则只显示对应分类"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        # 注意: 不清空 self.checked，保留已勾选状态
        count = 0

        for key in self.cleaners:
            if filter_cat != "all" and key != filter_cat:
                continue
            results = self.scan_results.get(key, [])
            found = [r for r in results if r[3]]
            if not found:
                continue

            cat_name, _ = self.CATEGORIES.get(key, (key, "#333"))
            st = self.scan_module_times.get(key, 0)

            cat_id = self.tree.insert(
                "",
                tk.END,
                text="",
                values=("☐", f"{cat_name} ({len(found)}项, {st:.1f}s)", "", "", "", ""),
                open=True,
                tags=("cat", f"cat:{key}"),
            )

            for desc, path, size, exists in found:
                if path.startswith("uninstall:"):
                    status, optype = "可卸载", "卸载"
                elif path.startswith("regclean:"):
                    status, optype = "残留", "注册表"
                elif path.startswith("selfdestruct:"):
                    status, optype = "可卸载", "自卸载"
                elif path.startswith("data:"):
                    status, optype = "存在", "清除"
                else:
                    status, optype = "存在", "清除"

                dp = path
                for pf in ("selfdestruct:", "uninstall:", "data:", "regclean:"):
                    if dp.startswith(pf):
                        dp = dp[len(pf) :]
                        break
                if len(dp) > 60:
                    dp = "..." + dp[-57:]

                # 检查之前是否勾选 (用稳定 key)
                item_tag = f"item:{key}:{path}"
                stable_key = f"{key}:{path}"
                is_checked = stable_key in self.checked
                chk = "☑" if is_checked else "☐"
                vis_tag = (
                    "checked"
                    if is_checked
                    else ("warn" if ("⚠" in desc or "★" in desc) else "normal")
                )

                self.tree.insert(
                    cat_id,
                    tk.END,
                    text="",
                    values=(chk, desc, dp, size, status, optype),
                    tags=(vis_tag, item_tag),
                )
                count += 1

        # 更新分类父节点的勾选状态
        for cat_row in self.tree.get_children():
            children = self.tree.get_children(cat_row)
            if children and all(
                self.tree.item(c, "values")[0] == "☑" for c in children
            ):
                vals = list(self.tree.item(cat_row, "values"))
                vals[0] = "☑"
                self.tree.item(cat_row, values=vals)

        self.count_label.config(text=f"共 {count} 项")

    def _filter_tree(self, cat_key):
        """点击左侧分类导航，过滤树视图"""
        self.current_filter = cat_key
        # 更新导航按钮高亮
        for k, btn in self.nav_buttons.items():
            if k == cat_key:
                btn.config(
                    bg="#1a73e8", fg="white", font=("Microsoft YaHei UI", 9, "bold")
                )
            else:
                btn.config(bg="#f5f5f5", fg="#333", font=("Microsoft YaHei UI", 9))
        # 重新填充树（保留勾选）
        if self.scan_results:
            self._fill_tree(filter_cat=cat_key)

    def _update_nav_counts(self):
        """扫描后更新分类导航按钮上的计数"""
        for key, btn in self.nav_buttons.items():
            if key == "all":
                total = sum(
                    len([r for r in res if r[3]]) for res in self.scan_results.values()
                )
                name = f"  全部 ({total})"
            else:
                res = self.scan_results.get(key, [])
                n = len([r for r in res if r[3]])
                cat_name, _ = self.CATEGORIES.get(key, (key, "#333"))
                name = f"  {cat_name} ({n})" if n > 0 else f"  {cat_name}"
            btn.config(text=name)

        self.count_label.config(text=f"共 {total} 项")

    # ================================================================
    #  勾选逻辑
    # ================================================================

    def _on_tree_click(self, event):
        """点击 ☐/☑ 列切换勾选"""
        region = self.tree.identify_region(event.x, event.y)
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row:
            return
        # col #1 = "chk"
        if col == "#1" or (region == "cell" and col == "#1"):
            pass  # 继续处理
        elif col != "#1":
            return  # 不是点击勾选列

        tags = self.tree.item(row, "tags")
        tag_str = tags[1] if len(tags) > 1 else ""

        if tag_str.startswith("cat:"):
            # 分类节点 —— 切换所有子项
            self._toggle_cat_node(row)
        elif tag_str.startswith("item:"):
            self._toggle_item_node(row)

    def _toggle_cat_node(self, cat_row):
        vals = list(self.tree.item(cat_row, "values"))
        new_chk = "☐" if vals[0] == "☑" else "☑"
        vals[0] = new_chk
        self.tree.item(cat_row, values=vals)
        for child in self.tree.get_children(cat_row):
            self._set_item_checked(child, new_chk == "☑")

    def _toggle_item_node(self, row):
        vals = list(self.tree.item(row, "values"))
        is_checked = vals[0] == "☑"
        self._set_item_checked(row, not is_checked)

    def _set_item_checked(self, row, checked):
        vals = list(self.tree.item(row, "values"))
        vals[0] = "☑" if checked else "☐"
        self.tree.item(row, values=vals)

        tags = self.tree.item(row, "tags")
        tag_str = tags[1] if len(tags) > 1 else ""
        if not tag_str.startswith("item:"):
            return

        # "item:cat:path"
        parts = tag_str.split(":", 2)
        cat, path = parts[1], parts[2]
        stable_key = f"{cat}:{path}"  # 用 cat:path 作为稳定 key

        if checked:
            self.checked[stable_key] = {"cat": cat, "path": path, "desc": vals[1]}
            self.tree.item(row, tags=("checked", tag_str))
        else:
            self.checked.pop(stable_key, None)
            is_warn = "⚠" in vals[1] or "★" in vals[1]
            self.tree.item(row, tags=("warn" if is_warn else "normal", tag_str))

    def _toggle_select_all(self):
        checked = self.select_all_var.get()
        for cat_row in self.tree.get_children():
            vals = list(self.tree.item(cat_row, "values"))
            vals[0] = "☑" if checked else "☐"
            self.tree.item(cat_row, values=vals)
            for child in self.tree.get_children(cat_row):
                self._set_item_checked(child, checked)

    # ================================================================
    #  树选中 → 预览 + 按钮状态
    # ================================================================

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.btn_clean_sel.config(state=tk.DISABLED)
            self.btn_uninstall.config(state=tk.DISABLED)
            self.btn_open.config(state=tk.DISABLED)
            return
        tags = self.tree.item(sel[0], "tags")
        tag = tags[1] if len(tags) > 1 else ""
        is_item = tag.startswith("item:")
        self.btn_clean_sel.config(state=tk.NORMAL if is_item else tk.DISABLED)
        self.btn_open.config(state=tk.NORMAL if is_item else tk.DISABLED)
        if is_item:
            parts = tag.split(":", 2)
            path = parts[2]
            self.btn_uninstall.config(
                state=tk.NORMAL if path.startswith("uninstall:") else tk.DISABLED
            )
            vals = self.tree.item(sel[0], "values")
            self._show_preview(parts[1], path, vals)
        else:
            self.btn_uninstall.config(state=tk.DISABLED)

    def _ctx_preview(self):
        sel = self.tree.selection()
        if sel:
            self._on_tree_select(None)

    def _on_right_click(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            self.ctx.tk_popup(event.x_root, event.y_root)

    # ================================================================
    #  预览
    # ================================================================

    def _show_preview(self, cat, raw_path, values):
        self.preview.config(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)
        desc = values[1] if len(values) > 1 else ""
        size = values[3] if len(values) > 3 else ""
        real = raw_path
        ptype = "数据"
        for pf, pt in [
            ("uninstall:", "卸载命令"),
            ("data:", "数据目录"),
            ("regclean:", "注册表"),
        ]:
            if real.startswith(pf):
                real, ptype = real[len(pf) :], pt
                break
        self.preview.insert(tk.END, f"{desc}\n", "title")
        self.preview.insert(tk.END, "路径: ", "key")
        self.preview.insert(tk.END, f"{real}\n", "path")
        self.preview.insert(tk.END, "类型: ", "key")
        self.preview.insert(tk.END, f"{ptype}  |  大小: {size}\n", "path")
        if ptype == "卸载命令":
            self.preview.insert(tk.END, "卸载命令: ", "key")
            self.preview.insert(tk.END, f"{real}\n", "warn")
        elif ptype == "注册表":
            self.preview.insert(tk.END, "操作: 删除此注册表项\n", "warn")
        elif os.path.isfile(real):
            self._pv_file(real)
        elif os.path.isdir(real):
            self._pv_dir(real)
        self.preview.config(state=tk.DISABLED)

    def _pv_file(self, p):
        try:
            from utils.scanner import format_size

            self.preview.insert(
                tk.END, f"文件大小: {format_size(os.path.getsize(p))}\n", "path"
            )
            ext = os.path.splitext(p)[1].lower()
            if ext in (
                ".json",
                ".txt",
                ".log",
                ".ini",
                ".cfg",
                ".conf",
                ".xml",
                ".yaml",
                ".yml",
                ".toml",
                ".gitconfig",
                ".npmrc",
                ".condarc",
                ".zshrc",
                "",
                ".history",
            ):
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()[:10]
                self.preview.insert(tk.END, "内容预览:\n", "key")
                for ln in lines:
                    d = ln.rstrip()
                    for kw in [
                        "password",
                        "token",
                        "secret",
                        "key",
                        "credential",
                        "api_key",
                        "private",
                    ]:
                        if kw in d.lower() and ("=" in d or ":" in d):
                            sep = "=" if "=" in d else ":"
                            parts = d.split(sep, 1)
                            if len(parts[1].strip()) > 3:
                                d = parts[0] + sep + " ********"
                            break
                    self.preview.insert(tk.END, f"  {d}\n", "path")
                if len(lines) >= 10:
                    self.preview.insert(tk.END, "  ...\n", "path")
            elif ext in (".sqlite", ".db", ".ldb"):
                self.preview.insert(tk.END, "数据库文件\n", "path")
            elif ext in (".pub", ".pem"):
                self.preview.insert(tk.END, "⚠ 密钥文件!\n", "warn")
        except Exception:
            pass

    def _pv_dir(self, p):
        try:
            from utils.scanner import format_size

            ents = []
            for e in os.scandir(p):
                try:
                    if e.is_dir(follow_symlinks=False):
                        ents.append(("D", e.name, ""))
                    else:
                        ents.append(
                            (
                                "F",
                                e.name,
                                format_size(e.stat(follow_symlinks=False).st_size),
                            )
                        )
                except (OSError, PermissionError):
                    pass
            if not ents:
                self.preview.insert(tk.END, "(空目录)\n", "path")
                return
            self.preview.insert(tk.END, f"包含 {len(ents)} 项:\n", "key")
            ents.sort(key=lambda x: (x[0] != "D", x[1].lower()))
            sens = [
                "credential",
                "token",
                "secret",
                "key",
                "password",
                "login",
                "cookie",
                "auth",
                ".pem",
                ".pub",
                "id_rsa",
                "id_ed25519",
                "known_hosts",
                "session",
            ]
            for tp, nm, sz in ents[:20]:
                icon = "📁" if tp == "D" else "📄"
                line = f"  {icon} {nm}"
                if sz:
                    line += f"  ({sz})"
                tag = "warn" if any(k in nm.lower() for k in sens) else "path"
                self.preview.insert(tk.END, line + "\n", tag)
            if len(ents) > 20:
                self.preview.insert(tk.END, f"  ... 还有 {len(ents) - 20} 项\n", "path")
        except (OSError, PermissionError):
            self.preview.insert(tk.END, "(无法读取)\n", "path")

    # ================================================================
    #  单项操作
    # ================================================================

    def _get_sel_item(self):
        sel = self.tree.selection()
        if not sel:
            return None
        tags = self.tree.item(sel[0], "tags")
        tag = tags[1] if len(tags) > 1 else ""
        if not tag.startswith("item:"):
            return None
        parts = tag.split(":", 2)
        vals = self.tree.item(sel[0], "values")
        return parts[1], parts[2], vals[1]

    def _on_single_clean(self):
        it = self._get_sel_item()
        if not it:
            messagebox.showwarning("提示", "请先选择一项")
            return
        cat, path, desc = it
        act = "卸载" if path.startswith("uninstall:") else "清除"
        self._do_single(cat, path, desc, act)

    def _on_single_uninstall(self):
        it = self._get_sel_item()
        if not it:
            return
        cat, path, desc = it
        if path.startswith("uninstall:"):
            self._do_single(cat, path, desc, "卸载")

    def _on_open_path(self):
        it = self._get_sel_item()
        if not it:
            return
        p = it[1]
        for pf in ("uninstall:", "data:", "regclean:"):
            if p.startswith(pf):
                p = p[len(pf) :]
                break
        if os.path.isfile(p):
            p = os.path.dirname(p)
        if os.path.isdir(p):
            os.startfile(p)
        else:
            messagebox.showinfo("提示", f"路径不存在:\n{p}")

    def _on_copy_path(self):
        it = self._get_sel_item()
        if not it:
            return
        p = it[1]
        for pf in ("uninstall:", "data:", "regclean:"):
            if p.startswith(pf):
                p = p[len(pf) :]
                break
        self.root.clipboard_clear()
        self.root.clipboard_append(p)
        self.status_label.config(text=f"已复制: {p}")

    def _do_single(self, cat, path, desc, action):
        if not messagebox.askyesno(
            "确认", f"确定{action}: {desc}?\n\n不可撤销！", icon="warning"
        ):
            return
        self._log(f"正在{action}: {desc}...", "warning")

        def go():
            t0 = time.time()
            cl = self.cleaners[cat]
            n = cl.clean([path], self.logger)
            el = time.time() - t0
            for r in self.logger.get_records():
                tg = "success" if "成功" in r else ("error" if "错误" in r else "info")
                self.root.after(0, self._log, r, tg)
            self.logger.records.clear()
            tag = "success" if n > 0 else "error"
            self.root.after(
                0,
                self._log,
                f"{action}{'完成' if n else '失败'}: {desc} ({el:.2f}s)",
                tag,
            )
            if n > 0:
                self.root.after(0, self._inc_cleaned, 1)
            self.root.after(
                0, self.status_label.config, {"text": f"{action}完成 ({el:.2f}s)"}
            )
            if getattr(cl, "self_destruct_triggered", False):
                self.root.after(500, self._trigger_self_destruct)

        threading.Thread(target=go, daemon=True).start()

    def _inc_cleaned(self, n):
        try:
            v = int(self.stat_cards["cleaned"].cget("text")) + n
        except ValueError:
            v = n
        self.stat_cards["cleaned"].config(text=str(v))

    # ================================================================
    #  一键清理 (勾选项)
    # ================================================================

    def _on_clean(self):
        if not self.checked:
            messagebox.showwarning(
                "提示", "请先勾选(☑)需要清理的项目！\n点击每行左侧 ☐ 进行勾选"
            )
            return

        # 按分类统计
        by_cat = {}
        for info in self.checked.values():
            by_cat.setdefault(info["cat"], []).append(info["path"])

        count = len(self.checked)
        msg = f"即将处理 {count} 个勾选项:\n\n"
        ui = 0
        for cat, paths in by_cat.items():
            name = self.cleaners[cat].DISPLAY_NAME
            u = sum(1 for p in paths if p.startswith("uninstall:"))
            ui += u
            d = len(paths) - u
            if u:
                msg += f"  [{name}] 卸载 {u} 个\n"
            if d:
                msg += f"  [{name}] 清除 {d} 项\n"

        if ui:
            msg += f"\n⚠ {ui} 个软件将被卸载!\n"
        msg += "\n确定继续？"

        if not messagebox.askyesno("确认清理", msg, icon="warning"):
            return
        if not messagebox.askyesno(
            "最终确认", "数据删除后无法恢复，是否继续？", icon="warning"
        ):
            return

        self.clean_btn.config(state=tk.DISABLED, text="清理中...")
        self.scan_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self._log("=" * 50, "info")
        self._log(f"批量清理 [{datetime.now().strftime('%H:%M:%S')}]", "warning")
        threading.Thread(
            target=self._do_batch_clean, args=(by_cat,), daemon=True
        ).start()

    def _do_batch_clean(self, by_cat):
        total = sum(len(v) for v in by_cat.values())
        done = cleaned = 0
        for cat, paths in by_cat.items():
            cl = self.cleaners[cat]
            self.root.after(
                0, self._log, f"[{cl.DISPLAY_NAME}] {len(paths)} 项...", "warning"
            )
            t0 = time.time()
            for p in paths:
                n = cl.clean([p], self.logger)
                cleaned += n
                done += 1
                for r in self.logger.get_records():
                    tg = (
                        "success"
                        if "成功" in r
                        else ("error" if "错误" in r else "info")
                    )
                    self.root.after(0, self._log, r, tg)
                self.logger.records.clear()
                pct = done / total * 100
                self.root.after(0, self._batch_progress, pct, done, total, cleaned)
            self.root.after(
                0,
                self._log,
                f"[{cl.DISPLAY_NAME}] 完成 ({time.time() - t0:.2f}s)",
                "success",
            )
            if getattr(cl, "self_destruct_triggered", False):
                self.root.after(0, self._trigger_self_destruct)
                return
        self.root.after(0, self._batch_done, cleaned, total)

    def _batch_progress(self, pct, done, total, cleaned):
        self.progress_var.set(pct)
        self.progress_label.config(text=f"{done}/{total}")
        self.stat_cards["cleaned"].config(text=str(cleaned))

    def _batch_done(self, cleaned, total):
        self.clean_btn.config(state=tk.NORMAL, text="一键清理")
        self.scan_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.progress_label.config(text="清理完成")
        self.status_label.config(text=f"清理完成 - {cleaned}/{total}")
        self._log(f"批量清理完成 {cleaned}/{total}", "success")
        self._log("=" * 50, "info")
        messagebox.showinfo(
            "完成", f"清理完成！\n成功: {cleaned}/{total}\n\n建议重新扫描确认"
        )

    def _trigger_self_destruct(self):
        import subprocess
        import tempfile

        app_dir = os.path.dirname(os.path.abspath(__file__))
        batch_path = os.path.join(tempfile.gettempdir(), "leaveclean_selfdestruct.bat")
        subprocess.Popen(
            ["cmd.exe", "/c", batch_path],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            close_fds=True,
        )
        self.root.after(1000, self.root.destroy)

    # ================================================================
    #  日志
    # ================================================================

    def _log(self, msg, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] ", "time")
        self.log_text.insert(tk.END, msg + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _export_log(self):
        from tkinter import filedialog

        p = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            initialfile=f"clean_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", tk.END))
            self._log(f"日志已导出: {p}", "success")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    LeaveCleanApp().run()
