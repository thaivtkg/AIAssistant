from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class OpenApplicationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="open_application", 
            description="Mở một ứng dụng hệ thống an toàn thông qua danh sách Allowlist.", 
            requires_permission=False
        )
        self.manager = WindowsManager()

    def get_schema(self) -> Dict[str, Any]:
        allowed_apps = self.manager.application.get_allowed_apps()
        app_list = ", ".join([f"'{k}' ({v})" for k, v in allowed_apps.items()])
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string", 
                        "description": f"ID của ứng dụng cần mở. CHỈ ĐƯỢC PHÉP CHỌN: {app_list}."
                    }
                },
                "required": ["app_id"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        app_id = kwargs.get("app_id")
        if not app_id:
            return {"valid": False, "error": "Thiếu tham số 'app_id'."}
        if not self.manager.resolve_application(app_id):
            return {"valid": False, "error": f"Lỗi bảo mật: Ứng dụng '{app_id}' không tồn tại trong Allowlist."}
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        app_id = kwargs.get("app_id")
        app = self.manager.resolve_application(app_id)
        
        exe_name = app.executable_path.split("\\")[-1]
        
        # 1. Chụp ảnh snapshot các PID trước khi khởi chạy
        self._before_pids = set(self.manager.process.get_pids_by_name(exe_name))
        self._last_exe = exe_name
        
        # 2. Khởi chạy
        success = self.manager.open_application(app_id)
        if not success:
            return {"success": False, "error": f"Lỗi OS: Không thể khởi chạy '{app_id}'."}
            
        return {"success": True, "message": f"Đã gửi lệnh khởi chạy ứng dụng '{app.name}'."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        exe_name = getattr(self, "_last_exe", None)
        before_pids = getattr(self, "_before_pids", set())

        if not exe_name:
            return {"verified": False, "message": "Lỗi nội bộ."}

        # Kiểm tra xem có PID nào MỚI xuất hiện không
        def launched():
            current_pids = set(self.manager.process.get_pids_by_name(exe_name))
            return bool(current_pids - before_pids)

        verified = self.manager.wait_until(launched, timeout=5.0, interval=0.5)

        if not verified:
            return {
                "verified": False, 
                "message": f"Verification failed: Không phát hiện tiến trình mới của '{exe_name}'. Có thể HĐH từ chối hoặc ứng dụng đã crash lập tức."
            }
            
        return {"verified": True, "message": "Xác minh ứng dụng đã khởi chạy thành công (Phát hiện PID mới)."}