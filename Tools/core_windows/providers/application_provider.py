import os
import subprocess
from typing import Optional, Dict
from Tools.core_windows.models.windows_models import ApplicationInfo

class ApplicationProvider:
    def __init__(self):
        windir = os.environ.get("WINDIR", r"C:\Windows")
        
        # CHỈ ĐỊNH ABSOLUTE TRUSTED PATHS. KHÔNG FALLBACK.
        self.ALLOWLIST: Dict[str, ApplicationInfo] = {
            "notepad": ApplicationInfo("notepad", "Notepad", os.path.join(windir, "System32", "notepad.exe")),
            "calculator": ApplicationInfo("calculator", "Calculator", os.path.join(windir, "System32", "calc.exe")),
            "explorer": ApplicationInfo("explorer", "File Explorer", os.path.join(windir, "explorer.exe")),
            "chrome": ApplicationInfo("chrome", "Google Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            "edge": ApplicationInfo("edge", "Microsoft Edge", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
        }

    def resolve_application(self, app_id: str) -> Optional[ApplicationInfo]:
        if not app_id or not isinstance(app_id, str):
            return None
        app = self.ALLOWLIST.get(app_id.strip().lower())
        
        # Chỉ trả về nếu file thực thi THỰC SỰ tồn tại ở đường dẫn Hardcode
        if app and os.path.isfile(app.executable_path):
            return app
        return None

    def open_application(self, app_info: ApplicationInfo) -> bool:
        if not app_info:
            return False
            
        executable = os.path.realpath(app_info.executable_path)
        if not os.path.isfile(executable):
            return False
            
        try:
            # Không dùng shell=True, khóa chặt executable
            subprocess.Popen([executable], shell=False, close_fds=True)
            return True
        except (OSError, subprocess.SubprocessError):
            return False

    def get_allowed_apps(self) -> Dict[str, str]:
        return {app_id: app.name for app_id, app in self.ALLOWLIST.items() if os.path.isfile(app.executable_path)}