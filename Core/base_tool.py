from typing import Dict, Any

class BaseTool:
    def __init__(self, name: str, description: str, requires_permission: bool = False):
        self.name = name
        self.description = description
        self.requires_permission = requires_permission

    def get_schema(self) -> Dict[str, Any]:
        raise NotImplementedError

    def _validate(self, **kwargs) -> Dict[str, Any]:
        """Validate input. Subclass có thể override nếu cần kiểm tra logic phức tạp."""
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        """Nơi subclass BẮT BUỘC triển khai logic."""
        raise NotImplementedError

    def verify(self, **kwargs) -> Dict[str, Any]:
        """Hậu kiểm. Mặc định trả về True cho Tool read-only."""
        return {"verified": True, "message": "Không yêu cầu xác minh."}

    # TUYỆT ĐỐI KHÔNG OVERRIDE HÀM NÀY Ở SUBCLASS
    def execute(self, **kwargs) -> Dict[str, Any]:
        # 1. Validate
        val_result = self._validate(**kwargs)
        if not val_result.get("valid", False):
            return {"success": False, "error": f"Validation failed: {val_result.get('error', 'Unknown')}"}

        # 2. Execute
        try:
            result = self._execute(**kwargs)
        except Exception as e:
            return {"success": False, "error": f"Execution exception: {str(e)}"}

        if not result.get("success", False):
            return result

        # 3. Verify
        try:
            ver_result = self.verify(**kwargs)
            result["verification"] = ver_result
            if not ver_result.get("verified", False):
                result["success"] = False
                result["error"] = f"Verification failed: {ver_result.get('message', 'No reason provided')}"
        except Exception as e:
            result["success"] = False
            result["error"] = f"Verification exception: {str(e)}"

        return result