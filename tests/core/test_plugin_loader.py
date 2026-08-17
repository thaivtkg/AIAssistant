import json
import pytest
import sys
from pathlib import Path
from Core.tool_registry import ToolRegistry
from Core.plugin_loader import PluginLoader
from Core.base_tool import BaseTool

@pytest.fixture
def loader(tmp_path):
    registry = ToolRegistry()
    return PluginLoader(registry=registry), tmp_path, registry

def test_plugin_loader_valid_manifest(loader):
    pl, tmp_dir, reg = loader
    
    # BƠM TMP_PATH VÀO SYS.PATH ĐỂ IMPORTLIB NHẬN DIỆN ĐƯỢC MODULE
    sys.path.insert(0, str(tmp_dir.parent))
    try:
        plugin_dir = tmp_dir / "valid_plugin"
        plugin_dir.mkdir()
        
        py_file = plugin_dir / "fake_module.py"
        py_file.write_text("""
from Core.base_tool import BaseTool
class ValidTool(BaseTool):
    def __init__(self): super().__init__("valid_tool", "Test")
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True}
        """)
        
        manifest = {
            "plugin_id": "valid", "enabled": True,
            "tools": [{"module": "fake_module", "class": "ValidTool"}]
        }
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
        
        pl.load_plugins(str(tmp_dir))
        assert reg.exists("valid_tool") is True
    finally:
        # Dọn dẹp môi trường sys.path
        sys.path.pop(0)

def test_plugin_loader_skips_disabled(loader):
    pl, tmp_dir, reg = loader
    plugin_dir = tmp_dir / "disabled_plugin"
    plugin_dir.mkdir()
    manifest = {"plugin_id": "disabled", "enabled": False, "tools": [{"module": "mod", "class": "Cls"}]}
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
    
    pl.load_plugins(str(tmp_dir))
    assert len(reg._tools) == 0

def test_plugin_loader_graceful_invalid_json(loader):
    pl, tmp_dir, reg = loader
    plugin_dir = tmp_dir / "bad_json"
    plugin_dir.mkdir()
    (plugin_dir / "manifest.json").write_text("{ broken json, ")
    
    pl.load_plugins(str(tmp_dir))
    assert len(reg._tools) == 0

def test_plugin_loader_graceful_missing_module_or_class(loader):
    pl, tmp_dir, reg = loader
    plugin_dir = tmp_dir / "missing_code"
    plugin_dir.mkdir()
    manifest = {
        "plugin_id": "miss", "enabled": True,
        "tools": [{"module": "not_exist", "class": "NoClass"}]
    }
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
    
    pl.load_plugins(str(tmp_dir))
    assert len(reg._tools) == 0