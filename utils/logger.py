"""操作日志记录"""
import os
import logging
from datetime import datetime


class CleanLogger:
    """清理操作日志记录器"""

    def __init__(self):
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        self.logger = logging.getLogger("LeaveClean")
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self.logger.addHandler(fh)

        self.records = []

    def info(self, msg: str):
        self.logger.info(msg)
        self.records.append(f"[信息] {msg}")

    def success(self, msg: str):
        self.logger.info(f"[成功] {msg}")
        self.records.append(f"[成功] {msg}")

    def error(self, msg: str):
        self.logger.error(msg)
        self.records.append(f"[错误] {msg}")

    def warning(self, msg: str):
        self.logger.warning(msg)
        self.records.append(f"[警告] {msg}")

    def get_records(self) -> list:
        return self.records
