"""文件扫描与大小统计工具"""
import os
from pathlib import Path
from typing import List, Tuple, Dict


def format_size(size_bytes: int) -> str:
    """将字节数转换为人类可读的大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_dir_size(path: str) -> int:
    """计算目录总大小"""
    total = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total


def scan_directory(path: str, extensions: List[str] = None) -> List[Tuple[str, int]]:
    """扫描目录下的文件，返回 [(文件路径, 大小)] 列表"""
    results = []
    if not os.path.exists(path):
        return results
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file():
                    if extensions is None or Path(entry.path).suffix.lower() in extensions:
                        results.append((entry.path, entry.stat().st_size))
                elif entry.is_dir():
                    size = get_dir_size(entry.path)
                    results.append((entry.path, size))
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
