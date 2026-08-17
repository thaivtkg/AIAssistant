import pytest
from unittest.mock import patch, MagicMock
from Core.tool_registry import ToolRegistry
from Tools.tool_manager import ToolManager
from Core.base_tool import BaseTool

class SafeTool(BaseTool):
    def __init__(self): super().__init__("safe_tool", "Safe", requires_permission=False)
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True, "msg": "done safe"}

class DangerousTool(BaseTool):
    def __init__(self): super().__init__("danger_tool", "Danger", requires_permission=True)
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True, "msg": "done danger"}

@pytest.fixture
def manager():
    registry = ToolRegistry()
    registry.register(SafeTool())
    registry.register(DangerousTool())
    return ToolManager(registry, logger=MagicMock())

def test_manager_executes_safe_tool_without_prompt(manager):
    res = manager.execute_tool("safe_tool")
    assert res["success"] is True
    assert res["msg"] == "done safe"

def test_manager_executes_danger_tool_if_user_allows(manager):
    # Mock hàm input() trả về 'y'
    with patch("builtins.input", return_value="y"):
        res = manager.execute_tool("danger_tool")
        assert res["success"] is True
        assert res["msg"] == "done danger"

def test_manager_rejects_danger_tool_if_user_denies(manager):
    # Mock hàm input() trả về 'n'
    with patch("builtins.input", return_value="n"):
        res = manager.execute_tool("danger_tool")
        assert res["success"] is False
        assert "từ chối cấp quyền" in res["error"]

def test_manager_returns_error_if_tool_not_found(manager):
    res = manager.execute_tool("not_exist")
    assert res["success"] is False
    assert "không tồn tại" in res["error"]