from typing import Dict, Any

class BaseTool:
    def __init__(self, name: str, description: str, requires_permission: bool = False):
        self.name = name
        self.description = description
        self.requires_permission = requires_permission

    def get_schema(self) -> Dict[str, Any]:
        """Khai báo JSON schema cho LLM."""
        raise NotImplementedError

    def _execute(self, **kwargs) -> Dict[str, Any]:
        """Logic thực thi chính. Các class con BẮT BUỘC ghi đè hàm này."""
        raise NotImplementedError

    def verify(self, **kwargs) -> Dict[str, Any]:
        """
        Xác minh hậu kiểm (Verification Layer).
        Mặc định trả về True cho các Tool chỉ đọc (Read-only).
        """
        return {"verified": True, "message": "Không yêu cầu xác minh."}

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Hàm public được gọi bởi ToolManager. Quản lý vòng đời Thực thi -> Xác minh."""
        # Bước 1: Thực thi logic chính
        try:
            result = self._execute(**kwargs)
        except Exception as e:
            return {"success": False, "error": f"Ngoại lệ khi chạy tool: {str(e)}"}

        # Nếu thất bại ngay từ bước thực thi, trả về luôn (không cần xác minh)
        if not result.get("success", False):
            return result

        # Bước 2: Xác minh kết quả (Verification)
        try:
            verify_result = self.verify(**kwargs)
            result["verification"] = verify_result
            
            # Nếu xác minh thất bại, lật ngược kết quả success thành False
            if not verify_result.get("verified", False):
                result["success"] = False
                result["error"] = f"Lệnh chạy không báo lỗi, nhưng xác minh hệ thống THẤT BẠI: {verify_result.get('message', 'Không có lý do')}"
        except Exception as e:
            result["success"] = False
            result["error"] = f"Ngoại lệ trong quá trình xác minh hậu kiểm: {str(e)}"

        return result