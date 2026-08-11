import logging
import os
import sys  # <-- Bổ sung import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name="AIAssistant", log_file="Logs/app.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Tránh ghi log trùng lặp
    if not logger.handlers:
        # Format chuẩn cho log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Ghi ra file (tối đa 5MB/file, giữ 3 file cũ)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)

        # In ra Console qua sys.stdout thay vì sys.stderr (mặc định)
        console_handler = logging.StreamHandler(sys.stdout)  # <-- Cập nhật ở đây
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger