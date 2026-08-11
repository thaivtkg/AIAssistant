from typing import Any, Dict
from Core.base_plugin import BasePlugin

class SystemInfoPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="SystemInfo", version="1.0.0")

    def initialize(self) -> bool:
        if self.logger:
            self.logger.info(f"[{self.name}] Đã sẵn sàng.")
        return True

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "ping":
            return {"success": True, "message": "Pong! Core & Plugin giao tiếp tốt."}
        return {"success": False, "error": f"Hành động '{action}' không được hỗ trợ."}

    def shutdown(self) -> None:
        if self.logger:
            self.logger.info(f"[{self.name}] Đã giải phóng tài nguyên.")