from typing import Dict, Any, List
from Core.base_tool import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool, allow_override: bool = False) -> None:
        if tool.name in self._tools and not allow_override:
            raise ValueError(f"Tool Collision: Tool mang tên '{tool.name}' đã tồn tại trong Registry.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def exists(self, name: str) -> bool:
        return name in self._tools

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self._tools.values()]