import time
from typing import List, Optional, Callable
from Tools.core_windows.providers.process_provider import ProcessProvider
from Tools.core_windows.providers.application_provider import ApplicationProvider
from Tools.core_windows.providers.window_provider import WindowProvider
from Tools.core_windows.models.windows_models import ProcessInfo, ApplicationInfo, WindowInfo

class WindowsManager:
    def __init__(self):
        self.process = ProcessProvider()
        self.application = ApplicationProvider()
        self.window = WindowProvider()

    def wait_until(self, condition_func: Callable[[], bool], timeout: float = 3.0, interval: float = 0.2) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False

    def list_processes(self, name_filter: str = "") -> List[ProcessInfo]:
        return self.process.list_processes(name_filter)

    def get_process(self, pid: int) -> Optional[ProcessInfo]:
        return self.process.get_process(pid)

    def terminate_process(self, pid: int) -> bool:
        return self.process.terminate_process(pid)

    def close_application_gracefully(self, pid: int) -> bool:
        """Gửi lệnh WM_CLOSE tới tất cả cửa sổ của PID (Không Kill)."""
        hwnds = self.window.get_hwnds_by_pid(pid)
        if not hwnds:
            return False # Không tìm thấy cửa sổ để đóng an toàn
            
        success = False
        for hwnd in hwnds:
            if self.window.close_window(hwnd):
                success = True
        return success

    def resolve_application(self, app_id: str) -> Optional[ApplicationInfo]:
        return self.application.resolve_application(app_id)

    def open_application(self, app_id: str) -> bool:
        app = self.resolve_application(app_id)
        if not app:
            return False
        return self.application.open_application(app)

    def list_windows(self) -> List[WindowInfo]:
        return self.window.list_windows()

    def focus_window(self, hwnd: int) -> bool:
        return self.window.focus_window(hwnd)

    def close_window(self, hwnd: int) -> bool:
        return self.window.close_window(hwnd)
        
    def is_window_foreground(self, hwnd: int) -> bool:
        return self.window.get_foreground_window() == hwnd
    
    def is_window_alive(self, hwnd: int) -> bool:
        return self.window.is_window_alive(hwnd)