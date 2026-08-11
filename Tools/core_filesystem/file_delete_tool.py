import os
from typing import Any, Dict

from Core.base_tool import BaseTool
from Tools.core_filesystem.security import FileSecurityManager


class DeleteFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="delete_file",
            description="Xóa một file tại đường dẫn được chỉ định. BẮT BUỘC dùng khi người dùng yêu cầu xóa file.",
            requires_permission=True 
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Đường dẫn tuyệt đối của file."}
                },
                "required": ["path"]
            }
        }

    def _execute(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        if not path:
            return {"success": False, "error": "Thiếu tham số 'path'."}

        if not FileSecurityManager.is_safe_path(path):
            return {"success": False, "error": f"Lỗi bảo mật: Cấm thao tác tại '{path}'."}

        if not os.path.exists(path):
            return {"success": False, "error": f"File không tồn tại: {path}"}
            
        if not os.path.isfile(path):
            return {"success": False, "error": f"Đường dẫn là thư mục, không phải file: {path}"}

        try:
            os.remove(path)
            return {"success": True, "message": f"Đã gửi lệnh xóa file: {path}"}
        except Exception as e:
            return {"success": False, "error": f"Lỗi hệ điều hành khi xóa: {str(e)}"}

    def verify(self, **kwargs) -> Dict[str, Any]:
        """HẬU KIỂM: File thực sự đã bốc hơi khỏi hệ thống chưa?"""
        path = kwargs.get("path")
        if os.path.exists(path):
            return {"verified": False, "message": f"Dữ liệu vẫn còn tồn tại trên ổ cứng tại '{path}'."}
        return {"verified": True, "message": "Xác minh file đã bị xóa hoàn toàn."}