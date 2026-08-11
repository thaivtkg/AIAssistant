import os
from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_filesystem.security import FileSecurityManager

class ReadFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Đọc nội dung của một file văn bản. Trả về tối đa 5000 ký tự.",
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
                        "description": "Đường dẫn tuyệt đối của file cần đọc."
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
            return {"success": False, "error": f"Lỗi bảo mật: Truy cập bị từ chối đối với '{path}'."}

        if not os.path.exists(path) or not os.path.isfile(path):
            return {"success": False, "error": f"File không tồn tại: {path}"}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read(5000)
            return {
                "success": True,
                "data": {
                    "content": content,
                    "truncated": len(content) == 5000
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Lỗi hệ điều hành: {str(e)}"}