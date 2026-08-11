import os
from pathlib import Path
from typing import List


class FileSecurityManager:
    """Lớp bảo mật chuyên trách kiểm duyệt đường dẫn trước khi AI thao tác."""

    # Danh sách các thư mục tuyệt đối không được chạm vào
    FORBIDDEN_PATHS: List[str] = [
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
        "C:\\$Recycle.Bin"
    ]

    @staticmethod
    def is_safe_path(target_path: str) -> bool:
        """
        Kiểm tra đường dẫn có an toàn không.
        1. Chống Path Traversal (tự động phân giải ..\..)
        2. Chống truy cập thư mục cấm.
        """
        try:
            # Phân giải thành đường dẫn tuyệt đối, loại bỏ các ký tự ../
            resolved_path = Path(target_path).resolve()
            path_str = str(resolved_path).lower()

            # Kiểm tra xem có nằm trong danh sách cấm không
            for forbidden in FileSecurityManager.FORBIDDEN_PATHS:
                if path_str.startswith(forbidden.lower()):
                    return False

            return True
        except Exception:
            # Nếu có lỗi phân giải đường dẫn (path không hợp lệ), chặn luôn
            return False