from typing import Dict, Any
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

    def execute(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        content = kwargs.get("content", "")

        if not path:
            return {"success": False, "error": "Thiếu tham số 'path'."}

        if not FileSecurityManager.is_safe_path(path):
            return {"success": False, "error": f"Lỗi bảo mật: Truy cập bị từ chối đối với '{path}'."}

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "success": True,
                "message": f"Đã ghi file thành công: {path}"
            }
        except Exception as e:
            return {"success": False, "error": f"Lỗi hệ điều hành: {str(e)}"}