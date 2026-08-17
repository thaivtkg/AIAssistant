from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class FocusWindowTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="focus_window", 
            description="Đưa một cửa sổ lên phía trước (foreground) dựa vào HWND.", 
            requires_permission=False
        )
        self.manager = WindowsManager()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "hwnd": {"type": "integer", "description": "Window Handle (HWND) của cửa sổ cần focus."}
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
        success = self.manager.focus_window(hwnd)
        if not success:
            return {"success": False, "error": f"Không thể focus cửa sổ HWND {hwnd} (Cửa sổ có thể đã đóng hoặc là cửa sổ ẩn)."}
        return {"success": True, "message": f"Đã gửi lệnh focus tới cửa sổ HWND {hwnd}."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        """HẬU KIỂM: OS có thực sự đưa HWND này lên làm Foreground chưa?"""
        hwnd = kwargs.get("hwnd")
        
        # Poll kiểm tra tối đa 2 giây, mỗi 0.2 giây check 1 lần xem cửa sổ đã nổi lên chưa
        is_foreground = self.manager.wait_until(
            condition_func=lambda: self.manager.is_window_foreground(hwnd), 
            timeout=2.0, 
            interval=0.2
        )
        
        if not is_foreground:
            return {"verified": False, "message": "Verification failed: Cửa sổ không nổi lên foreground (Có thể bị HĐH chặn hoặc mất focus lập tức)."}
        
        return {"verified": True, "message": "Xác minh cửa sổ đã ở foreground."}