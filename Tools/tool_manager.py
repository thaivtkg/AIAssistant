from typing import Dict, Any, List
from Core.base_tool import BaseTool
from Core.interfaces import ILogger, IToolManager  # <-- Import thêm IToolManager


class ToolManager:
    def __init__(self, registry, logger=None):
        # Sử dụng registry được inject từ bên ngoài
        self.registry = registry
        self.logger = logger

    def has_tool(self, tool_name: str) -> bool:
        return self.registry.exists(tool_name)

    def get_all_schemas(self):
        return self.registry.get_all_schemas()

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        # SỬA LỖI TẠI ĐÂY: Dùng self.registry.get() thay vì self._registry.get()
        tool = self.registry.get(tool_name)
        
        if not tool:
            return {"success": False, "error": f"Tool '{tool_name}' không tồn tại."}

        # Vòng lặp cấp quyền (Preserved Existing Functionality)
        if tool.requires_permission:
            print(f"\n[⚠ YÊU CẦU XÁC NHẬN BẢO MẬT]")
            print(f"AI muốn chạy lệnh : {tool.name}")
            print(f"Tham số          : {kwargs}")
            
            while True:
                confirm = input("Cho phép thực thi? [Y/N]: ").strip().lower()
                if confirm == 'y':
                    if self.logger:
                        self.logger.info(f"[ToolManager] Người dùng ĐÃ CẤP QUYỀN cho '{tool.name}'.")
                    break
                elif confirm == 'n':
                    if self.logger:
                        self.logger.warning(f"[ToolManager] Người dùng ĐÃ TỪ CHỐI '{tool.name}'.")
                    return {"success": False, "error": "Người dùng đã từ chối cấp quyền thực thi. Hãy thông báo lại cho người dùng."}
                else:
                    print("Vui lòng chỉ nhập Y hoặc N.")

        # Gọi hàm execute của BaseTool (Đã tích hợp sẵn Verify Layer)
        return tool.execute(**kwargs)


