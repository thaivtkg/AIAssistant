import os
import json
import importlib
import logging
from pathlib import Path
from Core.tool_registry import ToolRegistry

class PluginLoader:
    def __init__(self, registry: ToolRegistry, logger: logging.Logger = None):
        self.registry = registry
        self.logger = logger

    def load_plugins(self, plugins_dir: str = "Tools") -> None:
        """Quét và nạp tất cả plugin dựa trên manifest.json (An toàn không crash)"""
        base_path = Path(plugins_dir).resolve()
        
        # Fallback: Nếu thư mục chưa có, log cảnh báo và dừng an toàn
        if not base_path.exists():
            if self.logger:
                self.logger.warning(f"[PluginLoader] Thư mục plugins không tồn tại: {base_path}")
            return

        for root, _, files in os.walk(base_path):
            if "manifest.json" in files:
                self._load_plugin(Path(root), base_path)

    def _load_plugin(self, plugin_dir: Path, base_dir: Path) -> None:
        manifest_path = plugin_dir / "manifest.json"
        
        # RECOVERY 1: Bắt lỗi cú pháp JSON
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"[PluginLoader] Lỗi cú pháp JSON tại '{manifest_path}': {e}. Đã bỏ qua plugin này.")
            return
        except Exception as e:
            if self.logger:
                self.logger.error(f"[PluginLoader] Lỗi đọc file '{manifest_path}': {e}. Đã bỏ qua.")
            return

        # Kiểm tra cờ kích hoạt
        if not manifest.get("enabled", False):
            if self.logger:
                self.logger.info(f"[PluginLoader] Đã bỏ qua plugin '{manifest.get('plugin_id')}' (enabled=False).")
            return

        tools_list = manifest.get("tools", [])
        for tool_info in tools_list:
            module_name = tool_info.get("module")
            class_name = tool_info.get("class")
            
            if not module_name or not class_name:
                continue

            rel_path = plugin_dir.relative_to(base_dir.parent)
            full_module_path = ".".join(rel_path.parts) + "." + module_name

            # RECOVERY 2: Bắt lỗi module/class không tồn tại
            try:
                module = importlib.import_module(full_module_path)
                tool_class = getattr(module, class_name)
                tool_instance = tool_class()
                
                self.registry.register(tool_instance)
                
                if self.logger:
                    self.logger.info(f"  [+] Đã nạp Tool: {tool_instance.name} (Plugin: {manifest.get('plugin_id')})")
            except ModuleNotFoundError as e:
                if self.logger:
                    self.logger.error(f"[PluginLoader] Không tìm thấy file code '{full_module_path}': {e}")
            except AttributeError as e:
                if self.logger:
                    self.logger.error(f"[PluginLoader] Không có class '{class_name}' trong '{full_module_path}': {e}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[PluginLoader] Lỗi Runtime khi khởi tạo {class_name}: {e}")