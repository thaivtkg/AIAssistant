import pytest
from Core.base_tool import BaseTool

class MockPassTool(BaseTool):
    def __init__(self):
        super().__init__("mock_pass", "Test")
    def get_schema(self): return {}
    def _validate(self, **kwargs): return {"valid": True}
    def _execute(self, **kwargs): return {"success": True, "data": "ok"}
    def verify(self, **kwargs): return {"verified": True, "message": "Verified"}

class MockValidateFailTool(BaseTool):
    def __init__(self):
        super().__init__("mock_val_fail", "Test")
    def get_schema(self): return {}
    def _validate(self, **kwargs): return {"valid": False, "error": "Invalid param"}
    def _execute(self, **kwargs): return {"success": True}

class MockExecuteFailTool(BaseTool):
    def __init__(self):
        super().__init__("mock_exec_fail", "Test")
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": False, "error": "Exec error"}

class MockVerifyFailTool(BaseTool):
    def __init__(self):
        super().__init__("mock_ver_fail", "Test")
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True}
    def verify(self, **kwargs): return {"verified": False, "message": "Verify failed"}

# --- BỔ SUNG EXCEPTION TESTS ---
class MockValidateExceptionTool(BaseTool):
    def __init__(self): super().__init__("mock_val_exc", "Test")
    def get_schema(self): return {}
    def _validate(self, **kwargs): raise ValueError("Validate crashed")
    def _execute(self, **kwargs): return {"success": True}

class MockExecuteExceptionTool(BaseTool):
    def __init__(self): super().__init__("mock_exe_exc", "Test")
    def get_schema(self): return {}
    def _execute(self, **kwargs): raise RuntimeError("Execute crashed")

class MockVerifyExceptionTool(BaseTool):
    def __init__(self): super().__init__("mock_ver_exc", "Test")
    def get_schema(self): return {}
    def _execute(self, **kwargs): return {"success": True}
    def verify(self, **kwargs): raise TypeError("Verify crashed")


def test_base_tool_lifecycle_success():
    tool = MockPassTool()
    res = tool.execute()
    assert res["success"] is True
    assert res["verification"]["verified"] is True

def test_base_tool_validate_fail_stops_execution():
    tool = MockValidateFailTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Invalid param" in res["error"]
    assert "verification" not in res

def test_base_tool_execute_fail_stops_verify():
    tool = MockExecuteFailTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Exec error" in res["error"]
    assert "verification" not in res

def test_base_tool_verify_fail_flips_success_flag():
    tool = MockVerifyFailTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Verify failed" in res["error"]

# --- BỔ SUNG ASSERTIONS CHO EXCEPTION RECOVERY ---
def test_base_tool_catches_validate_exception():
    tool = MockValidateExceptionTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Validate crashed" in res["error"]

def test_base_tool_catches_execute_exception():
    tool = MockExecuteExceptionTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Execution exception: Execute crashed" in res["error"]

def test_base_tool_catches_verify_exception():
    tool = MockVerifyExceptionTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Verification exception: Verify crashed" in res["error"]