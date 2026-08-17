import pytest
from unittest.mock import patch, MagicMock
from Tools.core_windows.tools.open_application_tool import OpenApplicationTool
from Tools.core_windows.tools.close_application_tool import CloseApplicationTool
from Tools.core_windows.models.windows_models import ApplicationInfo, ProcessInfo

@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
def test_open_app_rejects_unlisted_app(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.resolve_application.return_value = None # Trả về rỗng tức là không có trong Allowlist
    
    tool = OpenApplicationTool()
    res = tool.execute(app_id="malware_app")
    
    assert res["success"] is False
    assert "không tồn tại trong Allowlist" in res["error"]

@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
def test_open_app_verification_fails_if_process_not_found(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.resolve_application.return_value = ApplicationInfo("notepad", "Notepad", "notepad.exe")
    mock_manager.open_application.return_value = True
    
    # LỚP HẬU KIỂM: OS báo là app KHÔNG trồi lên sau 5 giây (Giả lập)
    mock_manager.wait_until.return_value = False 
    
    tool = OpenApplicationTool()
    res = tool.execute(app_id="notepad")
    
    # Kết quả tổng quát phải là False dù lệnh mở đã gửi thành công
    assert res["success"] is False
    assert "Verification failed" in res["error"]

@patch("Tools.core_windows.tools.close_application_tool.WindowsManager")
def test_close_app_blocks_system_process(mock_wm_class):
    tool = CloseApplicationTool()
    # svchost.exe nằm trong danh sách cấm
    res = tool.execute(process_name="svchost.exe")
    
    assert res["success"] is False
    assert "Không được phép đóng tiến trình hệ thống" in res["error"]

@patch("Tools.core_windows.tools.close_application_tool.WindowsManager")
def test_close_app_blocks_system_process(mock_wm_class):
    # TIÊM MOCK DATA: Bơm danh sách cấm vào object giả lập để Validate Layer hoạt động
    mock_manager = mock_wm_class.return_value
    mock_manager.process.SYSTEM_PROCESSES = {'svchost.exe', 'explorer.exe'} 

    tool = CloseApplicationTool()
    # svchost.exe nằm trong danh sách cấm
    res = tool.execute(process_name="svchost.exe")
    
    assert res["success"] is False
    assert "Không được phép đóng tiến trình hệ thống" in res["error"]