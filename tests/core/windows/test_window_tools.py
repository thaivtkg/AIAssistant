import pytest
from unittest.mock import patch, MagicMock
from Tools.core_windows.tools.list_windows_tool import ListWindowsTool
from Tools.core_windows.tools.focus_window_tool import FocusWindowTool
from Tools.core_windows.tools.close_window_tool import CloseWindowTool
from Tools.core_windows.models.windows_models import WindowInfo

@patch("Tools.core_windows.tools.focus_window_tool.WindowsManager")
def test_focus_window_verification_fails_if_blocked(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.focus_window.return_value = True # Gửi lệnh focus thành công
    
    # OS từ chối đẩy cửa sổ lên
    mock_manager.wait_until.return_value = False
    
    tool = FocusWindowTool()
    res = tool.execute(hwnd=12345)
    
    assert res["success"] is False
    assert "Cửa sổ không nổi lên foreground" in res["error"]

@patch("Tools.core_windows.tools.close_window_tool.WindowsManager")
def test_close_window_verification_fails_if_still_open(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    mock_manager.close_window.return_value = True
    
    # OS báo cửa sổ vẫn còn tồn tại (VD: Do bị kẹt popup "Do you want to save?")
    mock_manager.wait_until.return_value = False
    
    tool = CloseWindowTool()
    res = tool.execute(hwnd=9999)
    
    assert res["success"] is False
    # SỬA LỖI: Cập nhật lại text assertion cho khớp với message mới
    assert "vẫn còn tồn tại" in res["error"]