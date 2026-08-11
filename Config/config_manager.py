import json
import os

class ConfigManager:
    def __init__(self, config_path="Config/settings.json"):
        self.config_path = config_path
        self.settings = self._get_default_settings()
        self.load()

    def _get_default_settings(self):
        return {
            "app_name": "Offline AI Assistant",
            "version": "1.0 - Sprint 0",
            "log_level": "INFO",
            "model_path": "Models/",
            "plugin_dir": "Plugins/"
        }

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                try:
                    user_settings = json.load(f)
                    self.settings.update(user_settings)
                except json.JSONDecodeError:
                    print("Lỗi đọc file config. Dùng cấu hình mặc định.")
        else:
            self.save() # Tạo file mới nếu chưa có

    def save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
        
    def get(self, key, default=None):
        return self.settings.get(key, default)