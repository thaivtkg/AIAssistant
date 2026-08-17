import pytest
import json
from unittest.mock import MagicMock, patch
from Core.agent_runtime import AgentRuntime

@pytest.fixture
def runtime_setup():
    engine_mock = MagicMock()
    tool_mgr_mock = MagicMock()
    prompt_mgr_mock = MagicMock()
    prompt_mgr_mock.build_messages.return_value = [{"role": "system", "content": "mock"}]
    
    runtime = AgentRuntime(engine_mock, tool_mgr_mock, prompt_mgr_mock)
    runtime.max_retries = 3
    return runtime, engine_mock, tool_mgr_mock

def test_runtime_valid_tool_call(runtime_setup):
    runtime, engine, tm = runtime_setup
    
    # Engine trả về 1 chuỗi chứa tool call chuẩn
    engine.generate_stream.return_value = (chunk for chunk in ["<call>", '{"name": "test_tool", "kwargs": {"a": 1}}', "</call>"])
    tm.has_tool.return_value = True
    tm.execute_tool.return_value = {"success": True, "data": "mocked"}
    
    # execute_turn là generator, ép chạy bằng list()
    list(runtime.execute_turn("hello", []))
    
    # Tool phải được execute chính xác
    tm.execute_tool.assert_called_once_with("test_tool", a=1)

def test_runtime_recovers_malformed_json(runtime_setup):
    runtime, engine, tm = runtime_setup
    
    # Lần 1: JSON hỏng. Lần 2: LLM sinh chữ bình thường (để thoát loop)
    def engine_side_effect(*args, **kwargs):
        if engine.generate_stream.call_count == 1:
            return (c for c in ["<call>", "{ broken json", "</call>"])
        return (c for c in ["Okay done."])
    engine.generate_stream.side_effect = engine_side_effect
    
    list(runtime.execute_turn("hello", []))
    
    # Loop chạy 2 lần (1 lỗi, 1 thành công text)
    assert engine.generate_stream.call_count == 2
    tm.execute_tool.assert_not_called()

def test_runtime_recovers_hallucinated_tool(runtime_setup):
    runtime, engine, tm = runtime_setup
    
    def engine_side_effect(*args, **kwargs):
        if engine.generate_stream.call_count == 1:
            return (c for c in ["<call>", '{"name": "fake_tool", "kwargs": {}}', "</call>"])
        return (c for c in ["Okay done."])
    engine.generate_stream.side_effect = engine_side_effect
    
    # Báo fake_tool không tồn tại
    tm.has_tool.return_value = False 
    
    list(runtime.execute_turn("hello", []))
    
    assert engine.generate_stream.call_count == 2
    tm.execute_tool.assert_not_called()

def test_runtime_recovers_raw_json_without_call_tags(runtime_setup):
    runtime, engine, tm = runtime_setup
    
    def engine_side_effect(*args, **kwargs):
        if engine.generate_stream.call_count == 1:
            # Sinh JSON có name và kwargs nhưng KHÔNG có <call>
            return (c for c in ['{"name": "test_tool", \n', '"kwargs": {}}'])
        return (c for c in ["Okay done."])
    engine.generate_stream.side_effect = engine_side_effect
    
    list(runtime.execute_turn("hello", []))
    
    # Runtime phải bắt được bằng regex và ép retry
    assert engine.generate_stream.call_count == 2
    tm.execute_tool.assert_not_called()

def test_runtime_max_retries_termination(runtime_setup):
    runtime, engine, tm = runtime_setup
    runtime.max_retries = 2
    
    # Engine CỐ TÌNH sinh lỗi liên tục
    engine.generate_stream.return_value = (c for c in ["<call>", "{ broken", "</call>"])
    
    list(runtime.execute_turn("hello", []))
    
    # Phải kết thúc sau đúng 2 lần, không lặp vô hạn
    assert engine.generate_stream.call_count == 2