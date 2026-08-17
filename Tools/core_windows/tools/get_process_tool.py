from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class GetProcessTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="get_process", 
            description="Lấy thông tin chi tiết của một tiến trình thông qua PID.", 
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
                    "pid": {"type": "integer", "description": "PID của tiến trình cần kiểm tra."}
                },
                "required": ["pid"]
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        pid = kwargs.get("pid")
        if not isinstance(pid, int) or pid <= 0:
            return {"valid": False, "error": "PID phải là số nguyên dương lớn hơn 0."}
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        pid = kwargs.get("pid")
        proc = self.manager.get_process(pid)
        
        if not proc:
            return {"success": False, "error": f"Không tìm thấy tiến trình với PID {pid} (Có thể đã đóng hoặc AccessDenied)."}
        
        return {
            "success": True, 
            "process": {
                "pid": proc.pid, 
                "name": proc.name, 
                "exe": proc.exe, 
                "status": proc.status, 
                "memory_mb": proc.memory_mb
            }
        }