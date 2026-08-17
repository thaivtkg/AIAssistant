from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class ListProcessesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_processes", 
            description="Liệt kê tiến trình. LUÔN SỬ DỤNG 'name_filter' để tìm kiếm ứng dụng cụ thể nhằm TRÁNH TRÀN BỘ NHỚ (Context Window).", 
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
                        "description": "Từ khóa tên tiến trình để lọc (VD: 'notepad', 'chrome'). AI Bắt buộc dùng tham số này nếu đang tìm một ứng dụng cụ thể."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Giới hạn số lượng tiến trình trả về để không làm tràn context (Mặc định: 15)."
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
        name_filter = kwargs.get("name_filter", "").lower()
        limit = kwargs.get("limit", 15)
        
        all_processes = self.manager.list_processes()
        
        # Áp dụng bộ lọc (Filter)
        if name_filter:
            filtered_processes = [p for p in all_processes if name_filter in p.name.lower()]
        else:
            filtered_processes = all_processes
            
        total_found = len(filtered_processes)
        
        # Áp dụng giới hạn số lượng (Truncate) để bảo vệ LLM
        limited_processes = filtered_processes[:limit]
        
        proc_list = [
            {
                "pid": p.pid, 
                "name": p.name, 
                "memory_mb": p.memory_mb, 
                "status": p.status
            } for p in limited_processes
        ]
        
        # Trả về thông báo cảnh báo nếu số lượng bị cắt bớt
        message = f"Hiển thị {len(proc_list)}/{total_found} tiến trình."
        if total_found > limit:
            message += " (Đã bị cắt bớt để bảo vệ bộ nhớ. Vui lòng dùng name_filter chi tiết hơn)."

        return {
            "success": True, 
            "total_found": total_found,
            "message": message,
            "processes": proc_list
        }