import os
from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_filesystem.security import FileSecurityManager


class ListDirectoryTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_directory",
            description="Xem danh sách các file và thư mục con bên trong một thư mục cụ thể.",
            requires_permission=False
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Đường dẫn tuyệt đối của thư mục cần xem. Ví dụ: D:\\AI_Test_Folder"
                    }
                },
                "required": ["path"]
            }
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        if not path:
            return {"success": False, "error": "Thiếu tham số 'path'."}

        if not FileSecurityManager.is_safe_path(path):
            return {"success": False, "error": f"Lỗi bảo mật: Không được phép truy cập '{path}'."}

        if not os.path.exists(path):
            return {"success": False, "error": f"Thư mục không tồn tại: {path}"}

        if not os.path.isdir(path):
            return {"success": False, "error": f"Đường dẫn không phải là thư mục: {path}"}

        try:
            items = os.listdir(path)

            # Phân loại file và folder
            folders = []
            files = []
            for item in items:
                full_item_path = os.path.join(path, item)
                if os.path.isdir(full_item_path):
                    folders.append(item)
                else:
                    files.append(item)

            # Giới hạn số lượng trả về để tránh tràn RAM của LLM
            MAX_ITEMS = 50
            total_items = len(folders) + len(files)

            result_data = {
                "total_items": total_items,
                "folders": folders[:MAX_ITEMS],
                "files": files[:MAX_ITEMS]
            }

            if total_items > MAX_ITEMS:
                result_data["warning"] = f"Thư mục quá lớn. Chỉ hiển thị {MAX_ITEMS} mục đầu tiên."

            return {
                "success": True,
                "data": result_data
            }
        except PermissionError:
            return {"success": False, "error": "Không có quyền đọc thư mục này (Permission Denied)."}
        except Exception as e:
            return {"success": False, "error": f"Lỗi hệ điều hành: {str(e)}"}