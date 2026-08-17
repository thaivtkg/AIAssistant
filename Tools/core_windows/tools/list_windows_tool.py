from typing import Dict, Any
from Core.base_tool import BaseTool
from Tools.core_windows.windows_manager import WindowsManager

class ListWindowsTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_windows", 
            description="Liệt kê danh sách các cửa sổ đang mở. Nên dùng title_filter để tìm chính xác.", 
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
                    "title_filter": {
                        "type": "string",
                        "description": "Từ khóa tên cửa sổ (title) để lọc (VD: 'Notepad', 'Chrome')."
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
        title_filter = kwargs.get("title_filter", "").lower()
        limit = kwargs.get("limit", 15)
        
        windows = self.manager.list_windows()
        
        # Áp dụng bộ lọc
        if title_filter:
            filtered_windows = [w for w in windows if title_filter in w.title.lower()]
        else:
            filtered_windows = windows
            
        total_found = len(filtered_windows)
        limited_windows = filtered_windows[:limit]
        
        win_list = [
            {
                "hwnd": w.hwnd, 
                "title": w.title, 
                "pid": w.pid, 
                "visible": w.visible, 
                "minimized": w.minimized
            } for w in limited_windows
        ]
        
        message = f"Hiển thị {len(win_list)}/{total_found} cửa sổ."
        if total_found > limit:
            message += " (Dữ liệu bị cắt bớt. Hãy cung cấp title_filter)."
            
        return {
            "success": True, 
            "total_found": total_found,
            "message": message,
            "windows": win_list
        }