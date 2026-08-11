import pytest
from Core.base_tool import BaseTool

class MockPassTool(BaseTool):
    def __init__(self):
        super().__init__("mock_pass", "Test")
    def _validate(self, **kwargs):
        return {"valid": True}
    def _execute(self, **kwargs):
        return {"success": True, "data": "ok"}
    def verify(self, **kwargs):
        return {"verified": True}

class MockValidateFailTool(BaseTool):
    def __init__(self):
        super().__init__("mock_val_fail", "Test")
    def _validate(self, **kwargs):
        return {"valid": False, "error": "Invalid param"}
    def _execute(self, **kwargs):
        return {"success": True}

class MockExecuteFailTool(BaseTool):
    def __init__(self):
        super().__init__("mock_exec_fail", "Test")
    def _execute(self, **kwargs):
        return {"success": False, "error": "Exec error"}

class MockVerifyFailTool(BaseTool):
    def __init__(self):
        super().__init__("mock_ver_fail", "Test")
    def _execute(self, **kwargs):
        return {"success": True}
    def verify(self, **kwargs):
        return {"verified": False, "message": "Verify failed"}

class MockVerifyExceptionTool(BaseTool):
    def __init__(self):
        super().__init__("mock_ver_exc", "Test")
    def _execute(self, **kwargs):
        return {"success": True}
    def verify(self, **kwargs):
        raise ValueError("Crash during verify")


def test_lifecycle_success():
    tool = MockPassTool()
    res = tool.execute()
    assert res["success"] is True
    assert res["verification"]["verified"] is True

def test_validate_fail_stops_execution():
    tool = MockValidateFailTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Invalid param" in res["error"]

def test_execute_fail_stops_verify():
    tool = MockExecuteFailTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Exec error" in res["error"]
    assert "verification" not in res # Verify chưa từng được chạy

def test_verify_fail_flips_success_flag():
    tool = MockVerifyFailTool()
    res = tool.execute()
    assert res["success"] is False # Bị lật ngược dù _execute thành công
    assert "Verify failed" in res["error"]

def test_verify_exception_flips_success_flag():
    tool = MockVerifyExceptionTool()
    res = tool.execute()
    assert res["success"] is False
    assert "Crash during verify" in res["error"]