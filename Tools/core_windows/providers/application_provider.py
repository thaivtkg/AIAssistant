import os
import shutil
import subprocess
from typing import Optional, Dict
from Tools.core_windows.models.windows_models import ApplicationInfo

class ApplicationProvider:
    def __init__(self):
        # Trì hoãn việc lookup đường dẫn cứng, dựa vào shutil.which hoặc sys path
        self.ALLOWLIST: Dict[str, ApplicationInfo] = {
            "notepad": ApplicationInfo("notepad", "Notepad", "notepad.exe"),
            "calculator": ApplicationInfo("calculator", "Calculator", "calc.exe"),
            "explorer": ApplicationInfo("explorer", "File Explorer", "explorer.exe"),
            # Portable lookup
            "chrome": ApplicationInfo("chrome", "Google Chrome", self._resolve_path("chrome.exe", [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ])),
            "edge": ApplicationInfo("edge", "Microsoft Edge", self._resolve_path("msedge.exe", [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            ]))
        }

    def _resolve_path(self, exe_name: str, common_paths: list) -> str:
        """Thử tìm file thực thi trong PATH hệ thống hoặc các đường dẫn phổ biến."""
        which_path = shutil.which(exe_name)
        if which_path:
            return which_path
        for path in common_paths:
            if os.path.exists(path):
                return path
        return exe_name # Fallback về tên để HĐH tự lo

    def resolve_application(self, app_id: str) -> Optional[ApplicationInfo]:
        return self.ALLOWLIST.get(app_id.lower())

    def open_application(self, app_info: ApplicationInfo) -> bool:
        try:
            subprocess.Popen([app_info.executable_path])
            return True
        except Exception:
            return False
            
    def get_allowed_apps(self) -> Dict[str, str]:
        return {app_id: app.name for app_id, app in self.ALLOWLIST.items()}