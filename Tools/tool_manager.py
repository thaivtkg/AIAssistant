from typing import Dict, Any, List
from Core.base_tool import BaseTool
from Core.interfaces import ILogger, IToolManager  # <-- Import thêm IToolManager


class ToolManager(IToolManager):  # <-- Kế thừa IToolManager
    def __init__(self, registry, logger=None):
        self.registry = registry
        self.logger = logger

    def has_tool(self, tool_name: str) -> bool:
        return self.registry.exists(tool_name)

    def get_all_schemas(self):
        return self.registry.get_all_schemas()

    def execute_tool(self, tool_name: str, **kwargs):
        tool = self.registry.get(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool '{tool_name}' không tồn tại."}

        tool = self._registry[tool_name]

        # --- CƠ CHẾ XÁC NHẬN BẢO MẬT (MỚI) ---
        if tool.requires_permission:
            print(f"\n\033[93m[⚠ YÊU CẦU XÁC NHẬN BẢO MẬT]\033[0m")
            print(f"AI muốn chạy lệnh : \033[96m{tool_name}\033[0m")
            print(f"Tham số          : {kwargs}")

            while True:
                confirm = input("Cho phép thực thi? [Y/N]: ").strip().lower()
                if confirm == 'y':
                    self.logger.info(f"[ToolEngine] Người dùng ĐÃ XÁC NHẬN cho phép '{tool_name}'.")
                    break
                elif confirm == 'n':
                    self.logger.warning(f"[ToolEngine] Người dùng ĐÃ TỪ CHỐI '{tool_name}'.")
                    return {"success": False, "error": "User denied permission. (Người dùng đã hủy lệnh)"}
        # --------------------------------------

        # Thực thi Tool
        try:
            result = tool.execute(**kwargs)
            self.logger.info(f"[ToolEngine] Tool '{tool_name}' thực thi xong. Kết quả: {result}")
            return tool.execute(**kwargs)
        except Exception as e:
            error_msg = f"Lỗi nội tại khi chạy tool '{tool_name}': {str(e)}"
            self.logger.error(f"[ToolEngine] {error_msg}")
            return {"success": False, "error": error_msg}


