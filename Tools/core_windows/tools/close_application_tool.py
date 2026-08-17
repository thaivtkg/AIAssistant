from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class CloseApplicationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="close_application", 
            description="Đóng một ứng dụng cụ thể (Graceful Close) thông qua PID. AI cần gọi get_process hoặc list_processes trước để lấy PID.", 
            requires_permission=True
        )
        self.manager = WindowsManager()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "PID của tiến trình cần đóng."}
                },
                "required": ["pid"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        pid = kwargs.get("pid")
        if not isinstance(pid, int) or pid <= 0:
            return {"valid": False, "error": "PID không hợp lệ."}
        
        try:
            proc = self.manager.get_process(pid)
        except PermissionError:
            return {"valid": False, "error": "ACCESS_DENIED: Không có quyền truy cập PID này."}
        except ProcessLookupError:
            return {"valid": False, "error": "NOT_FOUND: PID không tồn tại."}
            
        if self.manager.is_system_process(proc.name):
            return {"valid": False, "error": f"Lỗi bảo mật nghiêm trọng: Không được phép đóng hệ thống '{proc.name}'."}
            
        # P0 FIX: Truyền nguyên object ProcessInfo để Manager check Absolute Path
        if not self.manager.is_allowed_application_process(proc):
            return {"valid": False, "error": f"Lỗi bảo mật: Tiến trình '{proc.name}' không thuộc Allowlist hoặc chạy từ đường dẫn giả mạo."}
            
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        pid = kwargs.get("pid")
        self._target_pid = pid
        
        try:
            proc_race = self.manager.get_process(pid)
            # P0 FIX: Truyền nguyên object ProcessInfo
            if not self.manager.is_allowed_application_process(proc_race):
                return {"success": False, "error_code": "SECURITY_DENIED", "error": "PID đã bị tái sử dụng cho tiến trình không được phép."}
        except ProcessLookupError:
            return {"success": False, "error_code": "NOT_FOUND", "error": "Tiến trình đã biến mất trước khi kịp đóng."}
        except PermissionError:
            return {"success": False, "error_code": "ACCESS_DENIED", "error": "Mất quyền truy cập vào PID."}
        
        success = self.manager.close_application_gracefully(pid)
        if not success:
            return {"success": False, "error": f"Ứng dụng (PID: {pid}) không có cửa sổ để nhận lệnh đóng WM_CLOSE."}
            
        return {"success": True, "message": f"Đã gửi tín hiệu WM_CLOSE tới PID {pid}."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        pid = getattr(self, "_target_pid", None)
        if not pid: return {"verified": True, "message": "Không có thao tác nào."}

        def is_closed_func():
            try:
                self.manager.get_process(pid)
                return False
            except ProcessLookupError:
                return True
            except PermissionError:
                return False # Access denied = còn sống nhưng bị chặn quyền

        is_closed = self.manager.wait_until(is_closed_func, timeout=3.0, interval=0.5)

        if not is_closed:
            return {"verified": False, "message": f"Verification failed: PID {pid} vẫn đang chạy (Có thể bị treo hoặc hỏi lưu file)."}
        return {"verified": True, "message": f"Xác minh PID {pid} đã đóng hoàn toàn."}