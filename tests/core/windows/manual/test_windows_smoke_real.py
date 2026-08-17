import pytest
import sys
from Tools.core_windows.windows_manager import WindowsManager

@pytest.mark.windows_real
@pytest.mark.skipif(sys.platform != "win32", reason="Chỉ chạy trên Windows OS thật.")
def test_real_notepad_lifecycle():
    manager = WindowsManager()
    
    before_pids = set(manager.get_process_pids_by_name("notepad.exe"))
    
    # 1. Open
    assert manager.open_application("notepad") is True
    
    def notepad_launched():
        current = set(manager.get_process_pids_by_name("notepad.exe"))
        return bool(current - before_pids)
        
    assert manager.wait_until(notepad_launched, timeout=5.0) is True
    
    after_pids = set(manager.get_process_pids_by_name("notepad.exe"))
    new_pids = list(after_pids - before_pids)
    assert len(new_pids) > 0
    
    # SỬA LỖI: Duyệt qua tất cả các PID mới sinh ra (Launcher + UI Host).
    # Chỉ chọn PID nào thực sự được HĐH cấp phát Window Handle (Giao diện).
    target_pid = None
    target_hwnd = None
    
    def hwnd_created():
        nonlocal target_pid, target_hwnd
        for pid in new_pids:
            hwnds = manager.window.get_hwnds_by_pid(pid)
            if hwnds:
                target_pid = pid
                target_hwnd = hwnds[0]
                return True
        return False
        
    assert manager.wait_until(hwnd_created, timeout=5.0) is True
    assert target_pid is not None
    assert target_hwnd is not None
    
    # 2. Focus
    assert manager.focus_window(target_hwnd) is True
    
    # 3. Graceful Close
    assert manager.close_application_gracefully(target_pid) is True
    
    def notepad_closed():
        try:
            manager.get_process(target_pid)
            return False
        except ProcessLookupError:
            return True
            
    assert manager.wait_until(notepad_closed, timeout=3.0) is True