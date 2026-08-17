import pytest
from unittest.mock import patch, MagicMock
from Tools.core_windows.tools.list_processes_tool import ListProcessesTool
from Tools.core_windows.tools.get_process_tool import GetProcessTool
from Tools.core_windows.models.windows_models import ProcessInfo

@patch("Tools.core_windows.tools.list_processes_tool.WindowsManager")
def test_list_processes_limits_output(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    # Giả lập HĐH trả về 20 tiến trình
    mock_manager.list_processes.return_value = [
        ProcessInfo(pid=i, name=f"proc_{i}.exe") for i in range(20)
    ]
    
    tool = ListProcessesTool()
    # Yêu cầu limit là 5
    res = tool.execute(limit=5)
    
    assert res["success"] is True
    assert res["total_found"] == 20
    assert len(res["processes"]) == 5 # Chỉ được trả về 5
    assert "bị cắt bớt" in res["message"]

@patch("Tools.core_windows.tools.list_processes_tool.WindowsManager")
def test_list_processes_filters_by_name(mock_wm_class):
    mock_manager = mock_wm_class.return_value
    
    # Vì logic filter đã được đẩy xuống WindowsManager/ProcessProvider,
    # Mock Object cần mô phỏng kết quả ĐÃ LỌC để khớp với hành vi thực tế của OS.
    mock_manager.list_processes.return_value = [
        ProcessInfo(pid=1, name="chrome.exe"),
        ProcessInfo(pid=3, name="chrome_crashpad.exe")
    ]
    
    tool = ListProcessesTool()
    res = tool.execute(name_filter="chrome")
    
    assert res["success"] is True
    assert len(res["processes"]) == 2 # Nhận đúng 2 kết quả
    assert res["processes"][0]["name"] == "chrome.exe"
    
    # BẢO VỆ KIẾN TRÚC: Đảm bảo Tool đã uỷ quyền (delegate) tham số name_filter xuống đúng Manager
    mock_manager.list_processes.assert_called_once_with(name_filter="chrome")

@patch("Tools.core_windows.tools.get_process_tool.WindowsManager")
def test_get_process_validates_pid(mock_wm_class):
    tool = GetProcessTool()
    # PID phải là số nguyên > 0
    res = tool.execute(pid=-5)
    assert res["success"] is False
    assert "số nguyên dương" in res["error"]