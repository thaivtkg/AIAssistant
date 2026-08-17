import pytest
import sys
import os
from Tools.core_windows.windows_manager import WindowsManager
from Tools.core_windows.models.windows_models import ApplicationInfo

@pytest.mark.windows_real
@pytest.mark.skipif(sys.platform != "win32", reason="Chỉ chạy trên Windows OS thật.")
def test_real_win32_app_lifecycle():
    """
    KIỂM THỬ VẬT LÝ: Mở Character Map -> Tìm đúng PID có HWND -> Focus -> Đóng an toàn.
    """
    manager = WindowsManager()
    windir = os.environ.get("WINDIR", r"C:\Windows")
    charmap_exe = os.path.normpath(os.path.join(windir, "System32", "charmap.exe"))
    
    # LƯU STATE: Sao lưu cấu hình hiện tại để dọn dẹp, tránh làm bẩn Global State
    original_charmap = manager.application.ALLOWLIST.get("charmap")
    
    try:
        manager.application.ALLOWLIST["charmap"] = ApplicationInfo(
            "charmap", "Character Map", charmap_exe
        )
        
        before_pids = set(manager.get_process_pids_by_name("charmap.exe"))
        
        # 1. Open
        assert manager.open_application("charmap") is True
        
        def app_launched():
            current = set(manager.get_process_pids_by_name("charmap.exe"))
            return bool(current - before_pids)
            
        assert manager.wait_until(app_launched, timeout=5.0) is True
        
        after_pids = set(manager.get_process_pids_by_name("charmap.exe"))
        new_pids = after_pids - before_pids
        assert new_pids
        
        # 2. Get Window (MEDIUM FIX: Duyệt toàn bộ PID mới để tìm PID giữ HWND)
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
        
        # 3. Focus (Dùng target_hwnd đã tìm được)
        assert manager.focus_window(target_hwnd) is True
        
        # 4. Graceful Close (Dùng target_pid đã tìm được)
        assert manager.close_application_gracefully(target_pid) is True
        
        def app_closed():
            try:
                manager.get_process(target_pid)
                return False
            except ProcessLookupError:
                return True
            except PermissionError:
                return False
                
        assert manager.wait_until(app_closed, timeout=3.0) is True

    finally:
        # LOW FIX: Dọn dẹp môi trường (Global Mutable State)
        if original_charmap is None:
            manager.application.ALLOWLIST.pop("charmap", None)
        else:
            manager.application.ALLOWLIST["charmap"] = original_charmap