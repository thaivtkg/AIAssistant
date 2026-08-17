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
        # Tự động lấy danh sách app hợp lệ để đưa vào Prompt cho LLM
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
                        "description": f"ID của ứng dụng cần mở. CHỈ ĐƯỢC PHÉP CHỌN CÁC ID SAU: {app_list}."
                    }
                },
                "required": ["app_id"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        app_id = kwargs.get("app_id")
        if not app_id:
            return {"valid": False, "error": "Thiếu tham số 'app_id'."}
            
        app = self.manager.resolve_application(app_id)
        if not app:
            return {"valid": False, "error": f"Lỗi bảo mật: Ứng dụng '{app_id}' không tồn tại trong Allowlist."}
            
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        app_id = kwargs.get("app_id")
        app = self.manager.resolve_application(app_id)
        
        success = self.manager.open_application(app_id)
        if not success:
            return {"success": False, "error": f"Lỗi OS: Không thể khởi chạy '{app_id}'."}
            
        # Trích xuất tên file exe (VD: notepad.exe) để Verify Layer kiểm tra
        self._last_exe = app.executable_path.split("\\")[-1]
        
        return {"success": True, "message": f"Đã gửi lệnh khởi chạy ứng dụng '{app.name}'."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        exe_name = getattr(self, "_last_exe", None)
        if not exe_name:
            return {"verified": False, "message": "Lỗi nội bộ: Không thể tìm thấy exe_name để xác minh."}

        # Chờ tối đa 5 giây xem Process có thực sự trồi lên hệ thống không
        is_running = self.manager.wait_until(
            condition_func=lambda: self.manager.check_process_by_name(exe_name),
            timeout=5.0,
            interval=0.5
        )

        if not is_running:
            return {"verified": False, "message": f"Verification failed: Không tìm thấy tiến trình '{exe_name}' sau 5 giây. Ứng dụng có thể đã crash."}
            
        return {"verified": True, "message": "Xác minh ứng dụng đã khởi chạy thành công."}