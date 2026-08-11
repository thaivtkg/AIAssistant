import importlib
import os
from typing import Dict, Any
from Core.base_plugin import BasePlugin
from Core.interfaces import ILogger, IConfig

class PluginManager:
    def __init__(self, logger: ILogger, config: IConfig):
        self.logger = logger
        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Đăng ký một plugin vào hệ thống"""
        try:
            plugin.setup(self.logger, self.config)
            if plugin.initialize():
                self.plugins[plugin.name] = plugin
                self.logger.info(f"[PluginLoaded] {plugin.name} (v{plugin.version})")
                return True
            else:
                self.logger.warning(f"[PluginFailed] Không thể khởi tạo {plugin.name}")
        except Exception as e:
            self.logger.error(f"[PluginError] Lỗi khi nạp plugin {plugin.name}: {str(e)}")
        return False

    def execute_action(self, plugin_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Gọi hành động từ plugin"""
        if plugin_name not in self.plugins:
            error_msg = f"Plugin '{plugin_name}' chưa được nạp hoặc không tồn tại."
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            return self.plugins[plugin_name].execute(action, **kwargs)
        except Exception as e:
            self.logger.error(f"Lỗi thực thi action '{action}' tại plugin '{plugin_name}': {str(e)}")
            return {"success": False, "error": str(e)}

    def shutdown_all(self) -> None:
        """Tắt toàn bộ plugin an toàn"""
        for name, plugin in self.plugins.items():
            try:
                plugin.shutdown()
                self.logger.info(f"[PluginShutdown] {name}")
            except Exception as e:
                self.logger.error(f"Lỗi khi tắt plugin {name}: {str(e)}")