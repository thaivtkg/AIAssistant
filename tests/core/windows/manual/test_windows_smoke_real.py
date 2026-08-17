import pytest
import sys
from Tools.core_windows.windows_manager import WindowsManager

@pytest.mark.windows_real
@pytest.mark.skipif(sys.platform != "win32", reason="Chỉ chạy trên Windows OS thật.")
def test_real_notepad_lifecycle():
    """
    KIỂM THỬ VẬT LÝ: Mở Notepad -> Focus -> Đóng an toàn.
    Test này tương tác với OS thực. Chạy bằng: pytest -m windows_real
    """
    manager = WindowsManager()
    
    # 1. Open
    assert manager.open_application("notepad") is True
    
    # Verify bằng cách đợi PID xuất hiện
    def notepad_launched():
        return len(manager.get_process_pids_by_name("notepad.exe")) > 0
    assert manager.wait_until(notepad_launched, timeout=5.0) is True
    
    pids = manager.get_process_pids_by_name("notepad.exe")
    target_pid = pids[-1] # Lấy PID mới nhất
    
    # 2. Get Window
    hwnds = manager.window.get_hwnds_by_pid(target_pid)
    assert len(hwnds) > 0
    target_hwnd = hwnds[0]
    
    # 3. Focus
    assert manager.focus_window(target_hwnd) is True
    
    # 4. Graceful Close
    assert manager.close_application_gracefully(target_pid) is True
    
    # Verify đóng thành công
    def notepad_closed():
        try:
            manager.get_process(target_pid)
            return False
        except ProcessLookupError:
            return True
    assert manager.wait_until(notepad_closed, timeout=3.0) is True