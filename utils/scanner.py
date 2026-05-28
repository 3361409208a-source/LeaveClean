"""文件扫描与大小统计工具（性能优化版）"""
import os
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 全局线程池，复用线程
_executor = ThreadPoolExecutor(max_workers=8)


def format_size(size_bytes: int) -> str:
    """将字节数转换为人类可读的大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_dir_size(path: str, max_depth: int = 10, timeout_files: int = 5000) -> int:
    """计算目录总大小，带深度限制和文件数上限防止卡死"""
    total = 0
    file_count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            # 深度限制
            depth = dirpath.replace(path, '').count(os.sep)
            if depth >= max_depth:
                dirnames.clear()
                continue
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except (OSError, PermissionError):
                    pass
                file_count += 1
                if file_count >= timeout_files:
                    # 超过上限，基于采样估算
                    return _estimate_size(path, total, file_count)
    except (OSError, PermissionError):
        pass
    return total


def get_dir_size_fast(path: str) -> int:
    """快速估算目录大小 - 只扫描第一层"""
    total = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    # 子目录只做浅层估算
                    total += _shallow_size(entry.path, max_files=200)
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass
    return total


def _shallow_size(path: str, max_files: int = 200) -> int:
    """浅层大小统计，最多计算 max_files 个文件"""
    total = 0
    count = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
                    count += 1
                    if count >= max_files:
                        break
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass
    return total


def _estimate_size(path: str, sampled_total: int, sampled_count: int) -> int:
    """基于采样结果估算总大小"""
    try:
        total_files = count_files_fast(path)
        if sampled_count > 0 and total_files > sampled_count:
            avg = sampled_total / sampled_count
            return int(avg * total_files)
    except Exception:
        pass
    return sampled_total


def scan_directory(path: str, extensions: List[str] = None) -> List[Tuple[str, int]]:
    """扫描目录下的第一层文件/文件夹"""
    results = []
    if not os.path.exists(path):
        return results
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    if extensions is None or Path(entry.path).suffix.lower() in extensions:
                        results.append((entry.path, entry.stat(follow_symlinks=False).st_size))
                elif entry.is_dir(follow_symlinks=False):
                    results.append((entry.path, 0))  # 大小延迟计算
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass
    return results


def check_path_exists(path: str) -> bool:
    """检查路径是否存在"""
    return os.path.exists(path)


def count_files(path: str) -> int:
    """统计目录下文件数量"""
    count = 0
    try:
        for _, _, files in os.walk(path):
            count += len(files)
    except (OSError, PermissionError):
        pass
    return count


def count_files_fast(path: str, max_walk: int = 50) -> int:
    """快速统计文件数（限制遍历目录数）"""
    count = 0
    dirs_walked = 0
    try:
        for _, _, files in os.walk(path):
            count += len(files)
            dirs_walked += 1
            if dirs_walked >= max_walk:
                break
    except (OSError, PermissionError):
        pass
    return count


def parallel_scan(tasks: list) -> dict:
    """并行执行多个扫描任务
    tasks: [(key, callable), ...]
    返回: {key: result}
    """
    results = {}
    futures = {}
    for key, func in tasks:
        futures[_executor.submit(func)] = key
    for future in as_completed(futures):
        key = futures[future]
        try:
            results[key] = future.result()
        except Exception:
            results[key] = []
    return results
