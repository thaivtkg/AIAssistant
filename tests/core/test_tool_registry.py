import pytest
from Core.tool_registry import ToolRegistry
from Core.base_tool import BaseTool

class DummyToolA(BaseTool):
    def __init__(self):
        super().__init__("dummy_tool", "Dummy A")
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True}

class DummyToolB(BaseTool):
    def __init__(self):
        super().__init__("dummy_tool", "Dummy B (Same name)")
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True}


def test_tool_registry_registration():
    registry = ToolRegistry()
    tool_a = DummyToolA()
    registry.register(tool_a)
    
    assert registry.exists("dummy_tool") is True
    assert registry.get("dummy_tool") == tool_a

def test_tool_registry_prevents_collision():
    registry = ToolRegistry()
    tool_a = DummyToolA()
    tool_b = DummyToolB()

    registry.register(tool_a)
    
    # Cố tình đăng ký tool_b có cùng tên "dummy_tool", mặc định allow_override=False
    with pytest.raises(ValueError) as excinfo:
        registry.register(tool_b)
    
    assert "Tool Collision" in str(excinfo.value)
    
    # Đảm bảo tool_a vẫn là tool duy nhất trong registry
    assert registry.get("dummy_tool").description == "Dummy A"