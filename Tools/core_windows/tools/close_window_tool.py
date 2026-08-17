from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class CloseWindowTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="close_window", 
            description="Đóng một cửa sổ cụ thể thông qua HWND. An toàn hơn đóng bằng Process Name.", 
            requires_permission=True  # Yêu cầu Y/N
        )
        self.manager = WindowsManager()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "hwnd": {"type": "integer", "description": "Window Handle (HWND) của cửa sổ cần đóng."}
                },
                "required": ["hwnd"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        hwnd = kwargs.get("hwnd")
        if not isinstance(hwnd, int) or hwnd <= 0:
            return {"valid": False, "error": "HWND phải là số nguyên dương."}
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        hwnd = kwargs.get("hwnd")
        success = self.manager.close_window(hwnd)
        if not success:
            return {"success": False, "error": f"Lỗi OS: Không thể gửi lệnh đóng tới cửa sổ HWND {hwnd}."}
            
        self._last_hwnd = hwnd
        return {"success": True, "message": f"Đã gửi tín hiệu WM_CLOSE tới cửa sổ HWND {hwnd}."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        hwnd = getattr(self, "_last_hwnd", None)
        if not hwnd:
            return {"verified": False, "message": "Lỗi nội bộ."}

        # SỬA LỖI: Kiểm tra trực tiếp bằng win32gui.IsWindow thay vì list_windows()
        is_closed = self.manager.wait_until(
            condition_func=lambda: not self.manager.is_window_alive(hwnd),
            timeout=3.0,
            interval=0.2
        )

        if not is_closed:
            return {"verified": False, "message": f"Verification failed: Cửa sổ HWND {hwnd} vẫn còn tồn tại (Có thể đang bị treo hoặc hỏi lưu file)."}
            
        return {"verified": True, "message": "Xác minh cửa sổ đã được đóng."}