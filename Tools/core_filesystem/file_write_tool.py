import os
from typing import Any, Dict

from Core.base_tool import BaseTool
from Tools.core_filesystem.security import FileSecurityManager


class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Tạo file mới hoặc ghi đè nội dung vào file hiện tại.",
            requires_permission=True
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
                        "description": "Đường dẫn tuyệt đối của file."
                    },
                    "content": {
                        "type": "string",
                        "description": "Nội dung cần ghi vào file."
                    }
                },
                "required": ["path", "content"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        if not path:
            return {"valid": False, "error": "Thiếu tham số 'path'."}
        if not FileSecurityManager.is_safe_path(path):
            return {"valid": False, "error": f"Lỗi bảo mật: Cấm thao tác '{path}'."}
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        content = kwargs.get("content", "")
        try:
            with open(path, 'w', encoding='utf-8') as f:
               f.write(content)
            return {"success": True, "message": f"Đã ghi file: {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify(self, **kwargs) -> Dict[str, Any]:
        """HẬU KIỂM: Đảm bảo file thực sự đã được tạo trên ổ cứng"""
        path = kwargs.get("path")
        if not os.path.exists(path):
            return {"verified": False, "message": "File chưa được ghi xuống đĩa."}
        return {"verified": True, "message": "Xác minh file đã tồn tại."}