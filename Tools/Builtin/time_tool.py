from datetime import datetime
from typing import Dict, Any
from Core.base_tool import BaseTool

class SystemTimeTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="get_system_time",
            description="Lấy thời gian và ngày tháng hiện tại của hệ thống.",
            requires_permission=False
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        # Luôn fetch thời gian mới nhất khi hàm được gọi
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "success": True,
            "data": {
                "current_time": current_time
            }
        }