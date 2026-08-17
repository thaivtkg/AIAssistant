import pytest
from unittest.mock import patch, mock_open
from Tools.core_filesystem.file_write_tool import WriteFileTool

def test_write_file_success_lifecycle():
    tool = WriteFileTool()
    with patch("Tools.core_filesystem.file_write_tool.open", mock_open()) as mocked_file:
        with patch("Tools.core_filesystem.security.FileSecurityManager.is_safe_path", return_value=True):
            with patch("os.path.exists", return_value=True):
                res = tool.execute(path="D:\\fake_test.txt", content="Hello Content")
                
                assert res["success"] is True
                assert res["verification"]["verified"] is True
                # BỔ SUNG: Kiểm tra nội dung có thực sự được ghi
                mocked_file().write.assert_called_once_with("Hello Content")

def test_write_file_silent_failure_caught_by_verify():
    tool = WriteFileTool()
    with patch("Tools.core_filesystem.file_write_tool.open", mock_open()):
        with patch("Tools.core_filesystem.security.FileSecurityManager.is_safe_path", return_value=True):
            # Cố tình giả lập file không tồn tại sau khi _execute
            with patch("os.path.exists", return_value=False):
                res = tool.execute(path="D:\\fake_silent.txt", content="Hi")
                assert res["success"] is False
                assert "chưa được ghi xuống đĩa" in res["error"]

# --- BỔ SUNG ---
def test_write_file_security_reject():
    tool = WriteFileTool()
    # Mock Security chặn
    with patch("Tools.core_filesystem.security.FileSecurityManager.is_safe_path", return_value=False):
        res = tool.execute(path="C:\\Windows\\System32\\fake.txt", content="hack")
        assert res["success"] is False
        assert "Lỗi bảo mật" in res["error"]

def test_write_file_catches_os_exception():
    tool = WriteFileTool()
    # Giả lập lỗi I/O của OS (VD: Permission Denied vật lý)
    with patch("Tools.core_filesystem.file_write_tool.open", side_effect=PermissionError("Access denied")):
        with patch("Tools.core_filesystem.security.FileSecurityManager.is_safe_path", return_value=True):
            res = tool.execute(path="D:\\fake.txt", content="Hi")
            assert res["success"] is False
            assert "Access denied" in res["error"]