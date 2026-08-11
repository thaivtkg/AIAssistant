import pytest
from Core.base_tool import BaseTool

class DummyPassTool(BaseTool):
    def __init__(self):
        super().__init__("dummy_pass", "Test pass tool")
    def _execute(self, **kwargs):
        return {"success": True, "data": "ok"}
    def verify(self, **kwargs):
        return {"verified": True}

class DummyBypassTool(BaseTool):
    def __init__(self):
        super().__init__("dummy_bypass", "Tool that tries to bypass")
    # Cố tình ghi đè execute để test
    def execute(self, **kwargs):
        return {"success": True, "bypassed": True}

class DummyFailVerifyTool(BaseTool):
    def __init__(self):
        super().__init__("dummy_fail", "Test fail verify")
    def _execute(self, **kwargs):
        return {"success": True}
    def verify(self, **kwargs):
        return {"verified": False, "message": "Mock verification failed"}

def test_base_tool_lifecycle_success():
    tool = DummyPassTool()
    result = tool.execute()
    assert result["success"] is True
    assert "verification" in result

def test_base_tool_verification_failure_flips_success_flag():
    tool = DummyFailVerifyTool()
    result = tool.execute()
    # Execute trả True, nhưng verify trả False -> success tổng phải là False
    assert result["success"] is False
    assert "Verification failed" in result["error"]