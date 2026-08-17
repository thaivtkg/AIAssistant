import os
import subprocess
from typing import Optional, Dict
from Tools.core_windows.models.windows_models import ApplicationInfo

class ApplicationProvider:
    # Bức tường bảo mật (Allowlist): Chỉ cho phép mở các ứng dụng đã đăng ký
    ALLOWLIST: Dict[str, ApplicationInfo] = {
        "notepad": ApplicationInfo("notepad", "Notepad", "C:\\Windows\\System32\\notepad.exe"),
        "calculator": ApplicationInfo("calculator", "Calculator", "calc.exe"), # Win10/11 tự resolve
        "explorer": ApplicationInfo("explorer", "File Explorer", "explorer.exe"),
        "chrome": ApplicationInfo("chrome", "Google Chrome", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
        "edge": ApplicationInfo("edge", "Microsoft Edge", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
    }

    def resolve_application(self, app_id: str) -> Optional[ApplicationInfo]:
        return self.ALLOWLIST.get(app_id.lower())

    def open_application(self, app_info: ApplicationInfo) -> bool:
        """Mở ứng dụng an toàn qua subprocess. KHÔNG DÙNG shell=True."""
        try:
            # Popen không block luồng chính
            subprocess.Popen([app_info.executable_path])
            return True
        except Exception:
            return False
            
    def get_allowed_apps(self) -> Dict[str, str]:
        """Trả về danh sách app_id để LLM biết đường gọi."""
        return {app_id: app.name for app_id, app in self.ALLOWLIST.items()}