import pytest
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock
from Core.tool_registry import ToolRegistry
from Core.plugin_loader import PluginLoader
from Tools.tool_manager import ToolManager

def test_full_plugin_to_execution_flow(tmp_path):
    """
    Integration Test:
    Tạo Plugin vật lý -> Manifest -> Loader -> Registry -> ToolManager -> Execute -> Verify Result
    """
    sys.path.insert(0, str(tmp_path.parent))
    try:
        plugin_dir = tmp_path / "integration_plugin"
        plugin_dir.mkdir()
        
        py_file = plugin_dir / "math_tool.py"
        py_file.write_text("""
from Core.base_tool import BaseTool
class AddTool(BaseTool):
    def __init__(self): super().__init__("add_tool", "Add 2 numbers", requires_permission=False)
    def get_schema(self): return {}
    def _execute(self, **kwargs): 
        a = kwargs.get("a", 0)
        b = kwargs.get("b", 0)
        return {"success": True, "result": a + b}
    def verify(self, **kwargs):
        return {"verified": True}
        """)
        
        manifest = {
            "plugin_id": "math_plugin", "enabled": True,
            "tools": [{"module": "math_tool", "class": "AddTool"}]
        }
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
        
        registry = ToolRegistry()
        loader = PluginLoader(registry)
        
        loader.load_plugins(str(tmp_path))
        
        assert registry.exists("add_tool") is True
        
        manager = ToolManager(registry, logger=MagicMock())
        result = manager.execute_tool("add_tool", a=5, b=10)
        
        assert result["success"] is True
        assert result["result"] == 15
        assert result["verification"]["verified"] is True
    finally:
        sys.path.pop(0)