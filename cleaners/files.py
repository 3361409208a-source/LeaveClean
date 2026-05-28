"""个人文件清理 - 桌面/下载/文档/图片/视频/回收站/临时文件"""
import os
import shutil
import ctypes
import subprocess
from utils.scanner import check_path_exists, get_dir_size_fast, format_size, scan_directory


class FileCleaner:
    DISPLAY_NAME = "个人文件"

    def __init__(self):
        home = os.path.expanduser("~")
        self.dirs = {
            "桌面": os.path.join(home, "Desktop"),
            "下载": os.path.join(home, "Downloads"),
            "文档": os.path.join(home, "Documents"),
            "图片": os.path.join(home, "Pictures"),
            "视频": os.path.join(home, "Videos"),
            "音乐": os.path.join(home, "Music"),
        }
        self.temp_dir = os.environ.get("TEMP", os.path.join(home, "AppData", "Local", "Temp"))
        self.recent_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Recent")

    def scan(self) -> list:
        results = []
        
        # 1. 敏感文档关键字 (简历、offer、劳动合同、交接、工作总结、密码等)
        sensitive_keywords = ["简历", "resume", "job", "offer", "合同", "contract", "交接", "工作总结", "汇报", "报告", "password", "密码", "账号", "总结"]
        sensitive_files = []
        
        # 2. 大体积安装包与压缩包 (> 20MB)
        large_files = []
        
        for name, path in self.dirs.items():
            if not check_path_exists(path):
                results.append((name, path, "0 B", False))
                continue
            
            # 扫描目录下的一级和二级文件
            try:
                for entry in os.scandir(path):
                    if entry.is_file(follow_symlinks=False):
                        self._classify_file(entry.path, entry.name, name, sensitive_keywords, sensitive_files, large_files)
                    elif entry.is_dir(follow_symlinks=False):
                        # 扫描二级文件
                        try:
                            for sub_entry in os.scandir(entry.path):
                                if sub_entry.is_file(follow_symlinks=False):
                                    self._classify_file(sub_entry.path, sub_entry.name, f"{name}/{entry.name}", sensitive_keywords, sensitive_files, large_files)
                        except Exception:
                            pass
            except Exception:
                pass

            # 常规目录只列出作为手动核对项，默认不执行自动清空，防误杀
            size = format_size(get_dir_size_fast(path))
            items = scan_directory(path)
            results.append((f"[手动审核] 建议手动核对 {name} 目录 ({len(items)}项)", f"manual_review:{path}", size, True))

        # 将敏感文件和大文件添加到结果中
        results.extend(sensitive_files)
        results.extend(large_files)

        # 临时文件
        if check_path_exists(self.temp_dir):
            size = format_size(get_dir_size_fast(self.temp_dir))
            results.append(("临时文件 (%TEMP%)", self.temp_dir, size, True))

        # 最近文件记录
        if check_path_exists(self.recent_dir):
            size = format_size(get_dir_size_fast(self.recent_dir))
            results.append(("最近文件记录", self.recent_dir, size, True))

        # 回收站
        results.append(("回收站", "$RECYCLE", "需扫描", True))

        return results

    def _classify_file(self, fp, name, cat_name, sensitive_keywords, sensitive_files, large_files):
        fl = name.lower()
        # 检查敏感词
        if any(kw in fl for kw in sensitive_keywords):
            try:
                sz = format_size(os.path.getsize(fp))
            except OSError:
                sz = "未知"
            sensitive_files.append((f"[敏感文件] {cat_name} - ⚠ {name}", f"data:{fp}", sz, True))
            return
            
        # 检查大体积安装包/压缩包
        ext = os.path.splitext(fl)[1]
        if ext in (".exe", ".msi", ".zip", ".rar", ".7z", ".tar.gz", ".dmg"):
            try:
                fsize = os.path.getsize(fp)
                if fsize > 20 * 1024 * 1024:  # > 20MB
                    large_files.append((f"[大安装包/压缩包] {cat_name} - {name}", f"data:{fp}", format_size(fsize), True))
            except OSError:
                pass

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for path in paths:
            try:
                if path.startswith("manual_review:"):
                    real_path = path[14:]
                    logger.warning(f"【安全提醒】为防误杀，{os.path.basename(real_path)} 目录请手动备份与清理：{real_path}")
                    cleaned += 1
                elif path.startswith("data:"):
                    real_path = path[5:]
                    if os.path.isfile(real_path):
                        os.remove(real_path)
                        logger.success(f"已删除敏感文件: {real_path}")
                        cleaned += 1
                    elif os.path.isdir(real_path):
                        shutil.rmtree(real_path, ignore_errors=True)
                        logger.success(f"已删除目录: {real_path}")
                        cleaned += 1
                elif path == "$RECYCLE":
                    self._empty_recycle_bin(logger)
                    cleaned += 1
                elif path == self.temp_dir:
                    self._clean_temp(logger)
                    cleaned += 1
                elif path == self.recent_dir:
                    self._clean_recent(logger)
                    cleaned += 1
                elif os.path.isdir(path):
                    # 兼容可能存在的旧格式（如果没有前缀的目录）
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                        except (PermissionError, OSError):
                            pass
                    logger.success(f"已清理目录内容: {path}")
                    cleaned += 1
            except Exception as e:
                logger.error(f"清理失败 {path}: {e}")
        return cleaned

    def _empty_recycle_bin(self, logger):
        """清空回收站"""
        try:
            # SHEmptyRecycleBin flags: SHERB_NOCONFIRMATION=1 | SHERB_NOPROGRESSUI=2 | SHERB_NOSOUND=4
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
            logger.success("已清空回收站")
        except Exception as e:
            logger.error(f"清空回收站失败: {e}")

    def _clean_temp(self, logger):
        """清理临时文件"""
        count = 0
        for item in os.listdir(self.temp_dir):
            item_path = os.path.join(self.temp_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    count += 1
            except (PermissionError, OSError):
                pass
        logger.success(f"已清理 {count} 个临时文件/目录")

    def _clean_recent(self, logger):
        """清理最近文件记录"""
        count = 0
        for item in os.listdir(self.recent_dir):
            item_path = os.path.join(self.recent_dir, item)
            try:
                os.remove(item_path)
                count += 1
            except (PermissionError, OSError):
                pass
        logger.success(f"已清理 {count} 条最近文件记录")
