import pytest
from Core.tool_registry import ToolRegistry
from Core.base_tool import BaseTool

class DummyToolA(BaseTool):
    def __init__(self): super().__init__("dummy_tool", "Dummy A")
    def get_schema(self): return {"name": self.name, "desc": self.description}
    def _execute(self, **kwargs): return {"success": True}

class DummyToolB(BaseTool):
    def __init__(self): super().__init__("dummy_tool", "Dummy B (Same name)")
    def get_schema(self): return {"name": self.name, "desc": self.description}
    def _execute(self, **kwargs): return {"success": True}


def test_tool_registry_registration():
    registry = ToolRegistry()
    tool_a = DummyToolA()
    registry.register(tool_a)
    assert registry.exists("dummy_tool") is True
    assert registry.get("dummy_tool") == tool_a

def test_tool_registry_prevents_collision_by_default():
    registry = ToolRegistry()
    registry.register(DummyToolA())
    
    with pytest.raises(ValueError) as excinfo:
        registry.register(DummyToolB())
    assert "Tool Collision" in str(excinfo.value)
    assert registry.get("dummy_tool").description == "Dummy A"

# --- BỔ SUNG CÁC TRƯỜNG HỢP BIÊN ---
def test_tool_registry_allows_override_if_explicit():
    registry = ToolRegistry()
    registry.register(DummyToolA())
    registry.register(DummyToolB(), allow_override=True)
    # Đã bị đè thành Dummy B
    assert registry.get("dummy_tool").description == "Dummy B (Same name)"

def test_tool_registry_get_nonexistent_returns_none():
    registry = ToolRegistry()
    assert registry.get("not_exist") is None
    assert registry.exists("not_exist") is False

def test_tool_registry_get_all_schemas():
    registry = ToolRegistry()
    registry.register(DummyToolA())
    
    class ToolC(BaseTool):
        def __init__(self): super().__init__("tool_c", "C")
        def get_schema(self): return {"name": "tool_c"}
        def _execute(self, **kwargs): return {"success": True}
        
    registry.register(ToolC())
    
    schemas = registry.get_all_schemas()
    assert len(schemas) == 2
    names = [s.get("name") for s in schemas]
    assert "dummy_tool" in names
    assert "tool_c" in names