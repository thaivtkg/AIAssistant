import pytest
from unittest.mock import patch, MagicMock
from Core.agent_runtime import AgentRuntime
from Core.tool_registry import ToolRegistry
from Tools.tool_manager import ToolManager
from Tools.core_windows.tools.open_application_tool import OpenApplicationTool
from Tools.core_windows.tools.list_windows_tool import ListWindowsTool
from Tools.core_windows.models.windows_models import ApplicationInfo, WindowInfo

@patch("Tools.core_windows.tools.open_application_tool.WindowsManager")
@patch("Tools.core_windows.tools.list_windows_tool.WindowsManager")
def test_agent_runtime_multistep_execution(mock_wm_list, mock_wm_open):
    """
    Test Integration Đích Thực: AgentRuntime -> ToolManager -> WindowsTools
    Mô phỏng AI gọi 2 tool liên tiếp: Open -> List Windows
    """
    # Setup Mocks
    wm_open = mock_wm_open.return_value
    wm_open.get_allowed_apps.return_value = {"notepad": "Notepad"}
    wm_open.resolve_application.return_value = ApplicationInfo("notepad", "Notepad", "notepad.exe")
    wm_open.get_process_pids_by_name.side_effect = [[], [100]] # Verify pass
    wm_open.open_application.return_value = True
    wm_open.wait_until.return_value = True

    wm_list = mock_wm_list.return_value
    wm_list.list_windows.return_value = [WindowInfo(123, "Notepad", 100, True, False)]

    # Setup Core Architecture
    registry = ToolRegistry()
    registry.register(OpenApplicationTool())
    registry.register(ListWindowsTool())
    tool_mgr = ToolManager(registry, logger=MagicMock())
    engine_mock = MagicMock()
    prompt_mock = MagicMock()
    prompt_mock.build_messages.return_value = [{"role": "system", "content": "mock"}]
    
    runtime = AgentRuntime(engine_mock, tool_mgr, prompt_mock)
    
    # Mô phỏng AI nhả Token Stream qua 3 lượt: Open -> List -> Final Text
    step = 0
    def mock_generate_stream(*args, **kwargs):
        nonlocal step
        if step == 0:
            step += 1
            return (c for c in ["<call>", '{"name": "open_application", "kwargs": {"app_id": "notepad"}}', "</call>"])
        elif step == 1:
            step += 1
            return (c for c in ["<call>", '{"name": "list_windows", "kwargs": {}}', "</call>"])
        else:
            return (c for c in ["Nhiệm vụ hoàn tất."])
            
    engine_mock.generate_stream.side_effect = mock_generate_stream
    
    # Kích hoạt Runtime loop
    responses = list(runtime.execute_turn("Mở notepad rồi lấy danh sách", []))
    
    # Xác minh Engine đã bị chạy 3 lần (Multistep loop thành công)
    assert engine_mock.generate_stream.call_count == 3
    # Xác minh Tool đã được ToolManager thực thi chứ không phải gọi trực tiếp
    wm_open.open_application.assert_called_once_with("notepad")
    wm_list.list_windows.assert_called_once()