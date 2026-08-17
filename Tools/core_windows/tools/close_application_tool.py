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
            
        proc = self.manager.get_process(pid)
        if not proc:
            return {"valid": False, "error": f"Không tìm thấy tiến trình với PID {pid}."}
            
        if proc.name.lower() in self.manager.process.SYSTEM_PROCESSES:
            return {"valid": False, "error": f"Lỗi bảo mật nghiêm trọng: Không được phép đóng tiến trình hệ thống '{proc.name}'."}
            
        # SIẾT CHẶT (MEDIUM): Phải thuộc ALLOWLIST mới được phép đóng
        allowed_exes = []
        for app in self.manager.application.ALLOWLIST.values():
            exe_name = app.executable_path.split("\\")[-1].lower()
            allowed_exes.append(exe_name)
            allowed_exes.append(app.app_id.lower())
            
        if proc.name.lower() not in allowed_exes:
            return {"valid": False, "error": f"Lỗi bảo mật: Tiến trình '{proc.name}' không nằm trong Allowlist. Agent chỉ được phép đóng các ứng dụng do Agent quản lý."}
            
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        pid = kwargs.get("pid")
        self._target_pid = pid
        
        # Gọi Graceful Close (Gửi WM_CLOSE tới các cửa sổ của PID)
        success = self.manager.close_application_gracefully(pid)
        if not success:
            return {"success": False, "error": f"Ứng dụng (PID: {pid}) không phản hồi lệnh đóng (Không có HWND hợp lệ). Không hỗ trợ Terminate/Kill trong Sprint 4."}
            
        return {"success": True, "message": f"Đã gửi tín hiệu đóng an toàn (WM_CLOSE) tới ứng dụng PID {pid}."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        pid = getattr(self, "_target_pid", None)
        if not pid:
            return {"verified": True, "message": "Không có thao tác nào."}

        # Hậu kiểm: Xác minh PID đã thực sự biến mất
        is_closed = self.manager.wait_until(
            condition_func=lambda: self.manager.get_process(pid) is None,
            timeout=3.0,
            interval=0.5
        )

        if not is_closed:
            return {"verified": False, "message": f"Verification failed: Ứng dụng PID {pid} vẫn đang chạy (Có thể do ứng dụng yêu cầu lưu file hoặc treo)."}
            
        return {"verified": True, "message": f"Xác minh ứng dụng PID {pid} đã đóng hoàn toàn."}