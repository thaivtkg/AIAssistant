import pytest
from unittest.mock import patch, MagicMock
from Tools.tool_manager import ToolManager
from Core.tool_registry import ToolRegistry
from Tools.core_windows.tools.close_window_tool import CloseWindowTool

def test_tool_manager_rejects_dangerous_windows_tool():
    """Xác minh boundary bảo mật: ToolManager CHẶN công cụ Windows khi bị User Say NO."""
    registry = ToolRegistry()
    registry.register(CloseWindowTool())
    
    manager = ToolManager(registry, logger=MagicMock())
    
    # Mock user nhập 'n' (từ chối)
    with patch("builtins.input", return_value="n"):
        res = manager.execute_tool("close_window", hwnd=12345)
        
    assert res["success"] is False
    assert "từ chối cấp quyền" in res["error"]

@patch("sys.platform", "linux")
def test_window_provider_graceful_on_linux():
    """Xác minh Windows API không làm crash CI trên Linux (Guard OS.name)."""
    from Tools.core_windows.providers.window_provider import WindowProvider
    
    provider = WindowProvider()
    assert provider.list_windows() == []
    assert provider.get_foreground_window() is None
    assert provider.focus_window(123) is False
    assert provider.is_window_alive(123) is False

@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
@patch("Tools.core_windows.tools.list_windows_tool.WindowsManager")
@patch("Tools.core_windows.tools.focus_window_tool.WindowsManager")
def test_agent_multistep_mock(mock_wm_focus, mock_wm_list, mock_wm_open):
    """Mô phỏng chuỗi: Open -> List -> Focus thành công."""
    from Tools.core_windows.tools.open_application_tool import OpenApplicationTool
    from Tools.core_windows.tools.list_windows_tool import ListWindowsTool
    from Tools.core_windows.tools.focus_window_tool import FocusWindowTool
    from Tools.core_windows.models.windows_models import ApplicationInfo, WindowInfo
    
    # Bước 1: Open
    wm_open = mock_wm_open.return_value
    wm_open.resolve_application.return_value = ApplicationInfo("notepad", "Notepad", "notepad.exe")
    wm_open.process.get_pids_by_name.side_effect = [[], [100]] # Verification: Thấy PID mới
    wm_open.open_application.return_value = True
    wm_open.wait_until.return_value = True
    
    res_open = OpenApplicationTool().execute(app_id="notepad")
    assert res_open["success"] is True
    
    # Bước 2: List Windows
    wm_list = mock_wm_list.return_value
    wm_list.list_windows.return_value = [WindowInfo(hwnd=555, title="Untitled - Notepad", pid=100, visible=True, minimized=False)]
    
    res_list = ListWindowsTool().execute(title_filter="notepad")
    assert res_list["success"] is True
    assert res_list["windows"][0]["hwnd"] == 555
    
    # Bước 3: Focus
    wm_focus = mock_wm_focus.return_value
    wm_focus.focus_window.return_value = True
    wm_focus.wait_until.return_value = True # Verification thành công
    
    res_focus = FocusWindowTool().execute(hwnd=555)
    assert res_focus["success"] is True
    assert res_focus["verification"]["verified"] is True