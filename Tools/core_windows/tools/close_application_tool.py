from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class CloseApplicationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="close_application", 
            description="Đóng một hoặc nhiều tiến trình dựa trên tên (process_name). RẤT NGUY HIỂM.", 
            requires_permission=True  # Bắt buộc phải có Y/N
        )
        self.manager = WindowsManager()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {"type": "string", "description": "Tên tiến trình cần đóng (VD: notepad.exe, chrome.exe)."}
                },
                "required": ["process_name"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        proc_name = kwargs.get("process_name")
        if not proc_name:
            return {"valid": False, "error": "Thiếu tham số 'process_name'."}
            
        # Chặn cứng từ vòng gửi xe để tránh Agent ảo giác vượt rào
        if proc_name.lower() in self.manager.process.SYSTEM_PROCESSES:
            return {"valid": False, "error": f"Lỗi bảo mật nghiêm trọng: Không được phép đóng tiến trình hệ thống '{proc_name}'."}
            
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        proc_name = kwargs.get("process_name")
        processes = self.manager.list_processes()
        targets = [p for p in processes if p.name.lower() == proc_name.lower()]

        if not targets:
            return {"success": False, "error": f"Không tìm thấy tiến trình nào mang tên '{proc_name}'."}

        killed_count = 0
        failed_count = 0
        for p in targets:
            if self.manager.terminate_process(p.pid):
                killed_count += 1
            else:
                failed_count += 1

        self._last_proc_name = proc_name
        return {"success": True, "message": f"Đã gửi lệnh đóng. Thành công: {killed_count}, Thất bại/AccessDenied: {failed_count}."}

    def verify(self, **kwargs) -> Dict[str, Any]:
        proc_name = getattr(self, "_last_proc_name", None)
        if not proc_name:
            return {"verified": True, "message": "Không có thao tác nào để xác minh."}

        # Kiểm tra xem còn cái process nào lảng vảng không
        is_closed = self.manager.wait_until(
            condition_func=lambda: not self.manager.check_process_by_name(proc_name),
            timeout=3.0,
            interval=0.5
        )

        if not is_closed:
            return {"verified": False, "message": f"Verification failed: Tiến trình '{proc_name}' vẫn đang chạy. Hệ điều hành từ chối lệnh đóng."}
            
        return {"verified": True, "message": f"Xác minh tất cả tiến trình '{proc_name}' đã tắt."}