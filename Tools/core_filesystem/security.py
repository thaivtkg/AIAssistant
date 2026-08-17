import os
from pathlib import Path

class FileSecurityManager:
    @staticmethod
    def is_safe_path(path: str) -> bool:
        """
        Kiểm tra đường dẫn có an toàn để thực thi hay không.
        - Chặn Path Traversal (..)
        - Chặn thao tác vào các thư mục hệ thống Windows
        """
        try:
            if not path:
                return False
                
            # 1. Chặn Path Traversal ngay từ chuỗi gốc
            if ".." in path:
                return False
                
            abs_path = os.path.abspath(path)
            path_obj = Path(abs_path).resolve()
            
            # 2. Chặn thao tác trực tiếp lên Root C:\ (Ví dụ: C:\)
            if str(path_obj) == "C:\\":
                return False

            # 3. Danh sách thư mục cấm (System / Core)
            forbidden_parents = [
                Path("C:/Windows").resolve(),
                Path("C:/Program Files").resolve(),
                Path("C:/Program Files (x86)").resolve(),
            ]
            
            # Kiểm tra xem path có nằm bên trong (hoặc trùng với) thư mục cấm không
            for forbidden_dir in forbidden_parents:
                if forbidden_dir in path_obj.parents or path_obj == forbidden_dir:
                    return False
                    
            return True
        except Exception:
            # Lỗi phân giải đường dẫn -> Chặn an toàn
            return False