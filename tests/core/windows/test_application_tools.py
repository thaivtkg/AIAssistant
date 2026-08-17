import pytest
from unittest.mock import patch, MagicMock
from Tools.core_windows.tools.open_application_tool import OpenApplicationTool
from Tools.core_windows.tools.close_application_tool import CloseApplicationTool
from Tools.core_windows.models.windows_models import ApplicationInfo, ProcessInfo

@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
def test_open_app_rejects_unlisted_app(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.resolve_application.return_value = None
    
    tool = OpenApplicationTool()
    res = tool.execute(app_id="malware")
    assert res["success"] is False
    assert "không tồn tại trong Allowlist" in res["error"]

@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
def test_open_app_verification_fails_no_new_pid(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.resolve_application.return_value = ApplicationInfo("notepad", "Notepad", "notepad.exe")
    mock_manager.open_application.return_value = True
    
    # GIẢ LẬP: Trước và sau khi gọi open, hàm get_pids_by_name đều trả về tập hợp cũ (Không sinh PID mới)
    mock_manager.process.get_pids_by_name.return_value = [1000]
    mock_manager.wait_until.return_value = False
    
    tool = OpenApplicationTool()
    res = tool.execute(app_id="notepad")
    
    assert res["success"] is False
    assert "Verification failed" in res["error"]

@patch("Tools.core_windows.tools.close_application_tool.WindowsManager")
def test_close_app_blocks_system_process_default_policy(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.get_process.return_value = ProcessInfo(pid=1, name="svchost.exe")
    mock_manager.is_system_process.return_value = True

    tool = CloseApplicationTool()
    res = tool.execute(pid=1)
    
    assert res["success"] is False
    assert "Không được phép đóng hệ thống" in res["error"]

@patch("Tools.core_windows.tools.close_application_tool.WindowsManager")
def test_close_app_graceful_success(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    # Mock trả về ProcessInfo cho cả Validate và Execute (Race re-check)
    mock_manager.get_process.return_value = ProcessInfo(pid=100, name="notepad.exe", exe=r"C:\Windows\System32\notepad.exe")
    mock_manager.is_system_process.return_value = False
    mock_manager.is_allowed_application_process.return_value = True
    
    mock_manager.close_application_gracefully.return_value = True
    mock_manager.wait_until.return_value = True
    
    tool = CloseApplicationTool()
    res = tool.execute(pid=100)
    
    assert res["success"] is True
    mock_manager.close_application_gracefully.assert_called_once_with(100)

@patch("Tools.core_windows.tools.close_application_tool.WindowsManager")
def test_close_app_blocks_fake_executable_path(mock_wm_class):
    """Test bảo mật P0: Chặn Fake Binary cùng tên."""
    mock_manager = mock_wm_class.return_value
    mock_manager.get_process.return_value = ProcessInfo(pid=99, name="notepad.exe", exe=r"C:\Temp\notepad.exe")
    mock_manager.is_system_process.return_value = False
    
    # Manager nhận ra đường dẫn C:\Temp là fake
    mock_manager.is_allowed_application_process.return_value = False
    
    tool = CloseApplicationTool()
    res = tool.execute(pid=99)
    
    assert res["success"] is False
    assert "không thuộc Allowlist hoặc chạy từ đường dẫn giả mạo" in res["error"]