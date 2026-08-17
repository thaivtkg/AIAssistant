from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class ListProcessesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_processes", 
            description="Liệt kê tiến trình. LUÔN SỬ DỤNG 'name_filter' để tìm kiếm ứng dụng cụ thể nhằm TRÁNH TRÀN BỘ NHỚ.", 
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
                    "name_filter": {
                        "type": "string",
                        "description": "Từ khóa tên tiến trình để lọc (VD: 'notepad')."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Giới hạn số lượng trả về (Mặc định: 15)."
                    }
                },
                "required": []
            }
        }

    def _validate(self, **kwargs) -> Dict[str, Any]:
        limit = kwargs.get("limit", 15)
        if not isinstance(limit, int) or limit <= 0:
            return {"valid": False, "error": "Tham số 'limit' phải là số nguyên dương."}
        return {"valid": True}

    def _execute(self, **kwargs) -> Dict[str, Any]:
        name_filter = kwargs.get("name_filter", "")
        limit = kwargs.get("limit", 15)
        
        # TỐI ƯU (P2.1): Đẩy filter xuống Provider để giảm Overhead OS I/O
        filtered_processes = self.manager.list_processes(name_filter=name_filter)
        
        total_found = len(filtered_processes)
        limited_processes = filtered_processes[:limit]
        
        proc_list = [
            {
                "pid": p.pid, 
                "name": p.name, 
                "memory_mb": p.memory_mb, 
                "status": p.status
            } for p in limited_processes
        ]
        
        message = f"Hiển thị {len(proc_list)}/{total_found} tiến trình."
        if total_found > limit:
            message += " (Đã bị cắt bớt. Vui lòng dùng name_filter chi tiết hơn)."

        return {
            "success": True, 
            "total_found": total_found,
            "message": message,
            "processes": proc_list
        }