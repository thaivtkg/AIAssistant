import pytest
from unittest.mock import patch, MagicMock
from Core.agent_runtime import AgentRuntime
from Core.tool_registry import ToolRegistry
from Tools.tool_manager import ToolManager
from Tools.core_windows.tools.open_application_tool import OpenApplicationTool
from Tools.core_windows.tools.list_windows_tool import ListWindowsTool
from Tools.core_windows.tools.focus_window_tool import FocusWindowTool
from Tools.core_windows.models.windows_models import ApplicationInfo, WindowInfo

@patch("Tools.core_windows.tools.focus_window_tool.WindowsManager")
@patch("Tools.core_windows.tools.list_windows_tool.WindowsManager")
@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
def test_agent_runtime_multistep_execution(mock_wm_open, mock_wm_list, mock_wm_focus):
    registry = ToolRegistry()
    registry.register(OpenApplicationTool())
    registry.register(ListWindowsTool())
    registry.register(FocusWindowTool())
    tool_mgr = ToolManager(registry, logger=MagicMock())

    wm_open = mock_wm_open.return_value
    wm_open.get_allowed_apps.return_value = {"notepad": "Notepad"}
    wm_open.resolve_application.return_value = ApplicationInfo("notepad", "Notepad", "notepad.exe")
    wm_open.get_process_pids_by_name.side_effect = [[], [100]] 
    wm_open.open_application.return_value = True
    wm_open.wait_until.return_value = True

    wm_list = mock_wm_list.return_value
    wm_list.list_windows.return_value = [WindowInfo(hwnd=123, title="Untitled - Notepad", pid=100, visible=True, minimized=False)]

    wm_focus = mock_wm_focus.return_value
    wm_focus.focus_window.return_value = True
    wm_focus.wait_until.return_value = True

    engine_mock = MagicMock()
    prompt_mock = MagicMock()
    prompt_mock.build_messages.return_value = [{"role": "system", "content": "mock"}]
    runtime = AgentRuntime(engine_mock, tool_mgr, prompt_mock)
    
    # SỬA LỖI: Nới lỏng giới hạn Loop của Agent để cho phép chạy chuỗi 4 bước
    runtime.max_retries = 5 

    step = 0
    def mock_generate_stream(*args, **kwargs):
        nonlocal step
        if step == 0:
            step += 1
            return (c for c in ["<call>", '{"name": "open_application", "kwargs": {"app_id": "notepad"}}', "</call>"])
        elif step == 1:
            step += 1
            return (c for c in ["<call>", '{"name": "list_windows", "kwargs": {}}', "</call>"])
        elif step == 2:
            step += 1
            return (c for c in ["<call>", '{"name": "focus_window", "kwargs": {"hwnd": 123}}', "</call>"])
        else:
            return (c for c in ["Đã mở, tìm thấy cửa sổ và focus thành công."])

    engine_mock.generate_stream.side_effect = mock_generate_stream

    list(runtime.execute_turn("Mở notepad và focus cửa sổ", []))

    assert engine_mock.generate_stream.call_count == 4
    wm_open.open_application.assert_called_once_with("notepad")
    wm_list.list_windows.assert_called_once()
    wm_focus.focus_window.assert_called_once_with(123)