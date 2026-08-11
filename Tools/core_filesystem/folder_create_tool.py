import os
from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_filesystem.security import FileSecurityManager

class CreateFolderTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="create_folder",
            description="Tạo một thư mục mới tại đường dẫn được chỉ định.",
            requires_permission=False
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Đường dẫn tuyệt đối của thư mục cần tạo."}
                },
                "required": ["path"]
            }
        }

    def _execute(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        if not path:
            return {"success": False, "error": "Thiếu tham số 'path'."}

        if not FileSecurityManager.is_safe_path(path):
            return {"success": False, "error": f"Lỗi bảo mật: Cấm truy cập '{path}'."}

        try:
            os.makedirs(path, exist_ok=True)
            return {"success": True, "message": f"Đã gửi lệnh tạo thư mục: {path}"}
        except Exception as e:
            return {"success": False, "error": f"Lỗi hệ điều hành: {str(e)}"}

    def verify(self, **kwargs) -> Dict[str, Any]:
        """HẬU KIỂM: Thư mục đã được ghi vật lý lên ổ cứng chưa?"""
        path = kwargs.get("path")
        if not os.path.exists(path) or not os.path.isdir(path):
            return {"verified": False, "message": f"Không tìm thấy thư mục '{path}' trên ổ cứng."}
        return {"verified": True, "message": "Xác minh thư mục đã tồn tại."}