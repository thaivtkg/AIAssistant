import sys
from typing import List, Optional
from Tools.core_windows.models.windows_models import WindowInfo

class WindowProvider:
    def _win32(self):
        """Lazy import để tránh crash trên môi trường Linux/CI."""
        if sys.platform != "win32":
            raise NotImplementedError("Windows API chỉ hoạt động trên hệ điều hành Windows.")
        import win32gui
        import win32process
        import win32con
        import win32api
        return win32gui, win32process, win32con, win32api

    def is_window_alive(self, hwnd: int) -> bool:
        """Kiểm tra chính xác HWND có tồn tại không (bao gồm cả cửa sổ ẩn/không title)."""
        if sys.platform != "win32": return False
        win32gui, _, _, _ = self._win32()
        return win32gui.IsWindow(hwnd)

    def list_windows(self) -> List[WindowInfo]:
        if sys.platform != "win32": return []
        win32gui, win32process, win32con, _ = self._win32()
        windows = []
        
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            placement = win32gui.GetWindowPlacement(hwnd)
            minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            
            windows.append(WindowInfo(
                hwnd=hwnd, title=title, pid=pid, 
                visible=True, minimized=minimized
            ))
        win32gui.EnumWindows(callback, None)
        return windows

    def get_hwnds_by_pid(self, pid: int) -> List[int]:
        if sys.platform != "win32": return []
        win32gui, win32process, _, _ = self._win32()
        hwnds = []
        def callback(hwnd, extra):
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid:
                hwnds.append(hwnd)
        win32gui.EnumWindows(callback, None)
        return hwnds

    def get_foreground_window(self) -> Optional[int]:
        if sys.platform != "win32": return None
        win32gui, _, _, _ = self._win32()
        hwnd = win32gui.GetForegroundWindow()
        return hwnd if hwnd else None

    def focus_window(self, hwnd: int) -> bool:
        if sys.platform != "win32": return False
        win32gui, win32process, win32con, _ = self._win32()
        if not win32gui.IsWindow(hwnd):
            return False
            
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
            # TRICK: Vượt qua Windows Foreground Lock
            fg = win32gui.GetForegroundWindow()
            if fg:
                cur_tid = win32process.GetWindowThreadProcessId(fg)[0]
                tgt_tid = win32process.GetWindowThreadProcessId(hwnd)[0]
                if cur_tid != tgt_tid:
                    win32process.AttachThreadInput(cur_tid, tgt_tid, True)
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                    finally:
                        win32process.AttachThreadInput(cur_tid, tgt_tid, False)
                else:
                    win32gui.SetForegroundWindow(hwnd)
            else:
                win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def close_window(self, hwnd: int) -> bool:
        if sys.platform != "win32": return False
        win32gui, _, win32con, _ = self._win32()
        if not win32gui.IsWindow(hwnd):
            return False
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception:
            return False