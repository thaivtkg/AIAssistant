import win32gui
import win32process
import win32con
from typing import List, Optional
from Tools.core_windows.models.windows_models import WindowInfo

class WindowProvider:
    def list_windows(self) -> List[WindowInfo]:
        windows = []
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title: # Bỏ qua cửa sổ ẩn hoặc không có tên
                return
                
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            placement = win32gui.GetWindowPlacement(hwnd)
            minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            
            windows.append(WindowInfo(
                hwnd=hwnd,
                title=title,
                pid=pid,
                visible=True,
                minimized=minimized
            ))
            
        win32gui.EnumWindows(callback, None)
        return windows

    def get_foreground_window(self) -> Optional[int]:
        hwnd = win32gui.GetForegroundWindow()
        return hwnd if hwnd else None

    def focus_window(self, hwnd: int) -> bool:
        if not win32gui.IsWindow(hwnd):
            return False
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def close_window(self, hwnd: int) -> bool:
        if not win32gui.IsWindow(hwnd):
            return False
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception:
            return False